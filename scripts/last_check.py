import pandas as pd
import numpy as np
from mtf_backtester import MTFBacktester
from strategies import imba_ut_bot_strategy

def last_check():
    df_1h = pd.read_csv('data/ROSEUSDT_1h_3y.csv', index_col='timestamp', parse_dates=True)
    leverage = 30
    margin_pct = 0.1
    sensitivity = 20

    # Try the IMBA + UT Bot with the looser 3% SL
    signals, ut_raw = imba_ut_bot_strategy(df_1h, imba_sens=sensitivity, ut_key=5, ut_atr=10)
    bt = MTFBacktester(leverage=leverage)
    res = bt.run_backtest(df_1h, signals, df_1h, tp_pct=0.05, sl_pct=0.03, margin_pct=margin_pct, exit_signals=ut_raw)

    print(f"IMBA+UT Bot (3% SL) 3-Year ROI: {res['total_return_pct']:.2f}%")

    # Try with 5% TP
    res2 = bt.run_backtest(df_1h, signals, df_1h, tp_pct=0.10, sl_pct=0.03, margin_pct=margin_pct, exit_signals=ut_raw)
    print(f"IMBA+UT Bot (3% SL, 10% TP) 3-Year ROI: {res2['total_return_pct']:.2f}%")

if __name__ == "__main__":
    from scripts.fetch_massive_data import fetch_years
    import os
    if not os.path.exists('data/ROSEUSDT_1h_3y.csv'):
        fetch_years('ROSEUSDT', '1h', years=3).to_csv('data/ROSEUSDT_1h_3y.csv')
    last_check()
