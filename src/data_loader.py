"""
Data Loader Module
Manages application data state, switching seamlessly between CSV files and MySQL database.
"""

import os
import pandas as pd
from src.validation import validate_sales_data
from src.database import check_db_status, load_sales_from_db, save_sales_to_db

DEFAULT_SAMPLE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sample_sales.csv')
ACTIVE_UPLOAD_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'uploads', 'active_sales.csv')

# In-memory storage for active dataset
_ACTIVE_DATA = None
_ACTIVE_SOURCE_NAME = "Sample CSV (data/sample_sales.csv)"
_ACTIVE_SOURCE_TYPE = "csv"  # 'csv' or 'mysql'


def get_active_source_info():
    """Returns current active source details."""
    global _ACTIVE_SOURCE_NAME, _ACTIVE_SOURCE_TYPE
    return {
        'name': _ACTIVE_SOURCE_NAME,
        'type': _ACTIVE_SOURCE_TYPE
    }


def load_initial_data():
    """Loads default sample CSV data into memory if not already loaded."""
    global _ACTIVE_DATA, _ACTIVE_SOURCE_NAME, _ACTIVE_SOURCE_TYPE
    
    if _ACTIVE_DATA is not None:
        return _ACTIVE_DATA

    # Check if a previously uploaded active file exists
    if os.path.exists(ACTIVE_UPLOAD_PATH):
        try:
            df = pd.read_csv(ACTIVE_UPLOAD_PATH)
            is_valid, cleaned, _, _ = validate_sales_data(df)
            if is_valid:
                _ACTIVE_DATA = cleaned
                _ACTIVE_SOURCE_NAME = "Uploaded Active Dataset"
                _ACTIVE_SOURCE_TYPE = "csv"
                return _ACTIVE_DATA
        except Exception:
            pass

    # Fallback to sample_sales.csv
    if os.path.exists(DEFAULT_SAMPLE_PATH):
        df = pd.read_csv(DEFAULT_SAMPLE_PATH)
        is_valid, cleaned, _, _ = validate_sales_data(df)
        if is_valid:
            _ACTIVE_DATA = cleaned
            _ACTIVE_SOURCE_NAME = "Sample Dataset (Retail Sales)"
            _ACTIVE_SOURCE_TYPE = "csv"
            return _ACTIVE_DATA

    # In worst case return empty valid structure
    _ACTIVE_DATA = pd.DataFrame(columns=['sale_id', 'product_id', 'product_name', 'category', 'sale_date', 'quantity', 'unit_price', 'revenue', 'region'])
    return _ACTIVE_DATA


def get_active_data() -> pd.DataFrame:
    """Returns a copy of the currently active sales dataframe."""
    global _ACTIVE_DATA
    if _ACTIVE_DATA is None:
        load_initial_data()
    return _ACTIVE_DATA.copy()


def set_active_data(df: pd.DataFrame, source_name: str = "Uploaded CSV", source_type: str = "csv"):
    """Sets new active sales dataframe and persists to active_sales.csv."""
    global _ACTIVE_DATA, _ACTIVE_SOURCE_NAME, _ACTIVE_SOURCE_TYPE
    _ACTIVE_DATA = df.copy()
    _ACTIVE_SOURCE_NAME = source_name
    _ACTIVE_SOURCE_TYPE = source_type
    
    # Persist copy locally
    try:
        os.makedirs(os.path.dirname(ACTIVE_UPLOAD_PATH), exist_ok=True)
        df.to_csv(ACTIVE_UPLOAD_PATH, index=False)
    except Exception:
        pass


def reset_to_sample_data():
    """Resets active dataset back to the built-in sample_sales.csv."""
    global _ACTIVE_DATA, _ACTIVE_SOURCE_NAME, _ACTIVE_SOURCE_TYPE
    if os.path.exists(ACTIVE_UPLOAD_PATH):
        try:
            os.remove(ACTIVE_UPLOAD_PATH)
        except Exception:
            pass

    if os.path.exists(DEFAULT_SAMPLE_PATH):
        df = pd.read_csv(DEFAULT_SAMPLE_PATH)
        is_valid, cleaned, _, _ = validate_sales_data(df)
        if is_valid:
            _ACTIVE_DATA = cleaned
            _ACTIVE_SOURCE_NAME = "Sample Dataset (Retail Sales)"
            _ACTIVE_SOURCE_TYPE = "csv"
            return True, "Dataset successfully reset to default sample sales records."

    return False, "Sample dataset file could not be found."


def switch_to_mysql_data():
    """Fetches data from MySQL database and sets it as active dataset."""
    global _ACTIVE_DATA, _ACTIVE_SOURCE_NAME, _ACTIVE_SOURCE_TYPE
    df, err = load_sales_from_db()
    if df is not None and not df.empty:
        _ACTIVE_DATA = df
        _ACTIVE_SOURCE_NAME = "MySQL Database (sales_forecasting_db)"
        _ACTIVE_SOURCE_TYPE = "mysql"
        return True, f"Successfully loaded {len(df)} records from MySQL database."
    return False, err or "No data available in MySQL."


def sync_active_to_mysql():
    """Syncs the currently active dataset to MySQL database."""
    global _ACTIVE_DATA
    if _ACTIVE_DATA is None or _ACTIVE_DATA.empty:
        return False, "No active dataset to sync."
    return save_sales_to_db(_ACTIVE_DATA)


def get_data_summary(df: pd.DataFrame = None):
    """
    Computes key performance metrics (KPIs) from the sales dataset.
    """
    if df is None:
        df = get_active_data()

    if df.empty:
        return {
            'total_revenue': 0.0,
            'total_quantity': 0,
            'product_count': 0,
            'record_count': 0,
            'category_count': 0,
            'date_min': 'N/A',
            'date_max': 'N/A',
            'days_span': 0,
            'avg_order_value': 0.0,
            'source_info': get_active_source_info()
        }

    total_revenue = float(df['revenue'].sum())
    total_quantity = int(df['quantity'].sum())
    product_count = int(df['product_name'].nunique())
    record_count = int(len(df))
    category_count = int(df['category'].nunique()) if 'category' in df.columns else 1
    
    dates = pd.to_datetime(df['sale_date'])
    date_min = dates.min().strftime('%Y-%m-%d')
    date_max = dates.max().strftime('%Y-%m-%d')
    days_span = (dates.max() - dates.min()).days + 1
    avg_order_value = round(total_revenue / record_count, 2) if record_count > 0 else 0.0

    return {
        'total_revenue': round(total_revenue, 2),
        'total_quantity': total_quantity,
        'product_count': product_count,
        'record_count': record_count,
        'category_count': category_count,
        'date_min': date_min,
        'date_max': date_max,
        'days_span': days_span,
        'avg_order_value': avg_order_value,
        'source_info': get_active_source_info()
    }
