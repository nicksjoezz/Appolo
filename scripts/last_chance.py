import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def last_chance_optimize():
    df_15m = pd.read_csv('data/ROSEUSDT_15m.csv', index_col='timestamp', parse_dates=True)
    leverage = 30
    margin_pct = 0.1
    sl = 0.01
    sensitivity = 18

    results = []

    print("Testing 15m Timeframe (No TC)...", file=sys.stderr)
    for el in [0, 200, 500]:
        for tp in [0.03, 0.05, 0.1]:
            signals = imba_algo_trend_filtered(df_15m, sensitivity=sensitivity,
                                              ema_filter=(el > 0), ema_len=el,
                                              trend_confirmation=False)
            bt = Backtester(leverage=leverage)
            res = bt.run_backtest(df_15m, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
            if res['n_trades'] >= 10:
                results.append({'el': el, 'tp': tp, 'res': res})

    results.sort(key=lambda x: x['res']['total_return_pct'], reverse=True)

    print("\nTOP 15M NO-TC RESULTS (SENS 18)")
    print("="*60)
    for i, item in enumerate(results[:10]):
        r = item['res']
        print(f"{i+1}. EMA: {item['el']} | TP: {item['tp']:.0%}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']:.2%} | MDD: {r['max_drawdown_pct']:.2f}%")
        print("-" * 50)

if __name__ == "__main__":
    last_chance_optimize()
