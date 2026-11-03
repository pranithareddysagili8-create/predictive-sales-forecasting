"""
Comprehensive Automated Test Suite for Sales Forecasting & Analytics System
Verifies data validation, preprocessing, forecasting, evaluation, and Flask routes.
"""

import os
import tempfile
if 'MPLCONFIGDIR' not in os.environ:
    os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import io
import unittest
import pandas as pd
import numpy as np

from src.validation import validate_sales_data
from src.preprocessing import (
    aggregate_sales, get_product_analytics, get_category_analytics,
    get_region_analytics, get_summary_stats, generate_sales_trend_chart
)
from src.forecasting import (
    forecast_moving_average, forecast_linear_regression,
    generate_future_dates, generate_forecast_chart
)
from src.evaluation import calculate_metrics, evaluate_models
from app import app


class TestSalesForecastingSystem(unittest.TestCase):

    def setUp(self):
        # Configure test Flask client
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        # Create valid synthetic dataset for testing
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        self.sample_df = pd.DataFrame({
            'sale_id': range(1, 31),
            'product_id': [101, 102] * 15,
            'product_name': ['Mouse', 'Keyboard'] * 15,
            'category': ['Electronics', 'Accessories'] * 15,
            'sale_date': dates.strftime('%Y-%m-%d'),
            'quantity': [2, 5, 1, 3] * 7 + [4, 2],
            'unit_price': [25.0, 50.0] * 15,
            'region': ['North', 'South', 'East'] * 10
        })

    # -------------------------------------------------------------
    # 1. Data Validation Tests
    # -------------------------------------------------------------
    def test_validation_empty_dataframe(self):
        empty_df = pd.DataFrame()
        valid, _, errors, _ = validate_sales_data(empty_df)
        self.assertFalse(valid)
        self.assertTrue(any("empty" in e.lower() for e in errors))

    def test_validation_missing_columns(self):
        bad_df = pd.DataFrame({'sale_date': ['2024-01-01'], 'quantity': [5]})
        valid, _, errors, _ = validate_sales_data(bad_df)
        self.assertFalse(valid)
        self.assertTrue(any("missing required columns" in e.lower() for e in errors))

    def test_validation_negative_quantity(self):
        bad_df = self.sample_df.copy()
        bad_df.loc[3, 'quantity'] = -10
        valid, _, errors, _ = validate_sales_data(bad_df)
        self.assertFalse(valid)
        self.assertTrue(any("quantity less than or equal to 0" in e.lower() for e in errors))

    def test_validation_negative_price(self):
        bad_df = self.sample_df.copy()
        bad_df.loc[5, 'unit_price'] = -45.0
        valid, _, errors, _ = validate_sales_data(bad_df)
        self.assertFalse(valid)
        self.assertTrue(any("unit price less than or equal to 0" in e.lower() for e in errors))

    def test_validation_valid_data(self):
        valid, cleaned, errors, _ = validate_sales_data(self.sample_df)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)
        self.assertIn('revenue', cleaned.columns)
        self.assertEqual(cleaned['revenue'].iloc[0], cleaned['quantity'].iloc[0] * cleaned['unit_price'].iloc[0])

    # -------------------------------------------------------------
    # 2. Preprocessing & Aggregation Tests
    # -------------------------------------------------------------
    def test_daily_and_monthly_aggregation(self):
        valid, cleaned, _, _ = validate_sales_data(self.sample_df)
        daily = aggregate_sales(cleaned, freq='D')
        self.assertEqual(len(daily), 30)
        self.assertIn('revenue', daily.columns)

        monthly = aggregate_sales(cleaned, freq='M')
        self.assertGreaterEqual(len(monthly), 1)

    def test_product_and_category_analytics(self):
        valid, cleaned, _, _ = validate_sales_data(self.sample_df)
        prods = get_product_analytics(cleaned)
        self.assertEqual(len(prods), 2)
        self.assertIn('revenue_share', prods.columns)

        cats = get_category_analytics(cleaned)
        self.assertEqual(len(cats), 2)
        self.assertAlmostEqual(cats['revenue_share'].sum(), 100.0, delta=0.5)

    # -------------------------------------------------------------
    # 3. Forecasting Tests
    # -------------------------------------------------------------
    def test_moving_average_forecasting(self):
        valid, cleaned, _, _ = validate_sales_data(self.sample_df)
        daily = aggregate_sales(cleaned, freq='D')
        res = forecast_moving_average(daily['revenue'], window=5, horizon=7)
        
        self.assertEqual(len(res['forecast_values']), 7)
        self.assertEqual(len(res['historical_fit']), len(daily))
        self.assertTrue(all(v >= 0 for v in res['forecast_values']))

    def test_linear_regression_forecasting(self):
        valid, cleaned, _, _ = validate_sales_data(self.sample_df)
        daily = aggregate_sales(cleaned, freq='D')
        res = forecast_linear_regression(daily['revenue'], horizon=7)
        
        self.assertEqual(len(res['forecast_values']), 7)
        self.assertIn('slope', res)
        self.assertIn('intercept', res)
        self.assertIn('r2_score', res)
        self.assertTrue(all(v >= 0 for v in res['forecast_values']))

    def test_forecast_chart_generation(self):
        valid, cleaned, _, _ = validate_sales_data(self.sample_df)
        daily = aggregate_sales(cleaned, freq='D')
        ma_res = forecast_moving_average(daily['revenue'], window=5, horizon=5)
        lr_res = forecast_linear_regression(daily['revenue'], horizon=5)
        future_dates = generate_future_dates(daily['date'].iloc[-1], horizon=5, freq='D')
        
        chart_b64 = generate_forecast_chart(daily, ma_res, lr_res, future_dates, freq='D')
        self.assertIsInstance(chart_b64, str)
        self.assertGreater(len(chart_b64), 100)

    # -------------------------------------------------------------
    # 4. Evaluation Tests
    # -------------------------------------------------------------
    def test_evaluation_metrics_calculation(self):
        y_true = np.array([100.0, 150.0, 200.0])
        y_pred = np.array([110.0, 140.0, 210.0])
        metrics = calculate_metrics(y_true, y_pred)
        
        # Absolute errors are 10, 10, 10 -> MAE = 10.0
        self.assertAlmostEqual(metrics['mae'], 10.0)
        self.assertAlmostEqual(metrics['rmse'], 10.0)
        self.assertGreater(metrics['mape'], 0)

    def test_chronological_holdout_evaluation(self):
        valid, cleaned, _, _ = validate_sales_data(self.sample_df)
        daily = aggregate_sales(cleaned, freq='D')
        eval_res = evaluate_models(daily, train_ratio=0.8, window=5)
        
        self.assertTrue(eval_res['success'])
        self.assertIn('ma_metrics', eval_res)
        self.assertIn('lr_metrics', eval_res)
        self.assertIn('winner', eval_res)
        self.assertGreater(len(eval_res['chart_b64']), 100)
        self.assertEqual(eval_res['train_count'] + eval_res['test_count'], len(daily))

    # -------------------------------------------------------------
    # 5. Flask Web Routes Tests
    # -------------------------------------------------------------
    def test_dashboard_route(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Sales Analytics Dashboard", resp.data)

    def test_upload_page_route(self):
        resp = self.client.get('/upload')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Upload Historical Sales Data", resp.data)

    def test_analytics_page_route(self):
        resp_daily = self.client.get('/analytics?freq=D')
        self.assertEqual(resp_daily.status_code, 200)
        self.assertIn(b"Business Analytics", resp_daily.data)

        resp_monthly = self.client.get('/analytics?freq=M')
        self.assertEqual(resp_monthly.status_code, 200)

    def test_forecasting_route_get_and_post(self):
        resp_get = self.client.get('/forecasting')
        self.assertEqual(resp_get.status_code, 200)
        self.assertIn(b"Predictive Sales Forecasting", resp_get.data)

        resp_post = self.client.post('/generate-forecast', data={
            'method': 'both',
            'freq': 'D',
            'horizon': '7',
            'window': '5'
        })
        self.assertEqual(resp_post.status_code, 200)
        self.assertIn(b"Projected Sales Revenue by Future Period", resp_post.data)

    def test_evaluation_route(self):
        resp = self.client.get('/evaluation')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Forecast Model Evaluation", resp.data)

    def test_reports_route(self):
        resp = self.client.get('/reports')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Executive Forecasting &amp; Analytics Report", resp.data)

    def test_download_sample_and_forecast_csv(self):
        resp_sample = self.client.get('/download-sample')
        self.assertEqual(resp_sample.status_code, 200)
        self.assertIn(b"sale_id,product_id", resp_sample.data)

        # Run forecast first so cache is active
        self.client.post('/generate-forecast', data={'method': 'both', 'freq': 'D', 'horizon': '7', 'window': '5'})
        resp_forecast = self.client.get('/download-forecast-csv')
        self.assertEqual(resp_forecast.status_code, 200)
        self.assertIn(b"Period_Date", resp_forecast.data)

    def test_upload_invalid_csv_file(self):
        # Test uploading non-csv file
        data = {'file': (io.BytesIO(b"Hello world"), 'bad.txt')}
        resp = self.client.post('/upload-file', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertIn(b"Only CSV (.csv) files are supported", resp.data)

        # Test uploading CSV with missing columns
        bad_csv = io.BytesIO(b"date,something\n2024-01-01,10\n")
        data2 = {'file': (bad_csv, 'missing_cols.csv')}
        resp2 = self.client.post('/upload-file', data=data2, content_type='multipart/form-data', follow_redirects=True)
        self.assertIn(b"Missing required columns", resp2.data)


if __name__ == '__main__':
    unittest.main()
