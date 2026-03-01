import pandas as pd
import numpy as np

class Backtester:
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

    def _open_pos(self, side, price, time, tp_pct, sl_pct):
        self.position = side
        self.entry_price = price

        # RISK MANAGEMENT: Use only 10% of balance as margin
        # This prevents instant liquidation and allows more trades
        self.margin_at_entry = self.balance * 0.1

        pos_value = self.margin_at_entry * self.leverage
        entry_fee = pos_value * self.fee

        if self.balance - entry_fee <= 0:
            return # Can't afford fee

        self.balance -= entry_fee

        if side == 1:
            self.tp = price * (1 + tp_pct)
            self.sl = price * (1 - sl_pct)
        else:
            self.tp = price * (1 - tp_pct)
            self.sl = price * (1 + sl_pct)

        self.trades.append({
            'entry_time': time,
            'entry_price': price,
            'side': 'LONG' if side == 1 else 'SHORT',
            'margin': self.margin_at_entry,
            'tp_price': self.tp,
            'sl_price': self.sl
        })

    def _close_pos(self, price, time, reason):
        pos_value_entry = self.margin_at_entry * self.leverage

        pnl_pct_move = self.position * (price / self.entry_price - 1)
        pnl_amount = pnl_pct_move * pos_value_entry

        exit_fee = (pos_value_entry + pnl_amount) * self.fee

        self.balance += pnl_amount - exit_fee

        # If PnL wiped out the margin plus some, cap balance at 0
        if self.balance < 0:
            self.balance = 0

        self.trades[-1].update({
            'exit_time': time,
            'exit_price': price,
            'pnl': pnl_amount - exit_fee,
            'pnl_pct': (pnl_amount - exit_fee) / self.margin_at_entry,
            'reason': reason
        })
        self.position = 0

        if self.balance <= 0:
            return True # Liquidated
        return False

    def run_backtest(self, df, signals, tp_pct=0.02, sl_pct=0.01):
        self.balance = self.initial_balance
        self.position = 0
        self.trades = []
        self.equity_curve = []

        for i in range(len(df)):
            current_price = df['close'].iloc[i]
            current_high = df['high'].iloc[i]
            current_low = df['low'].iloc[i]
            current_time = df.index[i]
            signal = signals.iloc[i]

            if self.position != 0:
                exit_price = None
                exit_reason = None

                if self.position == 1: # Long
                    if current_low <= self.sl:
                        exit_price = self.sl
                        exit_reason = "SL"
                    elif current_high >= self.tp:
                        exit_price = self.tp
                        exit_reason = "TP"
                elif self.position == -1: # Short
                    if current_high >= self.sl:
                        exit_price = self.sl
                        exit_reason = "SL"
                    elif current_low <= self.tp:
                        exit_price = self.tp
                        exit_reason = "TP"

                if exit_price:
                    if self._close_pos(exit_price, current_time, exit_reason):
                        self.equity_curve.extend([0] * (len(df) - len(self.equity_curve)))
                        break

            if self.position == 0 and signal != 0 and self.balance > 0:
                self._open_pos(signal, current_price, current_time, tp_pct, sl_pct)

            self.equity_curve.append(self.balance)

        return self._get_results()

    def _get_results(self):
        if not self.trades:
            return {"total_return_pct": 0, "n_trades": 0, "sharpe_ratio": 0, "max_drawdown_pct": 0, "final_balance": self.balance}

        trades_df = pd.DataFrame([t for t in self.trades if 'pnl' in t])
        if trades_df.empty:
             return {"total_return_pct": 0, "n_trades": 0, "sharpe_ratio": 0, "max_drawdown_pct": 0, "final_balance": self.balance}

        total_return_pct = (self.balance - self.initial_balance) / self.initial_balance * 100
        win_rate = len(trades_df[trades_df['pnl'] > 0]) / len(trades_df)

        equity_series = pd.Series(self.equity_curve)
        returns = equity_series.pct_change().fillna(0)

        sharpe = (returns.mean() / returns.std() * np.sqrt(24 * 365)) if returns.std() != 0 else 0

        roll_max = equity_series.cummax()
        drawdown = (equity_series - roll_max) / roll_max
        max_drawdown_pct = drawdown.min() * 100

        return {
            'initial_balance': self.initial_balance,
            'final_balance': self.balance,
            'total_return_pct': total_return_pct,
            'n_trades': len(trades_df),
            'win_rate': win_rate,
            'sharpe_ratio': sharpe,
            'max_drawdown_pct': max_drawdown_pct,
            'trades': trades_df,
            'equity_curve': self.equity_curve
        }
