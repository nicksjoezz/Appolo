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

    def run_backtest(self, df_1h, signals, df_precision, tp_pct=0.05, sl_pct=0.01, margin_pct=0.1):
        """
        Signals are aligned with df_1h.
        Execution uses df_precision (e.g. 5m) for high precision intra-hour SL/TP tracking.
        Logic: Signal on bar i (close) -> Entry on bar i+1 Open.
        """
        self.balance = self.initial_balance
        self.position = 0
        self.trades = []
        self.equity_curve = []

        for i in range(len(df_1h) - 1):
            # Signal generated at close of bar i
            signal_time = df_1h.index[i]
            entry_time = df_1h.index[i+1] # Start of the next bar

            # End of the window we check with precision (end of bar i+1)
            # If we have one more bar after i+1, the window ends at index i+2
            if i < len(df_1h) - 2:
                next_bar_end = df_1h.index[i+2]
            else:
                next_bar_end = df_1h.index[-1] + pd.Timedelta(hours=1)

            signal = signals.iloc[i]

            # Sub-data for the bar where we enter and stay (bar i+1)
            # We must NOT use any data from bar i (the signal bar)
            sub_precision = df_precision.loc[entry_time : next_bar_end - pd.Timedelta(seconds=1)]

            if sub_precision.empty:
                 # Fallback to 1h bar i+1 if no precision data
                 sub_precision = df_1h.iloc[i+1:i+2]

            for t_prec, row_prec in sub_precision.iterrows():
                # 1. Check Exit
                if self.position != 0:
                    exit_price = None
                    if self.position == 1:
                        if row_prec['low'] <= self.sl: exit_price = self.sl
                        elif row_prec['high'] >= self.tp: exit_price = self.tp
                    else:
                        if row_prec['high'] >= self.sl: exit_price = self.sl
                        elif row_prec['low'] <= self.tp: exit_price = self.tp

                    if exit_price:
                        self._close_pos(exit_price, t_prec, "Exit")
                        if self.balance <= 0: return self._results()

                # 2. Check Entry Signal
                # We enter on the OPEN of the first precision bar of the bar i+1
                if self.position == 0 and t_prec == entry_time:
                    if signal != 0 and self.balance > 0:
                        self._open_pos(signal, row_prec['open'], t_prec, tp_pct, sl_pct, margin_pct)

            self.equity_curve.append(self.balance)

        return self._results()

    def _results(self):
        if not self.trades: return {"total_return_pct": 0, "n_trades": 0, "win_rate": 0, "best_60d_roi": 0}
        final_roi = (self.balance - self.initial_balance) / self.initial_balance * 100
        equity_df = pd.Series(self.equity_curve)
        if len(equity_df) > 1440:
            rolling_roi = (equity_df / equity_df.shift(1440) - 1) * 100
            best_60d = rolling_roi.max()
        else:
            best_60d = final_roi
        trades_df = pd.DataFrame([t for t in self.trades if 'pnl' in t])
        wr = len(trades_df[trades_df['pnl'] > 0]) / len(trades_df) if not trades_df.empty else 0
        return {'final_balance': self.balance, 'total_return_pct': final_roi, 'best_60d_roi': best_60d, 'n_trades': len(trades_df), 'win_rate': wr, 'trades': trades_df}
