import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def optimize_sens18_deep_no_tc():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)
    leverage = 30
    margin_pct = 0.1
    sl = 0.01
    tp = 0.05
    sensitivity = 18

    results = []

    # Try different combinations of filters without TC
    for el in [0, 200, 500]:
        for rsi in [False, True]:
            for macd in [False, True]:
                for vol in [False, True]:
                    signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity,
                                                      ema_filter=(el > 0), ema_len=el,
                                                      rsi_filter=rsi,
                                                      macd_filter=macd,
                                                      vol_filter=vol,
                                                      trend_confirmation=False)
                    bt = Backtester(leverage=leverage)
                    res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
                    if res['n_trades'] >= 5:
                        results.append({'el': el, 'rsi': rsi, 'macd': macd, 'vol': vol, 'res': res})

    results.sort(key=lambda x: x['res']['total_return_pct'], reverse=True)

    print("\nTOP SENS 18 DEEP NO-TC RESULTS")
    print("="*60)
    for i, item in enumerate(results[:20]):
        r = item['res']
        print(f"{i+1}. EMA: {item['el']} | RSI: {item['rsi']} | MACD: {item['macd']} | VOL: {item['vol']}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']:.2%} | MDD: {r['max_drawdown_pct']:.2f}%")
        print(f"   Sharpe: {r['sharpe_ratio']:.4f} | Trades: {r['n_trades']}")
        print("-" * 50)

if __name__ == "__main__":
    optimize_sens18_deep_no_tc()
