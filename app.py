"""
Predictive Sales Forecasting and Business Analytics System
Flask Web Application Entry Point
"""

import os
import tempfile
if 'MPLCONFIGDIR' not in os.environ:
    os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import io
import csv
from flask import (
    Flask, render_template, request, redirect, url_for, flash, 
    send_file, jsonify, Response
)
import pandas as pd

from src.data_loader import (
    get_active_data, set_active_data, get_data_summary, 
    reset_to_sample_data, switch_to_mysql_data, sync_active_to_mysql,
    get_active_source_info, DEFAULT_SAMPLE_PATH
)
from src.validation import validate_sales_data
from src.preprocessing import (
    aggregate_sales, get_product_analytics, get_category_analytics, 
    get_region_analytics, get_summary_stats, generate_sales_trend_chart,
    generate_product_bar_chart, generate_category_chart
)
from src.forecasting import (
    forecast_moving_average, forecast_linear_regression,
    generate_future_dates, generate_forecast_chart
)
from src.evaluation import evaluate_models
from src.database import check_db_status, init_db, save_forecast_to_db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sales-forecast-secret-key-cse2024')

# In-memory storage for latest generated forecast to share across Dashboard, Forecasting, and Reports
LATEST_FORECAST_CACHE = None


@app.context_processor
def inject_global_status():
    """Injects database status and source info into all rendered templates."""
    status = check_db_status()
    source_info = get_active_source_info()
    return dict(db_status=status, active_source_info=source_info)


# -------------------------------------------------------------------------
# Page 1: Dashboard
# -------------------------------------------------------------------------
@app.route('/')
@app.route('/dashboard')
def index():
    df = get_active_data()
    summary = get_data_summary(df)

    # Generate historical trend chart for dashboard
    df_daily = aggregate_sales(df, freq='D')
    chart_url = generate_sales_trend_chart(df_daily, title="Daily Sales Revenue Velocity") if not df_daily.empty else ""

    return render_template(
        'index.html',
        active_page='dashboard',
        summary=summary,
        chart_url=chart_url,
        latest_forecast=LATEST_FORECAST_CACHE
    )


# -------------------------------------------------------------------------
# Page 2: Upload Sales Data
# -------------------------------------------------------------------------
@app.route('/upload')
def upload_page():
    df = get_active_data()
    summary = get_data_summary(df)
    preview_rows = df.head(15).to_dict(orient='records') if not df.empty else []

    return render_template(
        'upload.html',
        active_page='upload',
        summary=summary,
        preview_rows=preview_rows
    )


@app.route('/upload-file', methods=['POST'])
def upload_file_route():
    if 'file' not in request.files:
        flash("No file part provided in upload form.", "danger")
        return redirect(url_for('upload_page'))

    file = request.files['file']
    if file.filename == '':
        flash("Please select a valid CSV file to upload.", "warning")
        return redirect(url_for('upload_page'))

    if not file.filename.lower().endswith('.csv'):
        flash("Invalid file format. Only CSV (.csv) files are supported.", "danger")
        return redirect(url_for('upload_page'))

    try:
        df_uploaded = pd.read_csv(file)
        is_valid, cleaned_df, errors, warnings = validate_sales_data(df_uploaded)

        if not is_valid:
            for err in errors:
                flash(f"Validation Error: {err}", "danger")
            return redirect(url_for('upload_page'))

        for warn in warnings:
            flash(f"Notice: {warn}", "warning")

        # Save as active dataset
        set_active_data(cleaned_df, source_name=f"Uploaded CSV ({file.filename})", source_type="csv")
        flash(f"Successfully validated and loaded {len(cleaned_df)} sales records from '{file.filename}'.", "success")
        return redirect(url_for('upload_page'))

    except Exception as e:
        flash(f"Failed to process CSV file: {str(e)}", "danger")
        return redirect(url_for('upload_page'))


@app.route('/download-sample')
def download_sample_csv():
    if os.path.exists(DEFAULT_SAMPLE_PATH):
        with open(DEFAULT_SAMPLE_PATH, 'rb') as f:
            data = f.read()
        return Response(
            data,
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment;filename=sample_sales.csv"}
        )
    flash("Sample dataset not found.", "warning")
    return redirect(url_for('upload_page'))


@app.route('/reset-data', methods=['POST'])
def reset_data_route():
    success, msg = reset_to_sample_data()
    flash(msg, "success" if success else "danger")
    return redirect(url_for('upload_page'))


# -------------------------------------------------------------------------
# Page 3: Business Analytics
# -------------------------------------------------------------------------
@app.route('/analytics')
def analytics_page():
    freq = request.args.get('freq', 'D').upper()
    if freq not in ['D', 'M']:
        freq = 'D'

    df = get_active_data()
    if df.empty:
        flash("No sales data available. Please upload a dataset first.", "warning")
        return redirect(url_for('upload_page'))

    df_agg = aggregate_sales(df, freq=freq)
    stats = get_summary_stats(df_agg['revenue']) if not df_agg.empty else {}

    trend_title = "Monthly Revenue Trend" if freq == 'M' else "Daily Revenue Velocity"
    trend_chart = generate_sales_trend_chart(df_agg, title=trend_title) if not df_agg.empty else ""

    df_prods = get_product_analytics(df, top_n=10)
    product_chart = generate_product_bar_chart(df_prods, top_n=8) if not df_prods.empty else ""
    product_rows = df_prods.to_dict(orient='records') if not df_prods.empty else []

    df_cats = get_category_analytics(df)
    category_chart = generate_category_chart(df_cats) if not df_cats.empty else ""
    category_rows = df_cats.to_dict(orient='records') if not df_cats.empty else []

    df_regions = get_region_analytics(df)
    region_rows = df_regions.to_dict(orient='records') if not df_regions.empty else []

    return render_template(
        'analytics.html',
        active_page='analytics',
        freq=freq,
        df_agg=df_agg,
        stats=stats,
        trend_chart=trend_chart,
        product_chart=product_chart,
        category_chart=category_chart,
        product_rows=product_rows,
        category_rows=category_rows,
        region_rows=region_rows
    )


# -------------------------------------------------------------------------
# Page 4: Sales Forecasting
# -------------------------------------------------------------------------
@app.route('/forecasting')
def forecasting_page():
    return run_forecast_pipeline(method='both', freq='D', horizon=14, window=7)


@app.route('/generate-forecast', methods=['POST'])
def generate_forecast_route():
    method = request.form.get('method', 'both')
    freq = request.form.get('freq', 'D').upper()
    try:
        horizon = int(request.form.get('horizon', 14))
        window = int(request.form.get('window', 7))
    except ValueError:
        horizon, window = 14, 7

    return run_forecast_pipeline(method=method, freq=freq, horizon=horizon, window=window)


def run_forecast_pipeline(method='both', freq='D', horizon=14, window=7):
    global LATEST_FORECAST_CACHE
    df = get_active_data()
    if df.empty:
        flash("No sales data available to forecast. Please upload a dataset first.", "warning")
        return redirect(url_for('upload_page'))

    df_agg = aggregate_sales(df, freq=freq)
    if len(df_agg) < window:
        flash(f"Insufficient history: aggregated dataset has {len(df_agg)} intervals, but window size is {window}. Please select a smaller window.", "danger")
        window = max(2, len(df_agg) - 1)

    ma_res = None
    lr_res = None

    try:
        if method in ['ma', 'both']:
            ma_res = forecast_moving_average(df_agg['revenue'], window=window, horizon=horizon)

        if method in ['linear_regression', 'both']:
            lr_res = forecast_linear_regression(df_agg['revenue'], horizon=horizon)

        # Generate future dates
        last_date = df_agg['date'].iloc[-1]
        future_dates = generate_future_dates(last_date, horizon=horizon, freq=freq)

        # Generate visual forecast plot
        forecast_chart = generate_forecast_chart(
            df_agg=df_agg,
            ma_res=ma_res,
            lr_res=lr_res,
            future_dates=future_dates,
            freq=freq
        )

        # Assemble forecast data rows
        forecast_table = []
        for i in range(horizon):
            row_dict = {
                'date': future_dates[i],
                'ma_pred': ma_res['forecast_values'][i] if ma_res else None,
                'lr_pred': lr_res['forecast_values'][i] if lr_res else None
            }
            # Primary reference value for range calculation
            if lr_res:
                row_dict['primary_val'] = lr_res['forecast_values'][i]
            else:
                row_dict['primary_val'] = ma_res['forecast_values'][i]
            forecast_table.append(row_dict)

        primary_preds = lr_res['forecast_values'] if lr_res else ma_res['forecast_values']
        total_projected = sum(primary_preds)
        avg_projected = total_projected / horizon if horizon > 0 else 0.0

        # Update global cache for dashboard and reports
        LATEST_FORECAST_CACHE = {
            'method': "Linear Regression & MA" if method == 'both' else ("Moving Average" if method == 'ma' else "Linear Regression"),
            'horizon': horizon,
            'freq': 'Monthly' if freq == 'M' else 'Daily',
            'window': window,
            'total_projected': total_projected,
            'avg_projected': avg_projected,
            'forecast_table': forecast_table,
            'preview_rows': [{'period': r['date'], 'value': r['primary_val']} for r in forecast_table[:5]],
            'chart_b64': forecast_chart,
            'lr_res': lr_res,
            'ma_res': ma_res
        }

        return render_template(
            'forecasting.html',
            active_page='forecasting',
            method=method,
            freq=freq,
            horizon=horizon,
            window=window,
            forecast_chart=forecast_chart,
            forecast_table=forecast_table,
            total_projected=total_projected,
            avg_projected=avg_projected,
            ma_res=ma_res,
            lr_res=lr_res
        )

    except Exception as e:
        flash(f"Forecasting error: {str(e)}", "danger")
        return redirect(url_for('analytics_page'))


@app.route('/save-forecasts-mysql', methods=['POST'])
def save_forecasts_to_mysql_route():
    global LATEST_FORECAST_CACHE
    if not LATEST_FORECAST_CACHE or not LATEST_FORECAST_CACHE.get('forecast_table'):
        flash("No forecast predictions found to save.", "warning")
        return redirect(url_for('forecasting_page'))

    method = LATEST_FORECAST_CACHE.get('method', 'Forecast Model')
    table = LATEST_FORECAST_CACHE.get('forecast_table', [])
    saved_count = 0

    for row in table:
        val = row.get('primary_val', 0.0)
        success = save_forecast_to_db(period=row['date'], method=method, predicted_value=val)
        if success:
            saved_count += 1

    if saved_count > 0:
        flash(f"Successfully saved {saved_count} forecast prediction records into MySQL 'forecasts' table.", "success")
    else:
        flash("Could not save to MySQL. Please check if MySQL database is initialized.", "danger")

    return redirect(url_for('forecasting_page'))


@app.route('/download-forecast-csv')
def download_forecast_csv():
    global LATEST_FORECAST_CACHE
    if not LATEST_FORECAST_CACHE or not LATEST_FORECAST_CACHE.get('forecast_table'):
        flash("No forecast data generated yet to download.", "warning")
        return redirect(url_for('forecasting_page'))

    table = LATEST_FORECAST_CACHE['forecast_table']
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Period_Date', 'Moving_Average_Prediction', 'Linear_Regression_Prediction', 'Estimated_Lower_Bound', 'Estimated_Upper_Bound'])

    for row in table:
        writer.writerow([
            row['date'],
            row.get('ma_pred', ''),
            row.get('lr_pred', ''),
            round(row['primary_val'] * 0.9, 2),
            round(row['primary_val'] * 1.1, 2)
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=sales_forecast_predictions.csv"}
    )


# -------------------------------------------------------------------------
# Page 5: Forecast Evaluation
# -------------------------------------------------------------------------
@app.route('/evaluation', methods=['GET', 'POST'])
def evaluation_page():
    train_ratio = 0.8
    window = 7
    freq = 'D'

    if request.method == 'POST':
        try:
            train_ratio = float(request.form.get('train_ratio', 0.8))
            window = int(request.form.get('window', 7))
            freq = request.form.get('freq', 'D').upper()
        except ValueError:
            pass

    df = get_active_data()
    if df.empty:
        flash("No dataset loaded for evaluation. Please upload sales data first.", "warning")
        return redirect(url_for('upload_page'))

    df_agg = aggregate_sales(df, freq=freq)
    eval_res = evaluate_models(df_agg=df_agg, train_ratio=train_ratio, window=window)

    return render_template(
        'evaluation.html',
        active_page='evaluation',
        train_ratio=train_ratio,
        window=window,
        freq=freq,
        eval_res=eval_res
    )


# -------------------------------------------------------------------------
# Page 6: Reports
# -------------------------------------------------------------------------
@app.route('/reports')
def reports_page():
    global LATEST_FORECAST_CACHE
    df = get_active_data()
    summary = get_data_summary(df)

    # Ensure evaluation results exist for reports
    df_agg = aggregate_sales(df, freq='D')
    eval_res = evaluate_models(df_agg=df_agg, train_ratio=0.8, window=7)

    # If forecast hasn't run yet, run default forecast pipeline silently to populate report
    if not LATEST_FORECAST_CACHE:
        run_forecast_pipeline(method='both', freq='D', horizon=14, window=7)

    forecast_chart = LATEST_FORECAST_CACHE.get('chart_b64', '') if LATEST_FORECAST_CACHE else ''
    forecast_table = LATEST_FORECAST_CACHE.get('forecast_table', []) if LATEST_FORECAST_CACHE else []
    horizon = LATEST_FORECAST_CACHE.get('horizon', 14) if LATEST_FORECAST_CACHE else 14
    ma_res = LATEST_FORECAST_CACHE.get('ma_res') if LATEST_FORECAST_CACHE else None
    lr_res = LATEST_FORECAST_CACHE.get('lr_res') if LATEST_FORECAST_CACHE else None

    return render_template(
        'reports.html',
        active_page='reports',
        summary=summary,
        eval_res=eval_res,
        forecast_chart=forecast_chart,
        forecast_table=forecast_table,
        horizon=horizon,
        ma_res=ma_res,
        lr_res=lr_res
    )


# -------------------------------------------------------------------------
# Database Operations Routes (MySQL)
# -------------------------------------------------------------------------
@app.route('/init-mysql', methods=['POST'])
def init_mysql_route():
    success, msg = init_db()
    flash(msg, "success" if success else "danger")
    return redirect(url_for('index'))


@app.route('/sync-mysql', methods=['POST'])
def sync_to_mysql_route():
    success, count, msg = sync_active_to_mysql()
    flash(msg, "success" if success else "danger")
    return redirect(url_for('index'))


@app.route('/load-mysql', methods=['POST'])
def load_from_mysql_route():
    success, msg = switch_to_mysql_data()
    flash(msg, "success" if success else "danger")
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Initialize default data
    from src.data_loader import load_initial_data
    load_initial_data()
    print("==================================================================")
    print("🚀 Predictive Sales Forecasting & Business Analytics System")
    print("🌐 Running on http://127.0.0.1:5000")
    print("📂 Data mode: Dual Engine (CSV Out-of-the-box & MySQL Ready)")
    print("==================================================================")
    app.run(host='127.0.0.1', port=5000, debug=True)
