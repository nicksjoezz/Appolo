import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mtf_backtester import MTFBacktester
from strategies import imba_ut_bot_strategy

def finalize_imba_ut():
    data_path_1h = os.path.join(os.path.dirname(__file__), '../data/ROSEUSDT_1h_3y.csv')
    data_path_15m = os.path.join(os.path.dirname(__file__), '../data/ROSEUSDT_15m_3y.csv')

    if not os.path.exists(data_path_1h) or not os.path.exists(data_path_15m):
        print(f"Data not found. Please run scripts/fetch_data.py and fetch_massive_15m.py first.")
        return

    df_1h = pd.read_csv(data_path_1h, index_col='timestamp', parse_dates=True)
    df_15m = pd.read_csv(data_path_15m, index_col='timestamp', parse_dates=True)

    # Winner: Sens 20, UT Key 5, ATR 10, TP 20%, SL 1%
    sensitivity = 20
    ut_key = 5
    ut_atr = 10
    tp = 0.20
    sl = 0.01
    leverage = 30
    margin_pct = 0.1

    print("Finalizing IMBA + UT BOT Strategy (3 Years) using 15m Precision...")

    signals, ut_raw = imba_ut_bot_strategy(df_1h, imba_sens=sensitivity, ut_key=ut_key, ut_atr=ut_atr)
    bt = MTFBacktester(leverage=leverage)
    # Use 1h for signals, 15m for precision SL/TP checking
    res = bt.run_backtest(df_1h, signals, df_15m, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct, exit_signals=ut_raw)

    print("\nIMBA + UT BOT RESULTS")
    print("="*30)
    print(f"Total ROI: {res['total_return_pct']:.2f}%")
    print(f"Best 60-Day ROI: {res['best_60d_roi']:.2f}%")
    print(f"Win Rate: {res['win_rate']:.2%}")

    res['trades'].to_csv('imba_ut_final_log.csv')
    print("\nLogs saved to imba_ut_final_log.csv")

if __name__ == "__main__":
    finalize_imba_ut()
