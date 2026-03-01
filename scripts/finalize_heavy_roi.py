import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered

def finalize():
    df_1h = pd.read_csv('data/ROSEUSDT_1h_3y.csv', index_col='timestamp', parse_dates=True)

    # BEST HEAVY ROI STRATEGY: Sens 20, EMA 200, TC, DMI Filter, TP 5%, SL 4%
    # This survived 3 years with 15,676% ROI and 57.67% Win Rate

    sensitivity = 20
    tp = 0.05
    sl = 0.04
    leverage = 30
    margin_pct = 0.1

    print("FINALIZING ABSOLUTE BEST HEAVY ROI STRATEGY (3-YEAR BACKTEST)...")

    signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity,
                                      ema_filter=True, ema_len=200,
                                      trend_confirmation=True,
                                      dmi_filter=True)

    bt = Backtester(leverage=leverage)
    res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)

    print("\nHEAVY ROI STRATEGY RESULTS")
    print("="*30)
    print(f"Total ROI: {res['total_return_pct']:.2f}%")
    print(f"Win Rate: {res['win_rate']:.2%}")
    print(f"Max Drawdown: {res['max_drawdown_pct']:.2f}%")
    print(f"Sharpe Ratio: {res['sharpe_ratio']:.4f}")
    print(f"Total Trades: {res['n_trades']}")

    res['trades'].to_csv('final_heavy_roi_log.csv')
    pd.DataFrame({'equity': res['equity_curve']}, index=df_1h.index).to_csv('final_heavy_roi_equity.csv')

if __name__ == "__main__":
    finalize()
