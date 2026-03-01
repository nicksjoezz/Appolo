import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def optimize_filtered_longterm():
    df_1h = pd.read_csv('data/ROSEUSDT_1h_3y.csv', index_col='timestamp', parse_dates=True)

    leverage = 30
    margin_pct = 0.1
    # User is open to < 3% SL. Let's test 1% and 2%.
    # TP 5% to 10%

    sensitivity = 20
    results = []

    print("Long-term Filtered Optimization (Sens 20, 3y data)...", file=sys.stderr)

    # 1. Baseline
    signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity)
    bt = Backtester(leverage=leverage)
    res = bt.run_backtest(df_1h, signals, tp_pct=0.05, sl_pct=0.01)
    results.append({'name': 'Baseline_5_1', 'res': res})

    # 2. Optimized Filter Set
    # We'll test different filters
    filter_configs = [
        {'name': 'ADX_DMI', 'params': {'adx_filter': True, 'dmi_filter': True}},
        {'name': 'EMA500_DMI', 'params': {'ema_filter': True, 'ema_len': 500, 'dmi_filter': True}},
        {'name': 'EMA500_ADX_DMI', 'params': {'ema_filter': True, 'ema_len': 500, 'adx_filter': True, 'dmi_filter': True}}
    ]

    for fc in filter_configs:
        for tp in [0.05, 0.10]:
            for sl in [0.01, 0.02]:
                signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity, **fc['params'])
                bt = Backtester(leverage=leverage)
                res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
                results.append({'name': f"{fc['name']}_TP{int(tp*100)}_SL{int(sl*100)}", 'res': res})

    summary = []
    for r in results:
        m = r['res']
        summary.append({
            'Config': r['name'],
            'ROI %': m['total_return_pct'],
            'Win Rate %': m['win_rate'] * 100,
            'MDD %': m['max_drawdown_pct'],
            'Sharpe': m['sharpe_ratio'],
            'Trades': m['n_trades']
        })

    summary_df = pd.DataFrame(summary).sort_values(by='ROI %', ascending=False)
    print("\nLONG-TERM FILTERED RESULTS (3 YEARS)")
    print("="*60)
    print(summary_df.to_string(index=False))

if __name__ == "__main__":
    optimize_filtered_longterm()
