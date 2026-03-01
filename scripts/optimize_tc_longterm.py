import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def optimize_with_tc_longterm():
    df_1h = pd.read_csv('data/ROSEUSDT_1h_3y.csv', index_col='timestamp', parse_dates=True)

    leverage = 30
    margin_pct = 0.1
    sensitivity = 20
    results = []

    print("Long-term TC Optimization (Sens 20, 3y data)...", file=sys.stderr)

    # TC is essential for 30x survival
    for tp in [0.05, 0.10, 0.20]:
        for sl in [0.01, 0.02]:
            # Test TC with EMA 500
            signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity,
                                              ema_filter=True, ema_len=500,
                                              trend_confirmation=True)
            bt = Backtester(leverage=leverage)
            res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
            results.append({'name': f"EMA500_TC_TP{int(tp*100)}_SL{int(sl*100)}", 'res': res})

    summary = []
    for r in results:
        m = r['res']
        summary.append({
            'Config': r['name'],
            'ROI %': m['total_return_pct'],
            'Win Rate %': m['win_rate'] * 100,
            'MDD %': m['max_drawdown_pct'],
            'Sharpe': m['sharpe_ratio'],
            'Trades': m['n_trades']
        })

    summary_df = pd.DataFrame(summary).sort_values(by='ROI %', ascending=False)
    print("\nLONG-TERM TC RESULTS (3 YEARS)")
    print("="*60)
    print(summary_df.to_string(index=False))

if __name__ == "__main__":
    optimize_with_tc_longterm()
