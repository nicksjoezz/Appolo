import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import *
import sys

def master_optimize():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    leverage = 30
    margin_pct = 0.1
    sl = 0.01
    tp_ranges = [0.03, 0.05, 0.08, 0.1, 0.15]
    sensitivity = 18

    results = []

    # Filter combinations
    filters = [
        {'name': 'Baseline', 'params': {'ema_filter': False, 'rsi_filter': False, 'macd_filter': False, 'trend_confirmation': False, 'vol_filter': False}},
        {'name': 'EMA_300', 'params': {'ema_filter': True, 'ema_len': 300, 'rsi_filter': False, 'macd_filter': False, 'trend_confirmation': False, 'vol_filter': False}},
        {'name': 'TC_Only', 'params': {'ema_filter': False, 'rsi_filter': False, 'macd_filter': False, 'trend_confirmation': True, 'vol_filter': False}},
        {'name': 'EMA_300_TC', 'params': {'ema_filter': True, 'ema_len': 300, 'rsi_filter': False, 'macd_filter': False, 'trend_confirmation': True, 'vol_filter': False}},
        {'name': 'EMA_200_MACD', 'params': {'ema_filter': True, 'ema_len': 200, 'rsi_filter': False, 'macd_filter': True, 'trend_confirmation': False, 'vol_filter': False}},
    ]

    for f in filters:
        for tp in tp_ranges:
            signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity, **f['params'])
            bt = Backtester(leverage=leverage)
            res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
            if res['n_trades'] >= 5:
                results.append({
                    'Strategy': f['name'],
                    'TP %': tp * 100,
                    'ROI %': res['total_return_pct'],
                    'Win Rate %': res['win_rate'] * 100,
                    'MDD %': res['max_drawdown_pct'],
                    'Sharpe': res['sharpe_ratio'],
                    'Trades': res['n_trades']
                })

    summary_df = pd.DataFrame(results)
    summary_df.sort_values(by='ROI %', ascending=False, inplace=True)
    summary_df.to_csv('detailed_strategies_summary.csv', index=False)

    print("\nDETAILED STRATEGIES RESULTS")
    print(summary_df.to_string(index=False))

if __name__ == "__main__":
    master_optimize()
