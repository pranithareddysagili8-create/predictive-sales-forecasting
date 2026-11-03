"""
Generates high-resolution publication-quality PNG diagrams and charts
for embedding directly into the technical documentation Word document.
"""

import os
import tempfile
if 'MPLCONFIGDIR' not in os.environ:
    os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from src.data_loader import get_active_data
from src.preprocessing import aggregate_sales, get_product_analytics, get_category_analytics
from src.forecasting import forecast_moving_average, forecast_linear_regression, generate_future_dates
from src.evaluation import evaluate_models

os.makedirs('docs/images', exist_ok=True)
df = get_active_data()
df_daily = aggregate_sales(df, freq='D')

# -------------------------------------------------------------
# 1. Historical Revenue Velocity Trend Chart
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 3.8), dpi=160)
x = range(len(df_daily))
y = df_daily['revenue'].tolist()
ax.plot(x, y, color='#2563eb', linewidth=1.8, label='Daily Revenue ($)')
ax.fill_between(x, y, color='#3b82f6', alpha=0.15)
step = max(1, len(df_daily) // 8)
ticks = list(range(0, len(df_daily), step))
ax.set_xticks(ticks)
ax.set_xticklabels([df_daily['date_str'].iloc[i] for i in ticks], rotation=25, ha='right', fontsize=8)
ax.set_title('Historical Sales Revenue Velocity (270 Days Timeline)', fontsize=12, fontweight='bold', pad=10)
ax.set_ylabel('Revenue ($)', fontsize=9)
ax.yaxis.set_major_formatter('${x:,.0f}')
ax.grid(True, linestyle='--', alpha=0.45)
ax.legend(loc='upper left', fontsize=8)
plt.tight_layout()
fig.savefig('docs/images/trend_chart.png')
plt.close(fig)

# -------------------------------------------------------------
# 2. Top Products Horizontal Bar Chart
# -------------------------------------------------------------
df_prods = get_product_analytics(df, top_n=8).sort_values(by='revenue', ascending=True)
fig, ax = plt.subplots(figsize=(8.5, 3.8), dpi=160)
y_pos = range(len(df_prods))
bars = ax.barh(y_pos, df_prods['revenue'], color='#6366f1', height=0.65)
ax.set_yticks(y_pos)
ax.set_yticklabels(df_prods['product_name'], fontsize=8.5)
ax.set_title('Top 8 Best-Selling Products Ranked by Gross Revenue', fontsize=12, fontweight='bold', pad=10)
ax.set_xlabel('Total Revenue Generated ($)', fontsize=9)
ax.xaxis.set_major_formatter('${x:,.0f}')
for bar in bars:
    w = bar.get_width()
    ax.text(w + 350, bar.get_y() + bar.get_height()/2, f'${w:,.0f}', ha='left', va='center', fontsize=7.5, color='#374151', fontweight='bold')
ax.grid(True, linestyle='--', alpha=0.4, axis='x')
plt.tight_layout()
fig.savefig('docs/images/product_chart.png')
plt.close(fig)

# -------------------------------------------------------------
# 3. Forecast Trajectory (Actual vs SMA vs LinReg)
# -------------------------------------------------------------
ma_res = forecast_moving_average(df_daily['revenue'], window=7, horizon=14)
lr_res = forecast_linear_regression(df_daily['revenue'], horizon=14)
future_dates = generate_future_dates(df_daily['date'].iloc[-1], horizon=14, freq='D')

fig, ax = plt.subplots(figsize=(8.5, 4.0), dpi=160)
hist_x = list(range(len(df_daily)))
ax.plot(hist_x, df_daily['revenue'], label='Actual Sales Revenue', color='#2563eb', linewidth=1.6, alpha=0.75)
valid_idx = [i for i, v in enumerate(ma_res['historical_fit']) if not np.isnan(v)]
ax.plot(valid_idx, [ma_res['historical_fit'][i] for i in valid_idx], label='MA (7-period) Fit', color='#f59e0b', linestyle='--', linewidth=1.6)
ax.plot(hist_x, lr_res['historical_fit'], label='Linear Regression Fit', color='#10b981', linestyle=':', linewidth=1.8)

future_x = list(range(len(df_daily), len(df_daily) + 14))
ax.plot(future_x, ma_res['forecast_values'], label='MA 14-Day Forecast', color='#d97706', linewidth=2.2, marker='o', markersize=4)
ax.plot(future_x, lr_res['forecast_values'], label='LinReg 14-Day Forecast', color='#059669', linewidth=2.2, marker='s', markersize=4)
ax.axvspan(len(df_daily) - 0.5, len(df_daily) + 13.5, color='#fef3c7', alpha=0.35, label='14-Day Forecast Horizon')
ax.axvline(len(df_daily) - 0.5, color='#9ca3af', linestyle='--', linewidth=1.2)

total_pts = len(df_daily) + 14
all_lbls = df_daily['date_str'].tolist() + future_dates
step = max(1, total_pts // 8)
t_idx = list(range(0, total_pts, step))
ax.set_xticks(t_idx)
ax.set_xticklabels([all_lbls[i] for i in t_idx], rotation=25, ha='right', fontsize=8)
ax.set_title('Predictive Sales Forecast: Historical Demand and 14-Day Projections', fontsize=12, fontweight='bold', pad=10)
ax.set_ylabel('Revenue ($)', fontsize=9)
ax.yaxis.set_major_formatter('${x:,.0f}')
ax.grid(True, linestyle='--', alpha=0.45)
ax.legend(loc='upper left', fontsize=8)
plt.tight_layout()
fig.savefig('docs/images/forecast_chart.png')
plt.close(fig)

# -------------------------------------------------------------
# 4. Holdout Evaluation Chart
# -------------------------------------------------------------
eval_res = evaluate_models(df_daily, train_ratio=0.8, window=7)
split_idx = eval_res['train_count']
y_test = df_daily['revenue'].iloc[split_idx:].to_numpy(dtype=float)

fig, ax = plt.subplots(figsize=(8.5, 4.0), dpi=160)
n = len(df_daily)
x_all = list(range(n))
ax.plot(x_all[:split_idx], df_daily['revenue'].iloc[:split_idx], label=f'Training Window ({split_idx} Days)', color='#6b7280', linewidth=1.5, alpha=0.7)
ax.plot(x_all[split_idx:], y_test, label=f'Actual Holdout Test Window ({len(y_test)} Days)', color='#1e3a8a', linewidth=2.2, marker='o', markersize=3.5)

ma_preds = [r['ma_pred'] for r in eval_res['test_rows']]
lr_preds = [r['lr_pred'] for r in eval_res['test_rows']]
ax.plot(x_all[split_idx:], ma_preds, label='Moving Average Predictions', color='#d97706', linestyle='--', linewidth=1.8)
ax.plot(x_all[split_idx:], lr_preds, label='Linear Regression Predictions', color='#059669', linestyle=':', linewidth=1.8)
ax.axvline(split_idx - 0.5, color='#ef4444', linestyle='-', linewidth=1.4, label='Chronological Split (80/20)')
ax.axvspan(split_idx - 0.5, n - 0.5, color='#dbeafe', alpha=0.25, label='Holdout Evaluation Period')

step = max(1, n // 8)
t_idx = list(range(0, n, step))
ax.set_xticks(t_idx)
ax.set_xticklabels([df_daily['date_str'].iloc[i] for i in t_idx], rotation=25, ha='right', fontsize=8)
ax.set_title('Chronological Holdout Model Evaluation (Train vs Test Actual vs Models)', fontsize=12, fontweight='bold', pad=10)
ax.set_ylabel('Revenue ($)', fontsize=9)
ax.yaxis.set_major_formatter('${x:,.0f}')
ax.grid(True, linestyle='--', alpha=0.45)
ax.legend(loc='upper left', fontsize=8)
plt.tight_layout()
fig.savefig('docs/images/evaluation_chart.png')
plt.close(fig)

# -------------------------------------------------------------
# 5. Architecture Tier Flow Diagram
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 3.6), dpi=160)
ax.axis('off')

# User Layer Box
rect1 = patches.FancyBboxPatch((0.03, 0.52), 0.26, 0.40, boxstyle="round,pad=0.03", fc="#dbeafe", ec="#1d4ed8", lw=2)
ax.add_patch(rect1)
ax.text(0.16, 0.72, "Client / UI Tier\n(HTML5, CSS3, Jinja2)\n• Dashboard & KPI Cards\n• CSV Upload & Preview\n• Dynamic Analytics & Reports", 
        ha='center', va='center', fontsize=7.5, fontweight='bold', color="#1e293b")

# Flask Application Layer Box
rect2 = patches.FancyBboxPatch((0.37, 0.52), 0.26, 0.40, boxstyle="round,pad=0.03", fc="#d1fae5", ec="#047857", lw=2)
ax.add_patch(rect2)
ax.text(0.50, 0.72, "Application Controller Tier\n(Python & Flask 3.1)\n• MVC Route Handlers\n• In-Memory Forecast Cache\n• Validation & Error Shield", 
        ha='center', va='center', fontsize=7.5, fontweight='bold', color="#1e293b")

# Processing & ML Tier Box
rect3 = patches.FancyBboxPatch((0.71, 0.52), 0.26, 0.40, boxstyle="round,pad=0.03", fc="#ede9fe", ec="#6d28d9", lw=2)
ax.add_patch(rect3)
ax.text(0.84, 0.72, "Analytical & ML Tier\n(Pandas, NumPy, Scikit-learn)\n• Daily/Monthly Aggregation\n• SMA Baseline Modeling\n• OLS Trend Regression & MAE", 
        ha='center', va='center', fontsize=7.5, fontweight='bold', color="#1e293b")

# Dual-Engine Storage Tier Box
rect4 = patches.FancyBboxPatch((0.25, 0.06), 0.50, 0.34, boxstyle="round,pad=0.03", fc="#fef3c7", ec="#b45309", lw=2)
ax.add_patch(rect4)
ax.text(0.50, 0.23, "Dual-Engine Persistence Tier\n• Primary Mode: In-Memory / CSV (sample_sales.csv)\n• Enterprise Mode: MySQL Relational DB (sales_forecasting_db)\n• Products, Sales Transactions & Forecast Logs Tables", 
        ha='center', va='center', fontsize=7.5, fontweight='bold', color="#1e293b")

# Connections
ax.annotate('', xy=(0.36, 0.72), xytext=(0.30, 0.72), arrowprops=dict(arrowstyle='<->', color='#334155', lw=2))
ax.annotate('', xy=(0.70, 0.72), xytext=(0.64, 0.72), arrowprops=dict(arrowstyle='<->', color='#334155', lw=2))
ax.annotate('', xy=(0.50, 0.41), xytext=(0.50, 0.51), arrowprops=dict(arrowstyle='<->', color='#334155', lw=2))

ax.set_title('Predictive Sales Forecasting System: Multi-Tier Architecture', fontsize=11, fontweight='bold', pad=8)
plt.tight_layout()
fig.savefig('docs/images/architecture_diagram.png')
plt.close(fig)

print("All 5 publication figures successfully created in docs/images/")
