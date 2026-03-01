import pandas as pd
import matplotlib.pyplot as plt
from backtester import Backtester
from strategies import imba_algo_trend

def finalize():
    # Load 1h data
    df = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    # Best Balanced Strategy: IMBA 1h, sensitivity=1, TP=0.05, SL=0.05
    # Best ROI Strategy: IMBA 1h, sensitivity=18, TP=0.05, SL=0.01

    strategies = [
        {'name': 'IMBA_HIGH_ROI', 'sens': 18, 'tp': 0.05, 'sl': 0.01},
        {'name': 'IMBA_BALANCED', 'sens': 1, 'tp': 0.05, 'sl': 0.05}
    ]

    for s_info in strategies:
        signals = imba_algo_trend(df, sensitivity=s_info['sens'])
        bt = Backtester(leverage=30)
        res = bt.run_backtest(df, signals, tp_pct=s_info['tp'], sl_pct=s_info['sl'], margin_pct=0.1)

        print(f"\nFINALIZE: {s_info['name']}")
        print(f"Parameters: Sensitivity={s_info['sens']}, TP={s_info['tp']*100}%, SL={s_info['sl']*100}%")
        print("-" * 30)
        print(f"ROI: {res['total_return_pct']:.2f}%")
        print(f"Win Rate: {res['win_rate']*100:.2f}%")
        print(f"Sharpe Ratio: {res['sharpe_ratio']:.4f}")
        print(f"Max Drawdown: {res['max_drawdown_pct']:.2f}%")
        print(f"Number of Trades: {res['n_trades']}")

        res['trades'].to_csv(f"imba_{s_info['name']}_log.csv")
        equity_df = pd.DataFrame({'equity': res['equity_curve']}, index=df.index)
        equity_df.to_csv(f"imba_{s_info['name']}_equity.csv")

    print("\nLogs and equity curves saved for both IMBA versions.")

if __name__ == "__main__":
    finalize()
