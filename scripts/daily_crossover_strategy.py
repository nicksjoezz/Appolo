import pandas as pd
import numpy as np

class DailyCrossoverBacktester:
    def __init__(self, initial_balance=1000, fee=0.0005, leverage=30):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.fee = fee
        self.leverage = leverage
        self.position = 0
        self.entry_price = 0
        self.margin_at_entry = 0
        self.trades = []
        self.sl = 0
        self.tp_stage = 0

    def _open_pos(self, side, price, time, margin_pct):
        if self.balance <= 0: return
        self.position = side
        self.entry_price = price
        self.margin_at_entry = self.balance * margin_pct
        pos_value = self.margin_at_entry * self.leverage
        self.balance -= pos_value * self.fee
        # Initial SL = 1%
        self.sl = price * (0.99 if side == 1 else 1.01)
        self.tp_stage = 0
        self.trades.append({'entry_time': time, 'entry_price': price, 'side': 'LONG' if side == 1 else 'SHORT', 'margin': self.margin_at_entry})

    def _close_pos(self, price, time, reason):
        pos_value_entry = self.margin_at_entry * self.leverage
        pnl_pct_move = self.position * (price / self.entry_price - 1)
        pnl_amount = pnl_pct_move * pos_value_entry
        self.balance += pnl_amount - (pos_value_entry + pnl_amount) * self.fee
        if self.balance < 0: self.balance = 0
        self.trades[-1].update({'exit_time': time, 'exit_price': price, 'pnl': pnl_amount, 'reason': reason})
        self.position = 0

    def run_backtest(self, df_15m, margin_pct=0.1):
        df = df_15m.copy()
        df['day'] = df.index.date
        df['daily_open'] = df.groupby('day')['open'].transform('first')

        self.balance = self.initial_balance
        self.position = 0
        self.trades = []

        for i in range(len(df)):
            t = df.index[i]
            row = df.iloc[i]

            # --- EXIT LOGIC ---
            if self.position != 0:
                # Trailing logic
                move_pct = self.position * (row['close'] / self.entry_price - 1)

                # Hit 1% TP -> Move SL to +0.2%
                if self.tp_stage == 0 and move_pct >= 0.01:
                    self.tp_stage = 1
                    self.sl = self.entry_price * (1.002 if self.position == 1 else 0.998)
                # Hit 3% TP -> Move SL to +1.5%
                elif self.tp_stage == 1 and move_pct >= 0.03:
                    self.tp_stage = 2
                    self.sl = self.entry_price * (1.015 if self.position == 1 else 0.985)

                # TP Exits
                if move_pct >= 0.10:
                    self._close_pos(self.entry_price * (1 + self.position*0.10), t, "TP4")
                elif move_pct >= 0.05 and self.tp_stage < 3:
                     # Just noted as level 3 in your description. Assuming TP exit at 10% fully.
                     pass

                # SL / Trailing Check
                if self.position != 0:
                    if self.position == 1:
                        if row['low'] <= self.sl: self._close_pos(self.sl, t, "SL/Trailing")
                    else:
                        if row['high'] >= self.sl: self._close_pos(self.sl, t, "SL/Trailing")

            # --- ENTRY LOGIC ---
            if self.position == 0:
                # Buy: 15min Open < Daily Open AND 15min Close > Daily Open
                if row['open'] < row['daily_open'] and row['close'] > row['daily_open']:
                    self._open_pos(1, row['close'], t, margin_pct)
                # Sell: 15min Open > Daily Open AND 15min Close < Daily Open
                elif row['open'] > row['daily_open'] and row['close'] < row['daily_open']:
                    self._open_pos(-1, row['close'], t, margin_pct)

        return self._results()

    def _results(self):
        if not self.trades: return {"roi": 0, "n": 0}
        tdf = pd.DataFrame([t for t in self.trades if 'pnl' in t])
        roi = (self.balance - self.initial_balance) / self.initial_balance * 100
        wr = len(tdf[tdf['pnl'] > 0]) / len(tdf) if not tdf.empty else 0
        return {'final_balance': self.balance, 'roi': roi, 'win_rate': wr, 'n_trades': len(tdf), 'trades': tdf}

if __name__ == "__main__":
    df = pd.read_csv('data/ROSEUSDT_15m_3y.csv', index_col='timestamp', parse_dates=True)
    start_90d = df.index[-1] - pd.Timedelta(days=90)
    df_90d = df.loc[start_90d:]

    res = DailyCrossoverBacktester().run_backtest(df_90d)
    print(f"90-Day ROI: {res['roi']:.2f}% | Win Rate: {res['win_rate']:.2%} | Trades: {res['n_trades']}")
