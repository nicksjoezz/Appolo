import pandas as pd
import numpy as np
import os
from backtester import Backtester
from strategies import *
import sys

def deep_optimize():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)
    df_15m = pd.read_csv('data/ROSEUSDT_15m.csv', index_col='timestamp', parse_dates=True)

    results = []
    # Test only 15m for speed
    timeframes = [('15m', df_15m)]

    # Grid: vary margin risk
    margin_ranges = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    # Best aggressive candidates
    strategies = [
        ('RSI_BB', lambda df: rsi_bb_strategy(df, 14, 80, 20), 0.1, 0.03),
        ('Supertrend', lambda df: supertrend_strategy(df, 7, 3), 0.1, 0.02)
    ]

    for tf_name, df in timeframes:
        for name, strat_func, tp, sl in strategies:
            signals = strat_func(df)
            for mgn in margin_ranges:
                bt = Backtester(leverage=30)
                res = bt.run_backtest(df, signals, tp_pct=tp, sl_pct=sl, margin_pct=mgn)
                if res['final_balance'] > 0:
                    results.append({'strategy': name, 'tf': tf_name, 'tp': tp, 'sl': sl, 'mgn': mgn, 'res': res})

    results.sort(key=lambda x: x['res']['total_return_pct'], reverse=True)

    print("\n\nPROFITABILITY VS RISK (MARGIN %)")
    for i, item in enumerate(results[:10]):
        r = item['res']
        print(f"{i+1}. {item['strategy']} {item['tf']} | Margin: {item['mgn']*100}% | Return: {r['total_return_pct']:.2f}% | MDD: {r['max_drawdown_pct']:.2f}%")

if __name__ == "__main__":
    deep_optimize()
