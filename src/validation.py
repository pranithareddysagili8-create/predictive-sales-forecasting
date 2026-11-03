"""
Data Validation Module
Provides robust verification of uploaded sales datasets, checking required columns,
data types, negative numbers, and date formats.
"""

import pandas as pd
import numpy as np


REQUIRED_COLUMNS = ['sale_date', 'product_name', 'quantity', 'unit_price']

# Mapping common column name variations to standard names
COLUMN_ALIASES = {
    'date': 'sale_date',
    'sales_date': 'sale_date',
    'order_date': 'sale_date',
    'product': 'product_name',
    'item_name': 'product_name',
    'item': 'product_name',
    'qty': 'quantity',
    'units': 'quantity',
    'price': 'unit_price',
    'rate': 'unit_price',
    'product_category': 'category',
    'area': 'region',
    'location': 'region'
}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes column names to lowercase with underscores and maps common aliases."""
    normalized_cols = {col: col.strip().lower().replace(' ', '_') for col in df.columns}
    df = df.rename(columns=normalized_cols)
    
    # Apply aliases if exact required column is missing but alias exists
    for alias, standard in COLUMN_ALIASES.items():
        if standard not in df.columns and alias in df.columns:
            df = df.rename(columns={alias: standard})
            
    return df


def validate_sales_data(df: pd.DataFrame, min_records: int = 5):
    """
    Validates the sales dataset.
    
    Returns:
        tuple: (is_valid: bool, cleaned_df: pd.DataFrame or None, errors: list[str], warnings: list[str])
    """
    errors = []
    warnings = []

    if df is None or df.empty:
        errors.append("The uploaded file is empty. Please provide a CSV file with sales records.")
        return False, None, errors, warnings

    # Normalize column names
    df = standardize_columns(df)

    # Check required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}. "
                      f"Expected columns: {', '.join(REQUIRED_COLUMNS)}")
        return False, None, errors, warnings

    # Fill optional columns if missing
    if 'category' not in df.columns:
        df['category'] = 'General'
        warnings.append("Optional column 'category' was missing; populated with 'General'.")

    if 'region' not in df.columns:
        df['region'] = 'Default'
        warnings.append("Optional column 'region' was missing; populated with 'Default'.")

    if 'product_id' not in df.columns:
        # Create deterministic synthetic product IDs based on product name
        unique_prods = {name: idx + 101 for idx, name in enumerate(df['product_name'].dropna().unique())}
        df['product_id'] = df['product_name'].map(unique_prods)

    # Validate row count
    initial_count = len(df)
    if initial_count < min_records:
        errors.append(f"The dataset contains only {initial_count} records. A minimum of {min_records} records is required for analytics.")
        return False, None, errors, warnings

    # Validate dates
    try:
        df['sale_date'] = pd.to_datetime(df['sale_date'], errors='coerce')
        invalid_dates_count = df['sale_date'].isna().sum()
        if invalid_dates_count > 0:
            errors.append(f"Found {invalid_dates_count} row(s) with invalid or unparseable dates.")
    except Exception as e:
        errors.append(f"Date conversion error: {str(e)}")

    # Validate numeric quantities
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    invalid_qty_count = df['quantity'].isna().sum()
    if invalid_qty_count > 0:
        errors.append(f"Found {invalid_qty_count} row(s) with non-numeric quantity values.")

    # Validate numeric unit prices
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    invalid_price_count = df['unit_price'].isna().sum()
    if invalid_price_count > 0:
        errors.append(f"Found {invalid_price_count} row(s) with non-numeric unit price values.")

    # Check for negative or zero quantities
    negative_qty = (df['quantity'] <= 0).sum()
    if negative_qty > 0:
        errors.append(f"Found {negative_qty} row(s) with quantity less than or equal to 0. Quantities must be positive integers.")

    # Check for negative or zero unit prices
    negative_price = (df['unit_price'] <= 0).sum()
    if negative_price > 0:
        errors.append(f"Found {negative_price} row(s) with unit price less than or equal to 0. Prices must be positive numbers.")

    # If errors occurred, abort and return
    if errors:
        return False, None, errors, warnings

    # Clean DataFrame: sort by date and ensure revenue calculation
    cleaned_df = df.copy()
    cleaned_df['quantity'] = cleaned_df['quantity'].astype(int)
    cleaned_df['unit_price'] = cleaned_df['unit_price'].astype(float)
    cleaned_df['revenue'] = (cleaned_df['quantity'] * cleaned_df['unit_price']).round(2)
    cleaned_df['sale_date'] = cleaned_df['sale_date'].dt.strftime('%Y-%m-%d')
    cleaned_df = cleaned_df.sort_values(by='sale_date').reset_index(drop=True)

    if 'sale_id' not in cleaned_df.columns:
        cleaned_df['sale_id'] = range(1, len(cleaned_df) + 1)

    return True, cleaned_df, errors, warnings
