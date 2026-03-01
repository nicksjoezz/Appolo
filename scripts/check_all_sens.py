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
        self.trades = []
        self.equity_curve = []

    def _open_pos(self, side, price, time, tp_pct, sl_pct, margin_pct):
        if self.balance <= 0: return
        self.position = side
        self.entry_price = price
        self.margin_at_entry = self.balance * margin_pct
        pos_value = self.margin_at_entry * self.leverage
        entry_fee = pos_value * self.fee
        if self.balance - entry_fee <= 0:
            self.position = 0
            return
        self.balance -= entry_fee
        if side == 1:
            self.tp = price * (1 + tp_pct)
            self.sl = price * (1 - sl_pct)
        else:
            self.tp = price * (1 - tp_pct)
            self.sl = price * (1 + sl_pct)
        self.trades.append({'entry_time': time, 'entry_price': price, 'side': 'LONG' if side == 1 else 'SHORT', 'margin': self.margin_at_entry})

    def _close_pos(self, price, time, reason):
        pos_value_entry = self.margin_at_entry * self.leverage
        pnl_pct_move = self.position * (price / self.entry_price - 1)
        pnl_amount = pnl_pct_move * pos_value_entry
        exit_fee = (pos_value_entry + pnl_amount) * self.fee
        self.balance += pnl_amount - exit_fee
        if self.balance < 0: self.balance = 0
        self.trades[-1].update({'exit_time': time, 'exit_price': price, 'pnl': pnl_amount - exit_fee})
        self.position = 0
        return self.balance <= 0

    def run_backtest(self, df, signals, tp_pct=0.05, sl_pct=0.01, margin_pct=0.1):
        self.balance = self.initial_balance
        for i in range(len(df)):
            if self.position != 0:
                if self.position == 1:
                    if df['low'].iloc[i] <= self.sl: self._close_pos(self.sl, df.index[i], "SL")
                    elif df['high'].iloc[i] >= self.tp: self._close_pos(self.tp, df.index[i], "TP")
                else:
                    if df['high'].iloc[i] >= self.sl: self._close_pos(self.sl, df.index[i], "SL")
                    elif df['low'].iloc[i] <= self.tp: self._close_pos(self.tp, df.index[i], "TP")

            if self.position == 0 and i < len(df)-1:
                signal = signals.iloc[i]
                if signal != 0:
                    self._open_pos(signal, df['open'].iloc[i+1], df.index[i+1], tp_pct, sl_pct, margin_pct)
            self.equity_curve.append(self.balance)
        return self.balance

if __name__ == "__main__":
    df = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)
    from strategies import imba_algo_trend_filtered
    # sensitivity 18
    signals = imba_algo_trend_filtered(df, sensitivity=18, ema_filter=False, rsi_filter=False, trend_confirmation=False)

    real = RealisticBacktester()
    res = real.run_backtest(df, signals, tp_pct=0.05, sl_pct=0.01, margin_pct=0.1)
    print(f"Realistic ROI: {(res - 1000)/10:.2f}%")

    # Try other sensitivities
    for s in [1, 5, 10, 15, 18, 20]:
        signals = imba_algo_trend_filtered(df, sensitivity=s, ema_filter=False)
        res = RealisticBacktester().run_backtest(df, signals, tp_pct=0.05, sl_pct=0.01, margin_pct=0.1)
        print(f"Sens {s} ROI: {(res - 1000)/10:.2f}%")
