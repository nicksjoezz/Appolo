import pandas as pd
import numpy as np
from scripts.daily_crossover_strategy import DailyCrossoverBacktester

def analyze():
    print("Starting analysis...")
    df = pd.read_csv('data/ROSEUSDT_15m_3y.csv', index_col='timestamp', parse_dates=True)
    start_90d = df.index[-1] - pd.Timedelta(days=90)
    df_90d = df.loc[start_90d:]

    res = DailyCrossoverBacktester().run_backtest(df_90d)
    print(f"90-Day ROI: {res['roi']:.2f}% | Win Rate: {res['win_rate']:.2%} | Trades: {res['n_trades']}")

    if res['n_trades'] > 0:
        tdf = res['trades']
        print("\nExit Reasons count:")
        print(tdf['reason'].value_counts().to_string())

        print("\nAverage PnL by Reason:")
        print(tdf.groupby('reason')['pnl'].mean().to_string())

        print("\nWin Rate by Side:")
        wr_side = tdf.groupby('side').apply(lambda x: (x['pnl'] > 0).mean())
        print(wr_side.to_string())

if __name__ == "__main__":
    analyze()
