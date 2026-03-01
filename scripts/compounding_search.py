import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def massive_search_compounding():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    sensitivity = 18
    leverage = 30
    sl = 0.01

    results = []

    print("Starting Compounding Search (SENS 18)...", file=sys.stderr)

    # Sweep Margin risk
    for m in [0.2, 0.4, 0.6]:
        # Sweep TP
        for tp in [0.05, 0.1, 0.15]:
            # Sweep Filters
            for el in [0, 500]:
                for rsi in [False, True]:
                    for vol in [False, True]:
                        if el==0 and not rsi and not vol: continue

                        signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity,
                                                          ema_filter=(el>0), ema_len=el,
                                                          rsi_filter=rsi, vol_filter=vol)

                        bt = Backtester(leverage=leverage)
                        res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=m)
                        if res['final_balance'] > 100:
                            results.append({
                                'm': m, 'tp': tp, 'el': el, 'rsi': rsi, 'vol': vol, 'res': res
                            })

    results.sort(key=lambda x: x['res']['total_return_pct'], reverse=True)

    print("\nTOP COMPOUNDING RESULTS (REALISTIC)")
    print("="*60)
    for i, item in enumerate(results[:20]):
        r = item['res']
        print(f"{i+1}. Margin: {item['m']:.0%} | TP: {item['tp']:.0%} | EMA: {item['el']} | RSI: {item['rsi']} | VOL: {item['vol']}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']:.2%} | MDD: {r['max_drawdown_pct']:.2f}%")
        print("-" * 50)

if __name__ == "__main__":
    massive_search_compounding()
