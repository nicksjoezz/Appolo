import pandas as pd
import matplotlib.pyplot as plt
from backtester import Backtester
from strategies import rsi_bb_strategy

def finalize():
    # Load 15m data
    df = pd.read_csv('data/ROSEUSDT_15m.csv', index_col='timestamp', parse_dates=True)

    # Best strategy: RSI BB (15m), len=14, ob=80, os=20, tp=0.1, sl=0.03, mgn=0.6
    rsi_len, ob, os = 14, 80, 20
    tp, sl, mgn = 0.1, 0.03, 0.6

    signals = rsi_bb_strategy(df, rsi_len=rsi_len, rsi_ob=ob, rsi_os=os)
    bt = Backtester(leverage=30)
    res = bt.run_backtest(df, signals, tp_pct=tp, sl_pct=sl, margin_pct=mgn)

    print("BEST AGGRESSIVE STRATEGY: RSI BB (15M)")
    print(f"Parameters: Length={rsi_len}, OB={ob}, OS={os}")
    print(f"TP={tp*100:.1f}%, SL={sl*100:.1f}%, Margin per trade={mgn*100:.0f}% of balance")
    print("-" * 30)
    print(f"Total Return: {res['total_return_pct']:.2f}%")
    print(f"Max Drawdown: {res['max_drawdown_pct']:.2f}%")
    print(f"Sharpe Ratio: {res['sharpe_ratio']:.4f}")
    print(f"Number of Trades: {res['n_trades']}")
    print(f"Win Rate: {res['win_rate']*100:.2f}%")

    # Save results
    equity_df = pd.DataFrame({'equity': res['equity_curve']}, index=df.index)
    equity_df.to_csv('aggressive_equity_curve.csv')
    res['trades'].to_csv('aggressive_trade_log.csv')
    print("\nLogs saved to 'aggressive_equity_curve.csv' and 'aggressive_trade_log.csv'")

if __name__ == "__main__":
    finalize()
