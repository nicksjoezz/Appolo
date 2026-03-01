import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def final_aggressive_sweep():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)
    sensitivity = 18
    margin_pct = 0.1
    sl = 0.01
    leverage = 30

    results = []

    # Best Filters from previous step
    # 1. EMA 300 + TC
    # 2. EMA 200 + TC

    filters = [
        {'name': 'EMA_300_TC', 'el': 300, 'tc': True},
        {'name': 'EMA_200_TC', 'el': 200, 'tc': True}
    ]

    tp_ranges = [0.05, 0.08, 0.10, 0.15, 0.20, 0.30]

    print("Final Aggressive Realistic Sweep...", file=sys.stderr)
    for f in filters:
        signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity,
                                          ema_filter=True, ema_len=f['el'],
                                          trend_confirmation=f['tc'])
        for tp in tp_ranges:
            bt = Backtester(leverage=leverage)
            res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
            if res['n_trades'] >= 5:
                results.append({'filter': f['name'], 'tp': tp, 'res': res})

    results.sort(key=lambda x: x['res']['total_return_pct'], reverse=True)

    print("\nTOP RESULTS (SENS 18, FILTERED, REALISTIC)")
    print("="*60)
    for i, item in enumerate(results[:10]):
        r = item['res']
        print(f"{i+1}. Filter: {item['filter']} | TP: {item['tp']:.0%}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']:.2%} | MDD: {r['max_drawdown_pct']:.2f}%")
        print("-" * 50)

if __name__ == "__main__":
    final_aggressive_sweep()
