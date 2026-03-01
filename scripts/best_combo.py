import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def sweep_best_combo():
    df_1h = pd.read_csv('data/ROSEUSDT_1h_3y.csv', index_col='timestamp', parse_dates=True)

    leverage = 30
    margin_pct = 0.1
    sensitivity = 20
    results = []

    print("Sweeping best filters (Sens 20, 3y)...", file=sys.stderr)

    for tp in [0.05, 0.08]:
        for sl in [0.015, 0.02, 0.025]: # User open to < 3%
            # Combine TC with EMA and ADX/DMI
            signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity,
                                              ema_filter=True, ema_len=500,
                                              trend_confirmation=True,
                                              adx_filter=True, dmi_filter=True)
            bt = Backtester(leverage=leverage)
            res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
            results.append({'name': f"FULL_FILTER_TP{int(tp*100)}_SL{sl:.1%}", 'res': res})

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
    print("\nBEST COMBO RESULTS (3 YEARS)")
    print("="*60)
    print(summary_df.to_string(index=False))

if __name__ == "__main__":
    sweep_best_combo()
