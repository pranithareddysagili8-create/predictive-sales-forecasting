"""
Forecast Evaluation Module
Performs time-ordered holdout validation (chronological split), computes MAE, RMSE, and MAPE,
and compares Moving Average vs Linear Regression with beginner-friendly explanations.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from src.forecasting import plot_to_base64


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    Calculates MAE, RMSE, and MAPE.
    
    MAE: Mean Absolute Error (average magnitude of errors)
    RMSE: Root Mean Squared Error (penalizes larger errors more heavily)
    MAPE: Mean Absolute Percentage Error (relative error in percentage)
    """
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)

    # MAE = mean(|y_true - y_pred|)
    mae = float(np.mean(np.abs(y_true - y_pred)))

    # RMSE = sqrt(mean((y_true - y_pred)^2))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

    # MAPE = mean(|(y_true - y_pred) / y_true|) * 100 (ignoring zero true values)
    non_zero_mask = (y_true > 0)
    if np.sum(non_zero_mask) > 0:
        mape = float(np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100)
    else:
        mape = 0.0

    return {
        'mae': round(mae, 2),
        'rmse': round(rmse, 2),
        'mape': round(mape, 2)
    }


def evaluate_models(df_agg: pd.DataFrame, train_ratio: float = 0.8, window: int = 7) -> dict:
    """
    Performs time-ordered holdout evaluation on aggregated sales data.
    
    Args:
        df_agg: DataFrame with columns 'date_str' and 'revenue'.
        train_ratio: Fraction of historical data for training (e.g. 0.8 for 80%).
        window: Moving average window size.
        
    Returns:
        dict containing metrics, predictions, train/test subsets, and interpretation.
    """
    n = len(df_agg)
    min_required = max(10, window + 3)
    if n < min_required:
        return {
            'success': False,
            'message': f"Insufficient data for reliable evaluation. Dataset has {n} points, but at least {min_required} points are required."
        }

    # Chronological Split (NEVER SHUFFLE)
    split_idx = int(n * train_ratio)
    if split_idx < window:
        split_idx = window

    test_len = n - split_idx
    if test_len < 2:
        return {
            'success': False,
            'message': "Test set is too small. Please ensure dataset has enough historical records."
        }

    train_df = df_agg.iloc[:split_idx].copy()
    test_df = df_agg.iloc[split_idx:].copy()

    y_train = train_df['revenue'].to_numpy(dtype=float)
    y_test = test_df['revenue'].to_numpy(dtype=float)

    # 1. Moving Average Holdout Evaluation (Multi-step or rolling on train history)
    ma_history = list(y_train)
    ma_preds = []
    for actual_val in y_test:
        pred = float(np.mean(ma_history[-window:]))
        pred = max(0.0, round(pred, 2))
        ma_preds.append(pred)
        # Advance rolling window with the true observation (1-step ahead rolling forecast)
        ma_history.append(actual_val)

    ma_metrics = calculate_metrics(y_test, ma_preds)

    # 2. Linear Regression Holdout Evaluation
    X_train = np.arange(len(y_train)).reshape(-1, 1)
    lr = LinearRegression()
    lr.fit(X_train, y_train)

    X_test = np.arange(len(y_train), len(y_train) + len(y_test)).reshape(-1, 1)
    lr_preds = lr.predict(X_test)
    lr_preds = np.clip(lr_preds, 0, None)
    lr_preds = [round(float(v), 2) for v in lr_preds]

    lr_metrics = calculate_metrics(y_test, lr_preds)

    # Determine better model
    if ma_metrics['mae'] < lr_metrics['mae']:
        winner = "Moving Average"
        diff_mae = round(lr_metrics['mae'] - ma_metrics['mae'], 2)
        win_reason = f"Moving Average achieved a lower MAE by ${diff_mae:,.2f}, responding better to recent local demand variations."
    elif lr_metrics['mae'] < ma_metrics['mae']:
        winner = "Linear Regression"
        diff_mae = round(ma_metrics['mae'] - lr_metrics['mae'], 2)
        win_reason = f"Linear Regression achieved a lower MAE by ${diff_mae:,.2f}, effectively capturing the overall upward or downward sales trajectory."
    else:
        winner = "Tie"
        win_reason = "Both models achieved identical Mean Absolute Error on this test holdout period."

    # Generate Comparison Visualization
    chart_b64 = generate_evaluation_chart(
        df_agg=df_agg,
        split_idx=split_idx,
        y_test=y_test,
        ma_preds=ma_preds,
        lr_preds=lr_preds,
        window=window
    )

    # Prepare table rows for template display
    test_rows = []
    for i in range(len(test_df)):
        test_rows.append({
            'date': test_df['date_str'].iloc[i],
            'actual': round(float(y_test[i]), 2),
            'ma_pred': round(float(ma_preds[i]), 2),
            'lr_pred': round(float(lr_preds[i]), 2),
            'ma_error': round(abs(float(y_test[i]) - float(ma_preds[i])), 2),
            'lr_error': round(abs(float(y_test[i]) - float(lr_preds[i])), 2)
        })

    return {
        'success': True,
        'train_count': len(train_df),
        'test_count': len(test_df),
        'split_ratio': int(train_ratio * 100),
        'window': window,
        'ma_metrics': ma_metrics,
        'lr_metrics': lr_metrics,
        'winner': winner,
        'win_reason': win_reason,
        'chart_b64': chart_b64,
        'test_rows': test_rows
    }


def generate_evaluation_chart(df_agg: pd.DataFrame, split_idx: int, y_test: np.ndarray, 
                              ma_preds: list, lr_preds: list, window: int) -> str:
    """
    Renders the holdout evaluation chart comparing Train, Test, and predictions.
    """
    fig, ax = plt.subplots(figsize=(11, 5.2))
    
    n = len(df_agg)
    x_all = list(range(n))
    labels_all = df_agg['date_str'].tolist()

    # Train actual
    ax.plot(x_all[:split_idx], df_agg['revenue'].iloc[:split_idx], 
            label=f'Training Period ({split_idx} observations)', color='#6b7280', linewidth=1.8, alpha=0.7)

    # Test actual
    ax.plot(x_all[split_idx:], y_test, 
            label=f'Actual Test Period ({len(y_test)} observations)', color='#1e3a8a', linewidth=2.5, marker='o', markersize=4)

    # MA Predictions
    ax.plot(x_all[split_idx:], ma_preds, 
            label=f'MA ({window}-period) Predicted', color='#d97706', linestyle='--', linewidth=2.0)

    # LR Predictions
    ax.plot(x_all[split_idx:], lr_preds, 
            label='Linear Regression Predicted', color='#059669', linestyle=':', linewidth=2.0)

    # Train / Test split line & background
    ax.axvline(split_idx - 0.5, color='#ef4444', linestyle='-', linewidth=1.5, label='Train / Test Split')
    ax.axvspan(split_idx - 0.5, n - 0.5, color='#dbeafe', alpha=0.3, label='Holdout Test Window')

    step = max(1, n // 10)
    tick_indices = list(range(0, n, step))
    if (n - 1) not in tick_indices:
        tick_indices.append(n - 1)
        
    ax.set_xticks(tick_indices)
    ax.set_xticklabels([labels_all[i] for i in tick_indices], rotation=35, ha='right', fontsize=9)

    ax.set_title("Chronological Holdout Model Evaluation: Actual vs Predicted", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Timeline", fontsize=11, labelpad=8)
    ax.set_ylabel("Revenue ($)", fontsize=11, labelpad=8)
    ax.yaxis.set_major_formatter('${x:,.0f}')
    ax.grid(True, linestyle='--', alpha=0.45)
    ax.legend(loc='upper left', frameon=True, framealpha=0.92)

    plt.tight_layout()
    return plot_to_base64(fig)
