import pandas as pd
import numpy as np

class RealisticBacktester:
    def __init__(self, initial_balance=1000, fee=0.0005, leverage=30):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.fee = fee
        self.leverage = leverage
        self.position = 0
        self.entry_price = 0
        self.tp = 0
        self.sl = 0
        self.margin_at_entry = 0

    def _open_pos(self, side, price, tp_pct, sl_pct, margin_pct):
        self.position = side
        self.entry_price = price
        self.margin_at_entry = self.balance * margin_pct
        pos_value = self.margin_at_entry * self.leverage
        entry_fee = pos_value * self.fee
        self.balance -= entry_fee
        if side == 1:
            self.tp = price * (1 + tp_pct)
            self.sl = price * (1 - sl_pct)
        else:
            self.tp = price * (1 - tp_pct)
            self.sl = price * (1 + sl_pct)

    def _close_pos(self, price):
        pos_value_entry = self.margin_at_entry * self.leverage
        pnl_pct_move = self.position * (price / self.entry_price - 1)
        pnl_amount = pnl_pct_move * pos_value_entry
        exit_fee = (pos_value_entry + pnl_amount) * self.fee
        self.balance += pnl_amount - exit_fee
        self.position = 0

    def run_backtest(self, df, signals, tp_pct=0.05, sl_pct=0.01, margin_pct=0.1):
        self.balance = self.initial_balance
        for i in range(len(df)):
            # If in position, check for exit using high/low
            if self.position != 0:
                if self.position == 1:
                    if df['low'].iloc[i] <= self.sl: self._close_pos(self.sl)
                    elif df['high'].iloc[i] >= self.tp: self._close_pos(self.tp)
                else:
                    if df['high'].iloc[i] >= self.sl: self._close_pos(self.sl)
                    elif df['low'].iloc[i] <= self.tp: self._close_pos(self.tp)

            # If flat, check for entry signal on PREVIOUS bar
            # (Entry on current Open if previous bar had signal)
            if self.position == 0 and i > 0:
                signal = signals.iloc[i-1]
                if signal != 0:
                    self._open_pos(signal, df['open'].iloc[i], tp_pct, sl_pct, margin_pct)
                    # Check for intra-candle exit on the SAME entry bar
                    if self.position == 1:
                        if df['low'].iloc[i] <= self.sl: self._close_pos(self.sl)
                        elif df['high'].iloc[i] >= self.tp: self._close_pos(self.tp)
                    else:
                        if df['high'].iloc[i] >= self.sl: self._close_pos(self.sl)
                        elif df['low'].iloc[i] <= self.tp: self._close_pos(self.tp)
        return self.balance

if __name__ == "__main__":
    df = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)
    from strategies import imba_algo_trend_filtered
    # Sens 18
    signals_18 = imba_algo_trend_filtered(df, sensitivity=18, ema_filter=False, rsi_filter=False)
    # Sens 1
    signals_1 = imba_algo_trend_filtered(df, sensitivity=1, ema_filter=False, rsi_filter=False)

    real = RealisticBacktester()
    res_18 = real.run_backtest(df, signals_18, tp_pct=0.05, sl_pct=0.01, margin_pct=0.1)
    print(f"Realistic Sens 18 Final: {res_18:.2f}")

    real_1 = RealisticBacktester()
    res_1 = real_1.run_backtest(df, signals_1, tp_pct=0.05, sl_pct=0.01, margin_pct=0.1)
    print(f"Realistic Sens 1 Final: {res_1:.2f}")
