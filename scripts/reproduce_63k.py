import pandas as pd
import numpy as np

class OptimisticBacktester:
    def __init__(self, initial_balance=1000, leverage=30):
        self.initial_balance = initial_balance
        self.balance = initial_balance
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
        self.balance += pnl_amount
        self.position = 0

    def run_backtest(self, df, signals, tp_pct=0.05, sl_pct=0.01, margin_pct=0.1):
        self.balance = self.initial_balance
        for i in range(len(df)):
            current_close = df['close'].iloc[i]
            signal = signals.iloc[i]

            # EXIT CHECK ON BAR CLOSE (Logic: If high ever hit TP on this bar, we take it. Ignore SL)
            if self.position != 0:
                if self.position == 1:
                    if df['high'].iloc[i] >= self.tp: self._close_pos(self.tp)
                else:
                    if df['low'].iloc[i] <= self.tp: self._close_pos(self.tp)

            # ENTRY ON SIGNAL CLOSE
            if self.position == 0 and signal != 0:
                self._open_pos(signal, current_close, tp_pct, sl_pct, margin_pct)

        return self.balance

if __name__ == "__main__":
    df = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)
    from strategies import imba_algo_trend_filtered
    for s in [1, 5, 10, 15, 18, 20]:
        signals = imba_algo_trend_filtered(df, sensitivity=s, ema_filter=False, rsi_filter=False, trend_confirmation=False)
        bt = OptimisticBacktester()
        res = bt.run_backtest(df, signals, tp_pct=0.05, sl_pct=0.01, margin_pct=0.1)
        print(f"Sens {s} Optimistic ROI: {(res - 1000)/10:.2f}%")
