import pandas as pd
import numpy as np
from mtf_backtester import MTFBacktester
from strategies import imba_ut_bot_strategy
import sys

def optimize_imba_ut():
    df_1h = pd.read_csv('data/ROSEUSDT_1h_3y.csv', index_col='timestamp', parse_dates=True)
    leverage = 30
    margin_pct = 0.1
    sensitivity = 20
    results = []

    # Target smaller grid for speed
    for key_val in [1, 3, 5]:
        print(f"Testing UT Key {key_val}...", file=sys.stderr)
        for atr_per in [10, 20]:
            signals, ut_raw = imba_ut_bot_strategy(df_1h, imba_sens=sensitivity, ut_key=key_val, ut_atr=atr_per)
            for tp in [0.05, 0.1]:
                bt = MTFBacktester(leverage=leverage)
                res = bt.run_backtest(df_1h, signals, df_1h, tp_pct=tp, sl_pct=0.01, margin_pct=margin_pct, exit_signals=ut_raw)
                if res['n_trades'] >= 5:
                    results.append({'key': key_val, 'atr': atr_per, 'tp': tp, 'res': res})

    results.sort(key=lambda x: x['res']['total_return_pct'], reverse=True)

    print("\nTOP IMBA + UT BOT RESULTS")
    print("="*60)
    for i, item in enumerate(results[:10]):
        r = item['res']
        print(f"{i+1}. UT Key: {item['key']} | UT ATR: {item['atr']} | TP: {item['tp']:.0%}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']:.2%} | Best 60d: {r['best_60d_roi']:.2f}%")
        print("-" * 50)

if __name__ == "__main__":
    optimize_imba_ut()
