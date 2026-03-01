import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def finalize():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    # Best filtered configuration found for Sens 18
    # EMA: 300 | TC: True | MACD: True

    sensitivity = 18
    tp = 0.05
    sl = 0.01
    leverage = 30
    margin_pct = 0.1

    print("FINAL SELECTION: OPTIMIZED FILTERED IMBA (Sensitivity 18, TP 5%, SL 1%)")
    print("="*60)

    signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity,
                                      ema_filter=True, ema_len=300,
                                      macd_filter=True,
                                      trend_confirmation=True)

    bt = Backtester(leverage=leverage)
    res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)

    print(f"Filter: EMA_300 + MACD + Trend Confirmation")
    print(f"ROI: {res['total_return_pct']:.2f}% | Win Rate: {res['win_rate']:.2%} | MDD: {res['max_drawdown_pct']:.2f}%")
    print(f"Sharpe: {res['sharpe_ratio']:.4f} | Trades: {res['n_trades']}")
    print("-" * 50)

    res['trades'].to_csv('final_imba_filtered_realistic_log.csv')
    equity_df = pd.DataFrame({'equity': res['equity_curve']}, index=df_1h.index)
    equity_df.to_csv('final_imba_filtered_realistic_equity.csv')

if __name__ == "__main__":
    finalize()
