import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def finalize_no_tc():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)
    leverage = 30
    margin_pct = 0.1
    sl = 0.01

    # Best no-TC found: Sens 15, EMA 500, RSI True, TP 10%
    # or Sens 18, EMA 500, RSI True, TP 5%

    configs = [
        {'name': 'IMBA_15_EMA500_RSI', 's': 15, 'tp': 0.10, 'el': 500, 'rsi': True},
        {'name': 'IMBA_18_EMA500_RSI', 's': 18, 'tp': 0.05, 'el': 500, 'rsi': True},
        {'name': 'IMBA_1_EMA500_RSI', 's': 1, 'tp': 0.10, 'el': 500, 'rsi': True}
    ]

    print("FINAL SELECTION: NO-TC OPTIMIZED IMBA (1% SL)")
    print("="*60)

    for c in configs:
        signals = imba_algo_trend_filtered(df_1h, sensitivity=c['s'],
                                          ema_filter=True, ema_len=c['el'],
                                          rsi_filter=c['rsi'], trend_confirmation=False)
        bt = Backtester(leverage=leverage)
        res = bt.run_backtest(df_1h, signals, tp_pct=c['tp'], sl_pct=sl, margin_pct=margin_pct)

        print(f"Strategy: {c['name']}")
        print(f"Params: Sens={c['s']}, TP={c['tp']:.0%}, SL={sl:.0%}, Filters=EMA {c['el']} + RSI")
        print(f"ROI: {res['total_return_pct']:.2f}% | Win Rate: {res['win_rate']:.2%} | MDD: {res['max_drawdown_pct']:.2f}%")
        print(f"Sharpe: {res['sharpe_ratio']:.4f} | Trades: {res['n_trades']}")
        print("-" * 50)

        if c['name'] == 'IMBA_15_EMA500_RSI':
            res['trades'].to_csv('final_no_tc_log.csv')
            pd.DataFrame({'equity': res['equity_curve']}, index=df_1h.index).to_csv('final_no_tc_equity.csv')

if __name__ == "__main__":
    finalize_no_tc()
