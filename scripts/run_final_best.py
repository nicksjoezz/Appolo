import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtester import Backtester
from strategies import imba_algo_trend_filtered

def run_final():
    data_path = os.path.join(os.path.dirname(__file__), '../data/ROSEUSDT_1h_3y.csv')
    if not os.path.exists(data_path):
        from fetch_data import fetch_years
        os.makedirs('data', exist_ok=True)
        fetch_years('ROSEUSDT', '1h', years=3).to_csv(data_path)

    df_1h = pd.read_csv(data_path, index_col='timestamp', parse_dates=True)

    # BEST ROBUST STRATEGY: Sens 20, 5% TP, 3% SL
    print("Running FINAL ROBUST strategy (SENS 20, EMA 200, DMI, TC)...")

    signals = imba_algo_trend_filtered(df_1h, sensitivity=20, ema_len=200)

    bt = Backtester(leverage=30)
    res = bt.run_backtest(df_1h, signals, tp_pct=0.05, sl_pct=0.03, margin_pct=0.1)

    print("\nFINAL RESULTS")
    print("="*30)
    print(f"Total ROI: {res['total_return_pct']:.2f}%")
    print(f"Win Rate: {res['win_rate']:.2%}")
    print(f"Max Drawdown: {res['max_drawdown_pct']:.2f}%")

    res['trades'].to_csv('final_best_trade_log.csv')
    print("\nLogs saved to final_best_trade_log.csv")

if __name__ == "__main__":
    run_final()
