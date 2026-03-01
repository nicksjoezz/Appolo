import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def optimize_sens18_no_tc():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    sensitivity = 18
    tp = 0.05
    sl = 0.01
    leverage = 30
    margin_pct = 0.1

    results = []

    # Sweep EMA Length
    for el in [50, 100, 200, 300, 400, 500]:
        # Sweep MACD
        for macd in [True, False]:
            # Sweep Vol
            for vol in [True, False]:
                signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity,
                                                  ema_filter=True, ema_len=el,
                                                  macd_filter=macd,
                                                  vol_filter=vol,
                                                  trend_confirmation=False)
                bt = Backtester(leverage=leverage)
                res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
                if res['n_trades'] >= 10:
                    results.append({'el': el, 'macd': macd, 'vol': vol, 'res': res})

    results.sort(key=lambda x: (x['res']['win_rate'], x['res']['sharpe_ratio']), reverse=True)

    print("\nTOP SENS 18 NO-TC RESULTS")
    print("="*60)
    for i, item in enumerate(results[:20]):
        r = item['res']
        print(f"{i+1}. EMA: {item['el']} | MACD: {item['macd']} | VOL: {item['vol']}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']:.2%} | MDD: {r['max_drawdown_pct']:.2f}%")
        print(f"   Sharpe: {r['sharpe_ratio']:.4f} | Trades: {r['n_trades']}")
        print("-" * 50)

if __name__ == "__main__":
    optimize_sens18_no_tc()
