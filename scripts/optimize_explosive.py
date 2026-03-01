import pandas as pd
import numpy as np
from mtf_backtester import MTFBacktester
from strategies import *
import sys

def optimize_explosive():
    df_1h = pd.read_csv('data/ROSEUSDT_1h_3y.csv', index_col='timestamp', parse_dates=True)

    leverage = 30
    margin_pct = 0.1
    sl = 0.015

    results = []

    strats = [
        ('IMBA_S20_Filtered', lambda d: imba_algo_trend_filtered(d, sensitivity=20)),
        ('High_Vol_Filtered', lambda d: high_vol_breakout_strategy(d, mult=2.5)),
        ('RSI_Scalp_Filtered', lambda d: rsi_momentum_scalper(d)),
        ('VW_MACD_Filtered', lambda d: vw_macd_strategy(d)),
        ('BB_Width_Filtered', lambda d: bb_width_expansion_strategy(d)),
        ('Agg_Donchian_Filtered', lambda d: aggressive_donchian_strategy(d))
    ]

    print("Backtesting Filtered Explosive Potential (30x, 10% Margin, 1.5% SL)...", file=sys.stderr)

    for name, s_func in strats:
        print(f"  Testing {name}...", file=sys.stderr)
        signals = s_func(df_1h)
        for tp in [0.05, 0.10]:
            bt = MTFBacktester(leverage=leverage)
            # Full 3y 1h sweep
            res = bt.run_backtest(df_1h, signals, df_1h, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
            if res['n_trades'] > 10:
                results.append({'name': name, 'tp': tp, 'res': res})

    # Sort by 60-day ROI but cap displayed total ROI to avoid infinity issues
    results.sort(key=lambda x: x['res']['best_60d_roi'], reverse=True)

    print("\nTOP FILTERED EXPLOSIVE STRATEGIES (3-YEAR TEST)")
    print("="*60)
    for i, item in enumerate(results[:10]):
        r = item['res']
        print(f"{i+1}. {item['name']} | TP: {item['tp']:.0%}")
        print(f"   BEST 60-DAY ROI: {r['best_60d_roi']:.2f}%")
        # For very high ROI, we show in scientific notation if needed
        print(f"   Win Rate: {r['win_rate']:.2%} | Trades: {r['n_trades']}")
        print("-" * 50)

if __name__ == "__main__":
    optimize_explosive()
