import pandas as pd
import numpy as np
import os
from backtester import Backtester
from strategies import rsi_bb_strategy, supertrend_strategy

def optimize():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)
    df_15m = pd.read_csv('data/ROSEUSDT_15m.csv', index_col='timestamp', parse_dates=True)

    results = []

    # Deep optimization for RSI BB on 15m
    print("Fine-tuning RSI BB on 15m...")
    for rsi_len in [10, 14, 20]:
        for rsi_ob in [70, 75, 80]:
            for rsi_os in [20, 25, 30]:
                for tp in [0.03, 0.05, 0.08]:
                    for sl in [0.003, 0.005, 0.01]:
                        signals = rsi_bb_strategy(df_15m, rsi_len=rsi_len, rsi_ob=rsi_ob, rsi_os=rsi_os)
                        bt = Backtester(leverage=30)
                        res = bt.run_backtest(df_15m, signals, tp_pct=tp, sl_pct=sl)
                        if res['n_trades'] > 5:
                            results.append({
                                'strategy': 'RSI_BB', 'tf': '15m',
                                'params': {'len': rsi_len, 'ob': rsi_ob, 'os': rsi_os},
                                'tp': tp, 'sl': sl, 'res': res
                            })

    # Deep optimization for Supertrend on 1h
    print("Fine-tuning Supertrend on 1h...")
    for length in [7, 10, 14]:
        for mult in [2, 3, 4]:
            for tp in [0.05, 0.08, 0.1]:
                for sl in [0.01, 0.02]:
                    signals = supertrend_strategy(df_1h, length=length, multiplier=mult)
                    bt = Backtester(leverage=30)
                    res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl)
                    if res['n_trades'] > 5:
                        results.append({
                            'strategy': 'Supertrend', 'tf': '1h',
                            'params': {'len': length, 'mult': mult},
                            'tp': tp, 'sl': sl, 'res': res
                        })

    results.sort(key=lambda x: x['res']['sharpe_ratio'], reverse=True)

    print("\nTOP 3 OPTIMIZED STRATEGIES")
    for i, item in enumerate(results[:3]):
        r = item['res']
        print(f"{i+1}. {item['strategy']} {item['tf']}")
        print(f"   Sharpe: {r['sharpe_ratio']:.4f}, Return: {r['total_return_pct']:.2f}%, MDD: {r['max_drawdown_pct']:.2f}%")
        print(f"   Params: {item['params']}, TP: {item['tp']}, SL: {item['sl']}")
        print(f"   Trades: {r['n_trades']}, Win Rate: {r['win_rate']*100:.2f}%")
        print("-" * 30)

if __name__ == "__main__":
    optimize()
