import pandas as pd
import numpy as np
from mtf_backtester import MTFBacktester
from strategies import aggressive_donchian_strategy

def run_top_explosive():
    df_1h = pd.read_csv('data/ROSEUSDT_1h_3y.csv', index_col='timestamp', parse_dates=True)

    # TOP EXPLOSIVE: Aggressive Donchian (1H), Length 10, TP 5%, SL 1.5%, ADX Filter
    tp, sl, mgn = 0.05, 0.015, 0.1

    print("Running ABSOLUTE BEST EXPLOSIVE strategy (Aggressive Donchian)...")

    signals = aggressive_donchian_strategy(df_1h, length=10)
    bt = MTFBacktester(leverage=30)
    res = bt.run_backtest(df_1h, signals, df_1h, tp_pct=tp, sl_pct=sl, margin_pct=mgn)

    print("\nEXPLOSIVE STRATEGY RESULTS (3 YEARS)")
    print("="*40)
    print(f"Best 60-Day ROI: {res['best_60d_roi']:.2f}%")
    print(f"Win Rate: {res['win_rate']:.2%}")
    print(f"Total Trades: {res['n_trades']}")

    res['trades'].to_csv('explosive_trade_log.csv')
    print("\nLogs saved to explosive_trade_log.csv")

if __name__ == "__main__":
    run_top_explosive()
