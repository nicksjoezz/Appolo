import pandas as pd
import numpy as np
import os
import sys
from datetime import timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backtester import Backtester
from strategies import imba_algo_trend_filtered

def run_batch_backtest(data_path, window_days=60):
    if not os.path.exists(data_path):
        print(f"Data not found at {data_path}")
        return

    # Loading the full 3-year file once is generally fine for a ~30MB CSV in this environment.
    # To handle memory even more efficiently, we would read it in chunks or use indexed parquet.
    # For simplicity, we'll keep the full load but slice the DataFrame.

    df_full = pd.read_csv(data_path, index_col='timestamp', parse_dates=True)
    start_date = df_full.index.min()
    end_date = df_full.index.max()

    current_start = start_date
    batch_results = []

    print(f"Starting batch backtest from {start_date} to {end_date} in {window_days}-day windows...")
    print("-" * 50)

    while current_start < end_date:
        current_end = current_start + timedelta(days=window_days)
        df_batch = df_full.loc[current_start:current_end]

        if len(df_batch) < 100: # Skip small chunks
            current_start = current_end
            continue

        # Run Strategy
        signals = imba_algo_trend_filtered(df_batch, sensitivity=20)

        # Run Backtest
        bt = Backtester(initial_balance=1000, leverage=30)
        res = bt.run_backtest(df_batch, signals, tp_pct=0.05, sl_pct=0.03, margin_pct=0.1)

        batch_results.append({
            'start': current_start.strftime('%Y-%m-%d'),
            'end': current_end.strftime('%Y-%m-%d'),
            'roi': res['total_return_pct'],
            'win_rate': res['win_rate'],
            'trades': res['n_trades']
        })

        print(f"Window: {current_start.strftime('%Y-%m-%d')} to {current_end.strftime('%Y-%m-%d')} | ROI: {res['total_return_pct']:.2f}% | Trades: {res['n_trades']}")

        current_start = current_end

    print("-" * 50)
    res_df = pd.DataFrame(batch_results)
    print("\nBATCH SUMMARY:")
    print(res_df[['start', 'end', 'roi', 'win_rate', 'trades']].to_string(index=False))

    avg_roi = res_df['roi'].mean()
    total_trades = res_df['trades'].sum()
    print(f"\nAverage 60-Day ROI: {avg_roi:.2f}%")
    print(f"Total Trades across all batches: {total_trades}")

    res_df.to_csv('batch_results_60d.csv', index=False)
    print("\nResults saved to batch_results_60d.csv")

if __name__ == "__main__":
    data_file = 'data/ROSEUSDT_1h_3y.csv'
    run_batch_backtest(data_file)
