import pandas as pd
import numpy as np

class MTFBacktester:
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
        self.trades.append({
            'entry_time': time, 'entry_price': price,
            'side': 'LONG' if side == 1 else 'SHORT',
            'margin': self.margin_at_entry, 'tp_price': self.tp, 'sl_price': self.sl
        })

    def _close_pos(self, price, time, reason):
        pos_value_entry = self.margin_at_entry * self.leverage
        pnl_pct_move = self.position * (price / self.entry_price - 1)
        pnl_amount = pnl_pct_move * pos_value_entry
        exit_fee = (pos_value_entry + pnl_amount) * self.fee
        self.balance += pnl_amount - exit_fee
        if self.balance < 0: self.balance = 0
        self.trades[-1].update({'exit_time': time, 'exit_price': price, 'pnl': pnl_amount - exit_fee, 'reason': reason})
        self.position = 0

    def run_backtest(self, df_1h, signals, df_5m, tp_pct=0.05, sl_pct=0.01, margin_pct=0.1):
        """
        Signals are aligned with df_1h.
        Execution uses df_5m for high precision intra-hour SL/TP tracking.
        """
        self.balance = self.initial_balance
        self.position = 0
        self.trades = []

        # Align 5m data with 1h signals
        # We process bar-by-bar
        for i in range(len(df_1h) - 1):
            current_time = df_1h.index[i]
            next_1h_time = df_1h.index[i+1]
            signal = signals.iloc[i]

            # Sub-data for the next 1 hour
            sub_5m = df_5m.loc[current_time : next_1h_time - pd.Timedelta(seconds=1)]

            if sub_5m.empty:
                # If no 5m data, fallback to 1h bars (less precise)
                # But for this task, we assume 5m data is present.
                continue

            for t5, row5 in sub_5m.iterrows():
                # 1. Check Exit
                if self.position != 0:
                    exit_price = None
                    if self.position == 1:
                        if row5['low'] <= self.sl: exit_price = self.sl
                        elif row5['high'] >= self.tp: exit_price = self.tp
                    else:
                        if row5['high'] >= self.sl: exit_price = self.sl
                        elif row5['low'] <= self.tp: exit_price = self.tp

                    if exit_price:
                        self._close_pos(exit_price, t5, "Exit")
                        if self.balance <= 0: return self._results()

                # 2. Check Entry Signal (Only at the start of the hour)
                # Signal was generated at the close of bar i, so we enter on the first 5m bar of bar i+1
                if self.position == 0 and t5 == current_time:
                    if signal != 0 and self.balance > 0:
                        self._open_pos(signal, row5['open'], t5, tp_pct, sl_pct, margin_pct)

        return self._results()

    def _results(self):
        if not self.trades: return {"total_return_pct": 0, "n_trades": 0, "win_rate": 0}
        df = pd.DataFrame([t for t in self.trades if 'pnl' in t])
        if df.empty: return {"total_return_pct": 0, "n_trades": 0, "win_rate": 0}
        roi = (self.balance - self.initial_balance) / self.initial_balance * 100
        wr = len(df[df['pnl'] > 0]) / len(df)
        return {'final_balance': self.balance, 'total_return_pct': roi, 'n_trades': len(df), 'win_rate': wr, 'trades': df}
