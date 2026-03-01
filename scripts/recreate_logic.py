import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def recreate_high_roi():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    # Try Sens 18, 10% Margin, 30x, 1% SL, NO FILTERS
    # Using the realistic backtester but WITHOUT intra-candle exit on entry bar
    # To see if THAT was the "Optimistic" logic.

    class SemiOptimisticBacktester(Backtester):
        def run_backtest(self, df, signals, tp_pct=0.05, sl_pct=0.01, margin_pct=0.1):
            self.balance = self.initial_balance
            for i in range(len(df)):
                current_time = df.index[i]
                if self.position != 0:
                    exit_price = None
                    if self.position == 1:
                        if df['low'].iloc[i] <= self.sl: exit_price = self.sl
                        elif df['high'].iloc[i] >= self.tp: exit_price = self.tp
                    else:
                        if df['high'].iloc[i] >= self.sl: exit_price = self.sl
                        elif df['low'].iloc[i] <= self.tp: exit_price = self.tp
                    if exit_price:
                        if self._close_pos(exit_price, current_time, "Exit"): break

                # ENTRY on bar i Close, but CHECK EXIT starting bar i+1
                signal = signals.iloc[i]
                if self.position == 0 and signal != 0 and self.balance > 0:
                    self._open_pos(signal, df['close'].iloc[i], current_time, tp_pct, sl_pct, margin_pct)
                    # NO intra-candle check here
                self.equity_curve.append(self.balance)
            return self._get_results()

    signals = imba_algo_trend_filtered(df_1h, sensitivity=18, ema_filter=False)
    bt = SemiOptimisticBacktester(leverage=30)
    res = bt.run_backtest(df_1h, signals, tp_pct=0.05, sl_pct=0.01, margin_pct=0.1)

    print("SEMI-OPTIMISTIC RESULTS (Entry Close, Exit Next Bar H/L)")
    print(f"ROI: {res['total_return_pct']:.2f}% | Win Rate: {res['win_rate']:.2%}")

    # Try Sens 1
    signals_1 = imba_algo_trend_filtered(df_1h, sensitivity=1, ema_filter=False)
    bt_1 = SemiOptimisticBacktester(leverage=30)
    res_1 = bt_1.run_backtest(df_1h, signals_1, tp_pct=0.05, sl_pct=0.01, margin_pct=0.1)
    print(f"Semi-Optimistic Sens 1 ROI: {res_1['total_return_pct']:.2f}%")

if __name__ == "__main__":
    recreate_high_roi()
