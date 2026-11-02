"""
Generates additional visual UI architecture and page layout figures
for Chapters 14 & 4 in the 20-page Word documentation.
"""

import os
import tempfile
if 'MPLCONFIGDIR' not in os.environ:
    os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs('docs/images', exist_ok=True)

# -------------------------------------------------------------
# 1. UI Layout Figure: Dashboard View
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=160)
ax.axis('off')

# Main Canvas Background
bg = patches.Rectangle((0, 0), 1, 1, facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.5, transform=ax.transAxes)
ax.add_patch(bg)

# Navbar Header
nav = patches.Rectangle((0, 0.88), 1, 0.12, facecolor='#0f172a', edgecolor='none', transform=ax.transAxes)
ax.add_patch(nav)
ax.text(0.04, 0.94, "SalesPredict Analytics | Executive Dashboard", color='#ffffff', fontsize=9, fontweight='bold', transform=ax.transAxes)
ax.text(0.96, 0.94, "Source: Sample CSV (Retail Sales) [Active] • MySQL Offline", color='#93c5fd', fontsize=7.5, ha='right', transform=ax.transAxes)

# 4 KPI Cards
kpis = [
    (0.04, 0.68, 0.20, 0.16, "TOTAL REVENUE", "$366,413.00", "Avg Order: $594.83", "#dbeafe", "#1d4ed8"),
    (0.28, 0.68, 0.20, 0.16, "TOTAL QUANTITY", "3,112 Units", "Across 616 transactions", "#d1fae5", "#047857"),
    (0.52, 0.68, 0.20, 0.16, "ACTIVE SKUS", "12 Products", "5 Market Categories", "#ede9fe", "#6d28d9"),
    (0.76, 0.68, 0.20, 0.16, "RECORD COUNT", "616 Records", "Jan 01 to Sep 26 (270d)", "#fef3c7", "#b45309")
]
for x, y, w, h, label, val, sub, bgc, fgc in kpis:
    card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015", fc="#ffffff", ec="#e2e8f0", lw=1.2, transform=ax.transAxes)
    ax.add_patch(card)
    ax.text(x + 0.015, y + h - 0.04, label, fontsize=6.5, fontweight='bold', color='#64748b', transform=ax.transAxes)
    ax.text(x + 0.015, y + 0.07, val, fontsize=11, fontweight='bold', color=fgc, transform=ax.transAxes)
    ax.text(x + 0.015, y + 0.025, sub, fontsize=5.8, color='#94a3b8', transform=ax.transAxes)

# Left Card: Trend Velocity Chart
card_trend = patches.FancyBboxPatch((0.04, 0.22), 0.52, 0.42, boxstyle="round,pad=0.015", fc="#ffffff", ec="#e2e8f0", lw=1.2, transform=ax.transAxes)
ax.add_patch(card_trend)
ax.text(0.06, 0.59, "Historical Sales Revenue Velocity (270 Days)", fontsize=8, fontweight='bold', color='#1e293b', transform=ax.transAxes)
chart_ph = patches.Rectangle((0.06, 0.25), 0.48, 0.31, facecolor='#eff6ff', edgecolor='#93c5fd', linestyle='--', linewidth=1, transform=ax.transAxes)
ax.add_patch(chart_ph)
ax.text(0.30, 0.40, "[ Headless Matplotlib Agg Base64 Embedded Plot ]\nDaily Revenue Time Series with Area Fill & Date Ticks", 
        fontsize=6.8, ha='center', va='center', color='#1e40af', transform=ax.transAxes)

# Right Card: Latest Forecast Summary
card_fc = patches.FancyBboxPatch((0.60, 0.22), 0.36, 0.42, boxstyle="round,pad=0.015", fc="#ffffff", ec="#e2e8f0", lw=1.2, transform=ax.transAxes)
ax.add_patch(card_fc)
ax.text(0.62, 0.59, "Latest Forecast Summary", fontsize=8, fontweight='bold', color='#1e293b', transform=ax.transAxes)
ax.text(0.62, 0.53, "Algorithm: Linear Regression & Moving Average\nHorizon: 14 Periods • Interval: Daily\nProjected 14-Day Revenue: $20,845.20\nExpected Daily Average: $1,488.94", 
        fontsize=6.8, color='#334155', transform=ax.transAxes)
table_ph = patches.Rectangle((0.62, 0.25), 0.32, 0.22, facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1, transform=ax.transAxes)
ax.add_patch(table_ph)
ax.text(0.78, 0.36, "[ Predicted Values Table Preview ]\nPeriod #1 to #5 Revenue Breakdown", fontsize=6.5, ha='center', va='center', color='#475569', transform=ax.transAxes)

# Bottom Storage Card: Dual-Engine Status & Controls
card_db = patches.FancyBboxPatch((0.04, 0.04), 0.92, 0.15, boxstyle="round,pad=0.015", fc="#ffffff", ec="#e2e8f0", lw=1.2, transform=ax.transAxes)
ax.add_patch(card_db)
ax.text(0.06, 0.13, "Storage & Persistence Integration (MySQL & CSV Dual Engine)", fontsize=7.5, fontweight='bold', color='#1e293b', transform=ax.transAxes)
ax.text(0.06, 0.075, "Active Source: Sample Dataset (Retail Sales) • 616 records loaded in-memory • Zero configuration mode active.", fontsize=6.5, color='#64748b', transform=ax.transAxes)
ax.text(0.94, 0.10, "[ Init DB ]  [ Push to MySQL ]  [ Load MySQL ]  [ Reset ]", fontsize=6.8, ha='right', color='#2563eb', fontweight='bold', transform=ax.transAxes)

plt.tight_layout()
fig.savefig('docs/images/ui_dashboard_layout.png')
plt.close(fig)

# -------------------------------------------------------------
# 2. UI Layout Figure: Forecasting & Evaluation Screen Mockup
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 4.0), dpi=160)
ax.axis('off')

# Background
bg2 = patches.Rectangle((0, 0), 1, 1, facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.5, transform=ax.transAxes)
ax.add_patch(bg2)

# Top Bar
header2 = patches.Rectangle((0, 0.88), 1, 0.12, facecolor='#1e293b', edgecolor='none', transform=ax.transAxes)
ax.add_patch(header2)
ax.text(0.04, 0.94, "Forecast Model Evaluation & Accuracy Benchmarking", color='#ffffff', fontsize=9, fontweight='bold', transform=ax.transAxes)
ax.text(0.96, 0.94, "Validation Strategy: Chronological Holdout Split (80% Train / 20% Test)", color='#cbd5e1', fontsize=7.2, ha='right', transform=ax.transAxes)

# Left Metrics Card: Moving Average
card_ma = patches.FancyBboxPatch((0.04, 0.54), 0.44, 0.30, boxstyle="round,pad=0.015", fc="#fffbeb", ec="#fde68a", lw=1.5, transform=ax.transAxes)
ax.add_patch(card_ma)
ax.text(0.06, 0.77, "Baseline: Simple Moving Average (7-Period Window)", fontsize=8, fontweight='bold', color='#92400e', transform=ax.transAxes)
ax.text(0.06, 0.65, "Mean Absolute Error (MAE) : $153.22\nRoot Mean Squared (RMSE)   : $184.60\nMean Abs Percentage (MAPE) : 11.45%", fontsize=7.5, fontfamily='monospace', color='#78350f', transform=ax.transAxes)

# Right Metrics Card: Linear Regression
card_lr = patches.FancyBboxPatch((0.52, 0.54), 0.44, 0.30, boxstyle="round,pad=0.015", fc="#ecfdf5", ec="#a7f3d0", lw=1.5, transform=ax.transAxes)
ax.add_patch(card_lr)
ax.text(0.54, 0.77, "Advanced: Scikit-Learn Linear Regression (Trend Model)", fontsize=8, fontweight='bold', color='#065f46', transform=ax.transAxes)
ax.text(0.54, 0.65, "Mean Absolute Error (MAE) : $141.80\nRoot Mean Squared (RMSE)   : $172.15\nMean Abs Percentage (MAPE) : 10.22%", fontsize=7.5, fontfamily='monospace', color='#064e3b', transform=ax.transAxes)

# Verdict Banner
verdict = patches.FancyBboxPatch((0.04, 0.40), 0.92, 0.11, boxstyle="round,pad=0.015", fc="#eff6ff", ec="#3b82f6", lw=1.5, transform=ax.transAxes)
ax.add_patch(verdict)
ax.text(0.06, 0.455, "Evaluation Verdict: Winner - Linear Regression (Lower MAE by $11.42)", fontsize=7.8, fontweight='bold', color='#1e40af', transform=ax.transAxes)
ax.text(0.06, 0.415, "Linear Regression effectively captured the underlying secular upward sales trajectory across the 270-day window.", fontsize=6.5, color='#1e3a8a', transform=ax.transAxes)

# Bottom Chart Placeholder
chart_eval_ph = patches.FancyBboxPatch((0.04, 0.05), 0.92, 0.32, boxstyle="round,pad=0.015", fc="#ffffff", ec="#e2e8f0", lw=1.2, transform=ax.transAxes)
ax.add_patch(chart_eval_ph)
ax.text(0.06, 0.31, "Chronological Holdout Evaluation Chart & Error Decomposition Table", fontsize=7.5, fontweight='bold', color='#334155', transform=ax.transAxes)
inner_c = patches.Rectangle((0.06, 0.08), 0.88, 0.20, facecolor='#f8fafc', edgecolor='#cbd5e1', linestyle='--', linewidth=1, transform=ax.transAxes)
ax.add_patch(inner_c)
ax.text(0.50, 0.18, "[ Embedded Visualization: Training Period (216 pts) | Split Line | Actual Test Window (54 pts) | Model Predictions ]\nFollowed by Tabular Record-by-Record Error Analysis Table (Date, Actual, Pred, Error)", 
        fontsize=6.8, ha='center', va='center', color='#475569', transform=ax.transAxes)

plt.tight_layout()
fig.savefig('docs/images/ui_evaluation_layout.png')
plt.close(fig)

print("Generated ui_dashboard_layout.png and ui_evaluation_layout.png successfully in docs/images/")
