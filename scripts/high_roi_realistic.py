import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def find_high_roi_realistic():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    # Sweep Filters with Sens 18 to recover the 50% ROI realistically
    tp = 0.05
    sl = 0.01
    sensitivity = 18
    margin_pct = 0.1

    results = []

    print(f"Deep Filter Sweep for Sens 18...", file=sys.stderr)

    for el in [50, 100, 200, 300, 500]:
        for tc in [True, False]:
            for macd in [True, False]:
                signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity,
                                                  ema_filter=True, ema_len=el,
                                                  macd_filter=macd, trend_confirmation=tc)
                bt = Backtester(leverage=30)
                res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
                if res['n_trades'] >= 5:
                    results.append({'el': el, 'tc': tc, 'macd': macd, 'res': res})

    results.sort(key=lambda x: x['res']['total_return_pct'], reverse=True)

    print("\nTOP FILTERED RESULTS (Sens 18)")
    print("="*60)
    for i, item in enumerate(results[:15]):
        r = item['res']
        print(f"{i+1}. EMA: {item['el']} | TC: {item['tc']} | MACD: {item['macd']}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']:.2%} | MDD: {r['max_drawdown_pct']:.2f}%")
        print("-" * 50)

if __name__ == "__main__":
    find_high_roi_realistic()
