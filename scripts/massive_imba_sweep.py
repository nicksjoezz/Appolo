import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def massive_imba_sweep():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    leverage = 30
    margin_pct = 0.1

    results = []

    print("Massive Realistic IMBA Sweep...", file=sys.stderr)

    # Range of parameters
    sensitivities = range(1, 41)
    tp_ranges = [0.03, 0.05, 0.08, 0.10, 0.15]
    sl_ranges = [0.01, 0.015, 0.02]

    for s in sensitivities:
        signals = imba_algo_trend_filtered(df_1h, sensitivity=s, ema_filter=False, trend_confirmation=False)
        for tp in tp_ranges:
            for sl in sl_ranges:
                bt = Backtester(leverage=leverage)
                res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
                if res['n_trades'] >= 10:
                    results.append({'s': s, 'tp': tp, 'sl': sl, 'res': res})

    results.sort(key=lambda x: x['res']['total_return_pct'], reverse=True)

    print("\nTOP 20 REALISTIC IMBA-ONLY RESULTS")
    print("="*60)
    for i, item in enumerate(results[:20]):
        r = item['res']
        print(f"{i+1}. Sens: {item['s']} | TP: {item['tp']:.0%} | SL: {item['sl']:.1%}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']:.2%} | MDD: {r['max_drawdown_pct']:.2f}%")
        print("-" * 50)

if __name__ == "__main__":
    massive_imba_sweep()
