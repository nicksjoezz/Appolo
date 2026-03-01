import pandas as pd
import matplotlib.pyplot as plt
from backtester import Backtester
from strategies import supertrend_strategy

def finalize():
    # Load 1h data
    df = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    # Best strategy: Supertrend 1h, len=7, mult=4, tp=0.05, sl=0.01
    length, mult, tp, sl = 7, 4, 0.05, 0.01

    signals = supertrend_strategy(df, length=length, multiplier=mult)
    bt = Backtester(leverage=30)
    res = bt.run_backtest(df, signals, tp_pct=tp, sl_pct=sl)

    print("BEST OVERALL STRATEGY: SUPERTREND (1H)")
    print(f"Parameters: Length={length}, Multiplier={mult}")
    print(f"TP={tp*100:.1f}%, SL={sl*100:.1f}%")
    print("-" * 30)
    print(f"Total Return: {res['total_return_pct']:.2f}%")
    print(f"Max Drawdown: {res['max_drawdown_pct']:.2f}%")
    print(f"Sharpe Ratio: {res['sharpe_ratio']:.4f}")
    print(f"Number of Trades: {res['n_trades']}")
    print(f"Win Rate: {res['win_rate']*100:.2f}%")

    # Generate Equity Curve CSV for verification
    equity_df = pd.DataFrame({'equity': res['equity_curve']}, index=df.index)
    equity_df.to_csv('results_equity_curve.csv')

    # Detailed trade log
    res['trades'].to_csv('results_trade_log.csv')
    print("\nLogs saved to 'results_equity_curve.csv' and 'results_trade_log.csv'")

if __name__ == "__main__":
    finalize()
