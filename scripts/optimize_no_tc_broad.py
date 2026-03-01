import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def optimize_no_tc_broad():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    leverage = 30
    margin_pct = 0.1
    sl = 0.01

    results = []

    # Sweep sensitivities 1 to 30
    # Sweep filters
    # Sweep TP
    for s in [1, 5, 10, 15, 20]:
        print(f"Testing sensitivity {s}...", file=sys.stderr)
        for el in [0, 200, 500]:
            for rsi in [False, True]:
                for tp in [0.03, 0.05, 0.1]:
                    signals = imba_algo_trend_filtered(df_1h, sensitivity=s,
                                                      ema_filter=(el > 0), ema_len=el,
                                                      rsi_filter=rsi, trend_confirmation=False)
                    bt = Backtester(leverage=leverage)
                    res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
                    if res['n_trades'] >= 10:
                        results.append({'sens': s, 'el': el, 'rsi': rsi, 'tp': tp, 'res': res})

    results.sort(key=lambda x: x['res']['sharpe_ratio'], reverse=True)

    print("\nTOP NO-TC RESULTS (BROAD SWEEP)")
    print("="*60)
    for i, item in enumerate(results[:20]):
        r = item['res']
        print(f"{i+1}. Sens: {item['sens']} | EMA: {item['el']} | RSI: {item['rsi']} | TP: {item['tp']:.0%}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']:.2%} | MDD: {r['max_drawdown_pct']:.2f}%")
        print(f"   Sharpe: {r['sharpe_ratio']:.4f} | Trades: {r['n_trades']}")
        print("-" * 50)

if __name__ == "__main__":
    optimize_no_tc_broad()
