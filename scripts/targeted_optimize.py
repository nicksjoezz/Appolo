import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend
import sys

def optimize_broad():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    sensitivities = range(1, 41)
    # Testing combinations that might result in better drawdown
    tp_ranges = [0.03, 0.05, 0.08, 0.1, 0.15]
    sl_ranges = [0.01, 0.02, 0.03, 0.05]

    leverage = 30
    margin_pct = 0.1

    results = []

    for s in sensitivities:
        signals = imba_algo_trend(df_1h, sensitivity=s)
        for tp in tp_ranges:
            for sl in sl_ranges:
                bt = Backtester(leverage=leverage)
                res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
                if res['n_trades'] >= 10:
                    results.append({'sens': s, 'tp': tp, 'sl': sl, 'res': res})

    # Filter: Any Win Rate > 45% and ROI > 100%
    filtered = [r for r in results if r['res']['win_rate'] >= 0.45 and r['res']['total_return_pct'] > 100]

    # Sort by MDD (asc)
    filtered.sort(key=lambda x: abs(x['res']['max_drawdown_pct']))

    print("\nTOP RESULTS BY DRAWDOWN (WinRate > 45%, ROI > 100%)")
    print("="*60)
    for i, item in enumerate(filtered[:20]):
        r = item['res']
        print(f"{i+1}. Sens: {item['sens']} | TP: {item['tp']:.2%} | SL: {item['sl']:.2%}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']:.2%} | MDD: {r['max_drawdown_pct']:.2f}%")
        print(f"   Sharpe: {r['sharpe_ratio']:.4f} | Trades: {r['n_trades']}")
        print("-" * 50)

if __name__ == "__main__":
    optimize_broad()
