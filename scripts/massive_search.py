import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def massive_search():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)
    df_15m = pd.read_csv('data/ROSEUSDT_15m.csv', index_col='timestamp', parse_dates=True)

    sensitivity = 18
    leverage = 30
    margin_pct = 0.1
    sl = 0.01

    results = []

    timeframes = [('1h', df_1h), ('15m', df_15m)]

    print("Starting Massive Realistic Search (Sens 18, 30x, 1% SL)...", file=sys.stderr)

    for tf_name, df in timeframes:
        print(f"  Testing {tf_name}...", file=sys.stderr)
        # Filters to combine
        for el in [0, 100, 200, 300, 500]:
            for rsi in [False, True]:
                for macd in [False, True]:
                    for vol in [False, True]:
                        # Skip if all False (we know it's negative)
                        if el==0 and not rsi and not macd and not vol:
                            continue

                        signals = imba_algo_trend_filtered(df, sensitivity=sensitivity,
                                                          ema_filter=(el>0), ema_len=el,
                                                          rsi_filter=rsi, macd_filter=macd,
                                                          vol_filter=vol, trend_confirmation=False)

                        # Test different TP
                        for tp in [0.03, 0.05, 0.10, 0.15, 0.20]:
                            bt = Backtester(leverage=leverage)
                            res = bt.run_backtest(df, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
                            if res['total_return_pct'] > 50: # Looking for high ROI
                                results.append({
                                    'tf': tf_name, 'el': el, 'rsi': rsi, 'macd': macd, 'vol': vol, 'tp': tp, 'res': res
                                })

    results.sort(key=lambda x: x['res']['total_return_pct'], reverse=True)

    print("\nTOP MASSIVE SEARCH RESULTS (REALISTIC)")
    print("="*60)
    for i, item in enumerate(results[:20]):
        r = item['res']
        print(f"{i+1}. {item['tf']} | TP: {item['tp']:.0%} | EMA: {item['el']} | RSI: {item['rsi']} | MACD: {item['macd']} | VOL: {item['vol']}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']:.2%} | MDD: {r['max_drawdown_pct']:.2f}%")
        print("-" * 50)

if __name__ == "__main__":
    massive_search()
