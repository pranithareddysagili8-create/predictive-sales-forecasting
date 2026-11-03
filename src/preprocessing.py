"""
Data Preprocessing and Aggregation Module
Aggregates sales data across time intervals (daily/monthly), product lines,
categories, and geographic regions.
"""

import os
import tempfile
if 'MPLCONFIGDIR' not in os.environ:
    os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import io
import base64
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_to_base64(fig) -> str:
    """Converts a Matplotlib figure to a base64 encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    return img_b64


def generate_sales_trend_chart(df_agg: pd.DataFrame, title: str = "Sales Revenue Trend Over Time") -> str:
    """Renders revenue trend over time as a base64 PNG."""
    fig, ax = plt.subplots(figsize=(10, 4.2))
    x = range(len(df_agg))
    y = df_agg['revenue'].tolist()
    labels = df_agg['date_str'].tolist()

    ax.plot(x, y, color='#2563eb', linewidth=2.2, marker='o', markersize=3, label='Revenue')
    ax.fill_between(x, y, color='#3b82f6', alpha=0.15)

    step = max(1, len(df_agg) // 9)
    ticks = list(range(0, len(df_agg), step))
    if (len(df_agg) - 1) not in ticks:
        ticks.append(len(df_agg) - 1)

    ax.set_xticks(ticks)
    ax.set_xticklabels([labels[i] for i in ticks], rotation=30, ha='right', fontsize=9)
    ax.set_title(title, fontsize=13, fontweight='bold', pad=12)
    ax.set_ylabel("Revenue ($)", fontsize=10)
    ax.yaxis.set_major_formatter('${x:,.0f}')
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    return plot_to_base64(fig)


def generate_product_bar_chart(df_prods: pd.DataFrame, top_n: int = 8) -> str:
    """Renders top products by revenue bar chart."""
    df_top = df_prods.head(top_n).sort_values(by='revenue', ascending=True)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    
    y_pos = range(len(df_top))
    bars = ax.barh(y_pos, df_top['revenue'], color='#6366f1', height=0.65)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_top['product_name'], fontsize=9)
    ax.set_title(f"Top {len(df_top)} Best-Selling Products by Revenue", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Revenue ($)", fontsize=10)
    ax.xaxis.set_major_formatter('${x:,.0f}')
    
    # Value annotations on bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + (df_top['revenue'].max() * 0.01), bar.get_y() + bar.get_height()/2,
                f"${width:,.0f}", ha='left', va='center', fontsize=8.5, color='#374151')

    ax.grid(True, linestyle='--', alpha=0.4, axis='x')
    plt.tight_layout()
    return plot_to_base64(fig)


def generate_category_chart(df_cats: pd.DataFrame) -> str:
    """Renders category revenue distribution pie / donut chart."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = ['#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#14b8a6']
    
    wedges, texts, autotexts = ax.pie(
        df_cats['revenue'], 
        labels=df_cats['category'], 
        autopct='%1.1f%%',
        startangle=140,
        colors=colors[:len(df_cats)],
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2),
        textprops=dict(color='#1f2937', fontsize=9)
    )
    for at in autotexts:
        at.set_color('white')
        at.set_weight('bold')
        at.set_fontsize(8.5)

    ax.set_title("Revenue Breakdown by Product Category", fontsize=13, fontweight='bold', pad=12)
    plt.tight_layout()
    return plot_to_base64(fig)



def aggregate_sales(df: pd.DataFrame, freq: str = 'D') -> pd.DataFrame:
    """
    Aggregates sales by frequency ('D' for Daily, 'M' for Monthly).
    Ensures a continuous timeline with 0 values filled for days/months with no sales.
    
    Returns:
        pd.DataFrame with columns: ['date', 'revenue', 'quantity']
    """
    if df.empty:
        return pd.DataFrame(columns=['date', 'revenue', 'quantity'])

    df_work = df.copy()
    df_work['sale_date'] = pd.to_datetime(df_work['sale_date'])
    
    if freq.upper() == 'M':
        # Group by Year-Month
        df_work['period'] = df_work['sale_date'].dt.to_period('M').dt.to_timestamp()
        grouped = df_work.groupby('period').agg({'revenue': 'sum', 'quantity': 'sum'}).reset_index()
        
        # Ensure full continuous monthly range
        full_range = pd.date_range(start=grouped['period'].min(), end=grouped['period'].max(), freq='MS')
        grouped = grouped.set_index('period').reindex(full_range, fill_value=0.0).reset_index()
        grouped = grouped.rename(columns={'index': 'date'})
        grouped['date_str'] = grouped['date'].dt.strftime('%b %Y')
    else:
        # Group by Day
        grouped = df_work.groupby('sale_date').agg({'revenue': 'sum', 'quantity': 'sum'}).reset_index()
        full_range = pd.date_range(start=grouped['sale_date'].min(), end=grouped['sale_date'].max(), freq='D')
        grouped = grouped.set_index('sale_date').reindex(full_range, fill_value=0.0).reset_index()
        grouped = grouped.rename(columns={'index': 'date'})
        grouped['date_str'] = grouped['date'].dt.strftime('%Y-%m-%d')

    grouped['revenue'] = grouped['revenue'].round(2)
    grouped['quantity'] = grouped['quantity'].astype(int)
    return grouped


def get_product_analytics(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Aggregates product performance metrics.
    """
    if df.empty:
        return pd.DataFrame()

    agg_dict = {
        'revenue': 'sum',
        'quantity': 'sum',
        'sale_id': 'count',
        'unit_price': 'mean'
    }
    grouped = df.groupby(['product_name', 'category']).agg(agg_dict).reset_index()
    grouped = grouped.rename(columns={'sale_id': 'order_count', 'unit_price': 'avg_unit_price'})
    grouped['revenue'] = grouped['revenue'].round(2)
    grouped['avg_unit_price'] = grouped['avg_unit_price'].round(2)
    
    total_rev = df['revenue'].sum()
    if total_rev > 0:
        grouped['revenue_share'] = ((grouped['revenue'] / total_rev) * 100).round(1)
    else:
        grouped['revenue_share'] = 0.0

    grouped = grouped.sort_values(by='revenue', ascending=False).reset_index(drop=True)
    if top_n:
        return grouped.head(top_n)
    return grouped


def get_category_analytics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates sales performance by category.
    """
    if df.empty:
        return pd.DataFrame()

    grouped = df.groupby('category').agg({
        'revenue': 'sum',
        'quantity': 'sum',
        'sale_id': 'count'
    }).reset_index()
    grouped = grouped.rename(columns={'sale_id': 'order_count'})
    grouped['revenue'] = grouped['revenue'].round(2)
    
    total_rev = df['revenue'].sum()
    if total_rev > 0:
        grouped['revenue_share'] = ((grouped['revenue'] / total_rev) * 100).round(1)
    else:
        grouped['revenue_share'] = 0.0

    return grouped.sort_values(by='revenue', ascending=False).reset_index(drop=True)


def get_region_analytics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates sales performance by region.
    """
    if df.empty or 'region' not in df.columns:
        return pd.DataFrame()

    grouped = df.groupby('region').agg({
        'revenue': 'sum',
        'quantity': 'sum',
        'sale_id': 'count'
    }).reset_index()
    grouped = grouped.rename(columns={'sale_id': 'order_count'})
    grouped['revenue'] = grouped['revenue'].round(2)
    return grouped.sort_values(by='revenue', ascending=False).reset_index(drop=True)


def get_summary_stats(series: pd.Series):
    """
    Calculates summary statistics for a numeric series.
    """
    if series.empty:
        return {}
    return {
        'mean': round(float(series.mean()), 2),
        'median': round(float(series.median()), 2),
        'min': round(float(series.min()), 2),
        'max': round(float(series.max()), 2),
        'std': round(float(series.std()), 2) if len(series) > 1 else 0.0
    }
