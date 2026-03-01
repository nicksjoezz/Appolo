import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def sweep_aggressive_filters():
    df_1h = pd.read_csv('data/ROSEUSDT_1h_3y.csv', index_col='timestamp', parse_dates=True)

    leverage = 30
    margin_pct = 0.1
    sensitivity = 20
    results = []

    print("Sweeping aggressive filters (Sens 20, 3y)...", file=sys.stderr)

    # Try different TP and SL for very high ROI
    for tp in [0.05, 0.08, 0.1, 0.12]:
        for sl in [0.02, 0.025, 0.03]:
            # Slightly more relaxed filter to increase trade count?
            # Current best had 105 trades in 3 years (too low?)
            # Let's remove ADX max constraint but keep DMI
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
    print("\nAGGRESSIVE FILTER RESULTS (3 YEARS)")
    print("="*60)
    print(summary_df.to_string(index=False))

if __name__ == "__main__":
    sweep_aggressive_filters()
