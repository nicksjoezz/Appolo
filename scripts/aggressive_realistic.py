import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def optimize_aggressive_realistic():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    # User likes Sensitivity 18
    sensitivity = 18
    leverage = 30
    margin_pct = 0.1

    # Wide sweep for TP and SL to find high ROI realistically
    # Note: SL > 3.33% with 30x leverage is liquidation, so we keep SL tight.
    # But maybe 1% is TOO tight and we get stopped by noise.
    # 2% SL is 60% margin loss, but might stay in trades longer.
    tp_ranges = [0.05, 0.1, 0.15, 0.2, 0.3]
    sl_ranges = [0.01, 0.015, 0.02]

    results = []

    print(f"Aggressive Realistic Sweep (Sens 18)...", file=sys.stderr)
    signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity, ema_filter=False)

    for tp in tp_ranges:
        for sl in sl_ranges:
            bt = Backtester(leverage=leverage)
            res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
            if res['n_trades'] >= 5:
                results.append({'tp': tp, 'sl': sl, 'res': res})

    results.sort(key=lambda x: x['res']['total_return_pct'], reverse=True)

    print("\nTOP REALISTIC AGGRESSIVE RESULTS (Sens 18)")
    print("="*60)
    for i, item in enumerate(results[:10]):
        r = item['res']
        print(f"{i+1}. TP: {item['tp']:.2%} | SL: {item['sl']:.2%}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']:.2%} | MDD: {r['max_drawdown_pct']:.2f}%")
        print(f"   Sharpe: {r['sharpe_ratio']:.4f} | Trades: {r['n_trades']}")
        print("-" * 50)

if __name__ == "__main__":
    optimize_aggressive_realistic()
