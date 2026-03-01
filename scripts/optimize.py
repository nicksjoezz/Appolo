import pandas as pd
import numpy as np
import os
from backtester import Backtester
from strategies import ema_cross_strategy, rsi_bb_strategy, daily_high_low_breakout, supertrend_strategy, macd_strategy

def optimize_params(df, strategy_func, param_grid, tp_range, sl_range):
    best_res = None
    best_score = -float('inf')

    for params in param_grid:
        try:
            signals = strategy_func(df, **params)
        except Exception as e:
            # print(f"Error in strategy {strategy_func.__name__}: {e}")
            continue

        for tp in tp_range:
            for sl in sl_range:
                bt = Backtester(leverage=30)
                res = bt.run_backtest(df, signals, tp_pct=tp, sl_pct=sl)

                if res['final_balance'] <= 10: # Almost liquidated
                    continue

                score = res['sharpe_ratio']

                if score > best_score:
                    best_score = score
                    best_res = {
                        'params': params,
                        'tp': tp,
                        'sl': sl,
                        'results': res
                    }
    return best_res

if __name__ == "__main__":
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)
    df_15m = pd.read_csv('data/ROSEUSDT_15m.csv', index_col='timestamp', parse_dates=True)

    timeframes = {'1h': df_1h, '15m': df_15m}

    # Define Parameter Grids
    ema_grid = [{'fast': 9, 'slow': 21}, {'fast': 20, 'slow': 50}]
    rsi_grid = [{'rsi_len': 14, 'rsi_ob': 70, 'rsi_os': 30, 'bb_len': 20, 'bb_std': 2}]
    st_grid = [{'length': 10, 'multiplier': 3}, {'length': 12, 'multiplier': 2}]
    macd_grid = [{'fast': 12, 'slow': 26, 'signal': 9}]

    tp_range = [0.005, 0.01, 0.02, 0.05]
    sl_range = [0.003, 0.005, 0.01]

    all_best = []

    for tf_name, df in timeframes.items():
        print(f"\n--- {tf_name} ---")

        for strategy, grid in [
            (ema_cross_strategy, ema_grid),
            (rsi_bb_strategy, rsi_grid),
            (supertrend_strategy, st_grid),
            (macd_strategy, macd_grid)
        ]:
            res = optimize_params(df, strategy, grid, tp_range, sl_range)
            if res:
                res['strategy'] = strategy.__name__
                res['tf'] = tf_name
                all_best.append(res)
                print(f"{strategy.__name__}: Sharpe {res['results']['sharpe_ratio']:.4f}, PnL {res['results']['total_return_pct']:.2f}%")

        if tf_name == '1h':
            res_dhl = optimize_params(df, lambda d: daily_high_low_breakout(d), [{}], tp_range, sl_range)
            if res_dhl:
                res_dhl['strategy'] = 'daily_hl'
                res_dhl['tf'] = tf_name
                all_best.append(res_dhl)
                print(f"Daily HL: Sharpe {res_dhl['results']['sharpe_ratio']:.4f}, PnL {res_dhl['results']['total_return_pct']:.2f}%")

    all_best.sort(key=lambda x: x['results']['sharpe_ratio'], reverse=True)

    print("\n\n" + "="*50)
    print("FINAL TOP RESULTS")
    print("="*50)
    for i, item in enumerate(all_best[:5]):
        r = item['results']
        print(f"{i+1}. {item['strategy']} ({item['tf']})")
        print(f"   Sharpe: {r['sharpe_ratio']:.4f}, Return: {r['total_return_pct']:.2f}%, MDD: {r['max_drawdown_pct']:.2f}%")
        print(f"   Params: {item['params']}, TP: {item['tp']}, SL: {item['sl']}")
        print("-" * 30)
