import pandas as pd
import matplotlib.pyplot as plt
from backtester import Backtester
from strategies import imba_algo_trend

def finalize():
    # Load 1h data
    df = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    # Selecting three variants of the "Safe-High-ROI" IMBA:
    # 1. Best Overall Balance (ROI/WinRate/MDD)
    # 2. Maximum Win Rate
    # 3. High ROI Optimized for more stability (higher SL)

    configs = [
        {'name': 'IMBA_BEST_BALANCE', 'sens': 1, 'tp': 0.05, 'sl': 0.05},
        {'name': 'IMBA_MAX_WINRATE', 'sens': 1, 'tp': 0.03, 'sl': 0.05},
        {'name': 'IMBA_SENS_2_STABLE', 'sens': 2, 'tp': 0.05, 'sl': 0.05}
    ]

    print("FINAL SELECTION: OPTIMIZED IMBA STRATEGIES")
    print("="*60)

    for config in configs:
        signals = imba_algo_trend(df, sensitivity=config['sens'])
        bt = Backtester(leverage=30)
        res = bt.run_backtest(df, signals, tp_pct=config['tp'], sl_pct=config['sl'], margin_pct=0.1)

        print(f"Strategy: {config['name']}")
        print(f"Params: Sens={config['sens']}, TP={config['tp']:.2%}, SL={config['sl']:.2%}")
        print(f"ROI: {res['total_return_pct']:.2f}% | Win Rate: {res['win_rate']:.2%} | MDD: {res['max_drawdown_pct']:.2f}%")
        print(f"Sharpe: {res['sharpe_ratio']:.4f} | Trades: {res['n_trades']}")
        print("-" * 50)

        # Save logs for the best balanced one
        if config['name'] == 'IMBA_BEST_BALANCE':
            res['trades'].to_csv('final_imba_optimized_log.csv')
            equity_df = pd.DataFrame({'equity': res['equity_curve']}, index=df.index)
            equity_df.to_csv('final_imba_optimized_equity.csv')

if __name__ == "__main__":
    finalize()
