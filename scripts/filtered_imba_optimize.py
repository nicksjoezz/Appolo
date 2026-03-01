import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def optimize_filtered():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    sensitivity = 18
    tp = 0.05
    sl = 0.01
    leverage = 30
    margin_pct = 0.1

    results = []

    # Combined filters to find high win rate
    # EMA lengths
    ema_lengths = [50, 100, 200, 300]

    for el in ema_lengths:
        for tc in [True, False]:
            for macd in [True, False]:
                signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity,
                                                  ema_filter=True, ema_len=el,
                                                  macd_filter=macd,
                                                  trend_confirmation=tc)
                bt = Backtester(leverage=leverage)
                res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
                if res['n_trades'] >= 5:
                    results.append({'el': el, 'tc': tc, 'macd': macd, 'res': res})

    results.sort(key=lambda x: x['res']['win_rate'], reverse=True)

    print("\nTOP FILTERED CONFIGURATIONS BY WIN RATE (REALISTIC BACKTEST)")
    print("="*60)
    for i, item in enumerate(results[:20]):
        r = item['res']
        print(f"{i+1}. EMA: {item['el']} | TC: {item['tc']} | MACD: {item['macd']}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']:.2%} | MDD: {r['max_drawdown_pct']:.2f}%")
        print(f"   Sharpe: {r['sharpe_ratio']:.4f} | Trades: {r['n_trades']}")
        print("-" * 50)

if __name__ == "__main__":
    optimize_filtered()
