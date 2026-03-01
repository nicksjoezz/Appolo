import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def sweep_vbt_filters():
    df_1h = pd.read_csv('data/ROSEUSDT_1h_3y.csv', index_col='timestamp', parse_dates=True)

    leverage = 30
    margin_pct = 0.1
    sensitivity = 20
    results = []

    print("Final Deep Sweep (Sens 20, 3y)...", file=sys.stderr)

    # Try different TP and SL
    for tp in [0.03, 0.05]:
        for sl in [0.02, 0.03, 0.04]:
            # Keep DMI but relax trend confirm?
            # User wants HEAVY ROI
            signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity,
                                              ema_filter=True, ema_len=200,
                                              trend_confirmation=True,
                                              dmi_filter=True)
            bt = Backtester(leverage=leverage)
            res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
            results.append({'tp': tp, 'sl': sl, 'res': res})

    summary = []
    for r in results:
        m = r['res']
        summary.append({
            'TP%': r['tp']*100,
            'SL%': r['sl']*100,
            'ROI %': m['total_return_pct'],
            'Win Rate %': m['win_rate'] * 100,
            'MDD %': m['max_drawdown_pct'],
            'Sharpe': m['sharpe_ratio'],
            'Trades': m['n_trades']
        })

    summary_df = pd.DataFrame(summary).sort_values(by='ROI %', ascending=False)
    print("\nFINAL DEEP SWEEP RESULTS (3 YEARS)")
    print("="*60)
    print(summary_df.to_string(index=False))

if __name__ == "__main__":
    sweep_vbt_filters()
