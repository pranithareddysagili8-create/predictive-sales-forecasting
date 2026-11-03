"""
Sales Forecasting Module
Implements Moving-Average baseline and Scikit-learn Linear Regression models,
along with Matplotlib visualization rendering.
"""

import os
import tempfile
if 'MPLCONFIGDIR' not in os.environ:
    os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import io
import base64
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Headless backend for web server safety
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.linear_model import LinearRegression


def forecast_moving_average(series: pd.Series, window: int = 7, horizon: int = 14) -> dict:
    """
    Computes historical Simple Moving Average and generates future multi-step predictions.
    
    Args:
        series: Pandas Series with numeric sales values.
        window: Window size for moving average.
        horizon: Number of future periods to predict.
        
    Returns:
        dict containing 'historical_fit', 'forecast_values', 'window', 'horizon'
    """
    n = len(series)
    if n < window:
        raise ValueError(f"Dataset has {n} observations, but window size is {window}. Please choose a smaller window or upload more data.")

    values = series.to_numpy(dtype=float)
    
    # 1. Historical Moving Average: rolling mean of past 'window' values
    hist_ma = np.full(n, np.nan)
    for i in range(window, n):
        hist_ma[i] = np.mean(values[i - window:i])

    # 2. Future multi-step projection
    history = list(values)
    future_preds = []
    for _ in range(horizon):
        next_pred = float(np.mean(history[-window:]))
        next_pred = max(0.0, round(next_pred, 2))
        future_preds.append(next_pred)
        history.append(next_pred)

    return {
        'method': 'Moving Average',
        'window': window,
        'horizon': horizon,
        'historical_fit': hist_ma,
        'forecast_values': future_preds
    }


def forecast_linear_regression(series: pd.Series, horizon: int = 14) -> dict:
    """
    Fits a linear trend using Scikit-Learn LinearRegression and extrapolates future values.
    
    Args:
        series: Pandas Series with numeric sales values.
        horizon: Number of future periods to predict.
        
    Returns:
        dict containing 'historical_fit', 'forecast_values', 'slope', 'intercept', 'r2_score'
    """
    n = len(series)
    if n < 3:
        raise ValueError("Linear regression requires at least 3 historical observations.")

    y = series.to_numpy(dtype=float)
    X = np.arange(n).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, y)

    hist_preds = model.predict(X)
    hist_preds = np.clip(hist_preds, 0, None)  # Sales cannot be negative
    
    # Predict future time steps
    X_future = np.arange(n, n + horizon).reshape(-1, 1)
    future_preds = model.predict(X_future)
    future_preds = np.clip(future_preds, 0, None)
    future_preds = [round(float(v), 2) for v in future_preds]

    r2 = model.score(X, y)
    slope = float(model.coef_[0])
    intercept = float(model.intercept_)

    return {
        'method': 'Linear Regression',
        'horizon': horizon,
        'historical_fit': hist_preds,
        'forecast_values': future_preds,
        'slope': round(slope, 3),
        'intercept': round(intercept, 2),
        'r2_score': round(float(r2), 4),
        'equation': f"Revenue = {round(slope, 2)}·t + {round(intercept, 2)}"
    }


def generate_future_dates(last_date, horizon: int, freq: str = 'D'):
    """Generates future date strings based on frequency ('D' or 'M')."""
    last_dt = pd.to_datetime(last_date)
    if freq.upper() == 'M':
        future_dts = pd.date_range(start=last_dt + pd.DateOffset(months=1), periods=horizon, freq='MS')
        return [dt.strftime('%b %Y') for dt in future_dts]
    else:
        future_dts = pd.date_range(start=last_dt + pd.Timedelta(days=1), periods=horizon, freq='D')
        return [dt.strftime('%Y-%m-%d') for dt in future_dts]


def plot_to_base64(fig) -> str:
    """Converts a Matplotlib figure to a base64 encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=130)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    return img_b64


def generate_forecast_chart(df_agg: pd.DataFrame, 
                            ma_res: dict = None, 
                            lr_res: dict = None, 
                            future_dates: list = None,
                            freq: str = 'D') -> str:
    """
    Renders an actual vs forecast Matplotlib chart and returns it as a base64 string.
    """
    fig, ax = plt.subplots(figsize=(11, 5.2))
    
    # Prepare historical axis
    hist_x = list(range(len(df_agg)))
    hist_labels = df_agg['date_str'].tolist()
    hist_y = df_agg['revenue'].tolist()

    # Plot actual historical revenue
    ax.plot(hist_x, hist_y, label='Actual Revenue', color='#2563eb', linewidth=2.0, alpha=0.85)
    
    # Plot Moving Average historical fit & future forecast
    if ma_res:
        valid_idx = [i for i, v in enumerate(ma_res['historical_fit']) if not np.isnan(v)]
        valid_vals = [ma_res['historical_fit'][i] for i in valid_idx]
        ax.plot(valid_idx, valid_vals, label=f"MA ({ma_res['window']}-period) Trend", 
                color='#f59e0b', linestyle='--', linewidth=1.8)

        # Future forecast
        future_x = list(range(len(df_agg), len(df_agg) + len(ma_res['forecast_values'])))
        ax.plot(future_x, ma_res['forecast_values'], label='MA Forecast', 
                color='#d97706', linestyle='-', linewidth=2.5, marker='o', markersize=5)

    # Plot Linear Regression fit & future forecast
    if lr_res:
        ax.plot(hist_x, lr_res['historical_fit'], label='Linear Regression Trend', 
                color='#10b981', linestyle=':', linewidth=2.0)

        future_x = list(range(len(df_agg), len(df_agg) + len(lr_res['forecast_values'])))
        ax.plot(future_x, lr_res['forecast_values'], label='LinReg Forecast', 
                color='#059669', linestyle='-', linewidth=2.5, marker='s', markersize=5)

    # Shading the forecast future region
    if future_dates:
        start_future = len(df_agg) - 0.5
        end_future = len(df_agg) + len(future_dates) - 0.5
        ax.axvspan(start_future, end_future, color='#fef3c7', alpha=0.35, label='Forecast Horizon')
        ax.axvline(start_future, color='#9ca3af', linestyle='--', linewidth=1.2)

    # Configure axes and ticks
    total_points = len(df_agg) + (len(future_dates) if future_dates else 0)
    all_labels = hist_labels + (future_dates if future_dates else [])
    
    # Select tick frequency for readability
    step = max(1, total_points // 10)
    tick_indices = list(range(0, total_points, step))
    if (total_points - 1) not in tick_indices:
        tick_indices.append(total_points - 1)
        
    ax.set_xticks(tick_indices)
    ax.set_xticklabels([all_labels[i] for i in tick_indices], rotation=35, ha='right', fontsize=9)

    ax.set_title("Sales Revenue: Historical Trends and Predictive Forecast", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Timeline (" + ("Monthly" if freq.upper() == 'M' else "Daily") + ")", fontsize=11, labelpad=8)
    ax.set_ylabel("Revenue ($)", fontsize=11, labelpad=8)
    ax.yaxis.set_major_formatter('${x:,.0f}')
    ax.grid(True, linestyle='--', alpha=0.45)
    ax.legend(loc='upper left', frameon=True, framealpha=0.9)

    plt.tight_layout()
    return plot_to_base64(fig)
