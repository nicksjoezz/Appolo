import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import *
import sys

def optimize_imba():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)
    df_15m = pd.read_csv('data/ROSEUSDT_15m.csv', index_col='timestamp', parse_dates=True)

    timeframes = [('1h', df_1h), ('15m', df_15m)]
    results = []

    margin_pct = 0.1
    leverage = 30

    # Grid for IMBA
    sensitivities = [1, 5, 10, 15, 18, 20, 25]
    # TP/SL combinations
    # User wants GOOD win rate and HIGH ROI
    tp_ranges = [0.03, 0.05, 0.1]
    sl_ranges = [0.01, 0.02, 0.05]

    for tf_name, df in timeframes:
        print(f"Optimizing IMBA on {tf_name}...", file=sys.stderr)
        for s in sensitivities:
            signals = imba_algo_trend(df, sensitivity=s)
            for tp in tp_ranges:
                for sl in sl_ranges:
                    bt = Backtester(leverage=leverage)
                    res = bt.run_backtest(df, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
                    if res['n_trades'] >= 5:
                        results.append({
                            'strategy': 'IMBA', 'tf': tf_name,
                            'params': {'sensitivity': s},
                            'tp': tp, 'sl': sl, 'mgn': margin_pct, 'res': res
                        })

    # Sort by a score that balances ROI and Win Rate
    # Score = ROI * WinRate (Simple way to find high returns with decent hit rate)
    for item in results:
        # Avoid penalizing very high ROI but keep win rate in mind
        # We can also just sort by ROI and filter for WinRate > 30%
        pass

    # Best by ROI among those with WinRate > 30%
    best_balanced = [r for r in results if r['res']['win_rate'] > 0.30]
    best_balanced.sort(key=lambda x: x['res']['total_return_pct'], reverse=True)

    # Top ROI regardless of WinRate
    results.sort(key=lambda x: x['res']['total_return_pct'], reverse=True)

    print("\n\nTOP STRATEGIES BY ROI (10% MARGIN, 30X LEVERAGE)")
    print("="*60)
    for i, item in enumerate(results[:5]):
        r = item['res']
        print(f"{i+1}. {item['strategy']} {item['tf']}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']*100:.2f}% | Sharpe: {r['sharpe_ratio']:.4f}")
        print(f"   MDD: {r['max_drawdown_pct']:.2f}% | Trades: {r['n_trades']}")
        print(f"   Params: {item['params']}, TP: {item['tp']}, SL: {item['sl']}")
        print("-" * 50)

    print("\n\nTOP BALANCED STRATEGIES (Win Rate > 30%)")
    print("="*60)
    for i, item in enumerate(best_balanced[:5]):
        r = item['res']
        print(f"{i+1}. {item['strategy']} {item['tf']}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']*100:.2f}% | Sharpe: {r['sharpe_ratio']:.4f}")
        print(f"   MDD: {r['max_drawdown_pct']:.2f}% | Trades: {r['n_trades']}")
        print(f"   Params: {item['params']}, TP: {item['tp']}, SL: {item['sl']}")
        print("-" * 50)

if __name__ == "__main__":
    optimize_imba()
