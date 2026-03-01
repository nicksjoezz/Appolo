import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def find_imba_roi():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)
    leverage = 30
    sl = 0.01
    tp = 0.05
    margin_pct = 0.1

    results = []

    # Sweep only sensitivities
    for s in [1, 5, 10, 15, 18, 20, 25, 30]:
        signals = imba_algo_trend_filtered(df_1h, sensitivity=s, ema_filter=False)
        bt = Backtester(leverage=leverage)
        res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
        results.append({'s': s, 'res': res})

    results.sort(key=lambda x: x['res']['total_return_pct'], reverse=True)

    print("\nIMBA ONLY RESULTS (REALISTIC)")
    print("="*60)
    for r in results:
        m = r['res']
        print(f"Sens: {r['s']} | ROI: {m['total_return_pct']:.2f}% | Win Rate: {m['win_rate']:.2%}")

if __name__ == "__main__":
    find_imba_roi()
