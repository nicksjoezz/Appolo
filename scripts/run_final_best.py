import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered

def run_final():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    # Configuration for the Best Realistic ROI Strategy
    sensitivity = 18
    tp = 0.20 # 20% TP for High ROI
    sl = 0.01 # 1% SL
    leverage = 30
    margin_pct = 0.1

    print("Running FINAL BEST REALISTIC strategy (SENS 18, EMA 300, TC)...")

    signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity,
                                      ema_filter=True, ema_len=300,
                                      trend_confirmation=True)

    bt = Backtester(leverage=leverage)
    res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)

    print("\nFINAL RESULTS")
    print("="*30)
    print(f"ROI: {res['total_return_pct']:.2f}%")
    print(f"Win Rate: {res['win_rate']:.2%}")
    print(f"Max Drawdown: {res['max_drawdown_pct']:.2f}%")
    print(f"Sharpe Ratio: {res['sharpe_ratio']:.4f}")
    print(f"Total Trades: {res['n_trades']}")

    res['trades'].to_csv('final_best_trade_log.csv')
    equity_df = pd.DataFrame({'equity': res['equity_curve']}, index=df_1h.index)
    equity_df.to_csv('final_best_equity_curve.csv')
    print("\nLogs saved to final_best_trade_log.csv and final_best_equity_curve.csv")

if __name__ == "__main__":
    run_final()
