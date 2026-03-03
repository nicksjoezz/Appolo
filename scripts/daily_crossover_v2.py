import pandas as pd
import numpy as np
import pandas_ta as ta

class DailyCrossoverV2:
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
        # FIXED MARGIN instead of compounding for risky strategy
        self.margin_at_entry = self.initial_balance * 0.05
        if self.balance < self.margin_at_entry:
            self.margin_at_entry = self.balance

        pos_value = self.margin_at_entry * self.leverage
        self.balance -= pos_value * self.fee
        # Wider SL (3%) for 15m timeframe
        self.sl = price * (0.97 if side == 1 else 1.03)
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

        # Trend filter
        df['ema200'] = ta.ema(df['close'], length=200)

        self.balance = self.initial_balance
        self.position = 0
        self.trades = []

        last_trade_day = None

        for i in range(len(df)):
            t = df.index[i]
            row = df.iloc[i]
            current_day = row['day']

            # --- EXIT LOGIC ---
            if self.position != 0:
                move_pct = self.position * (row['close'] / self.entry_price - 1)

                # Trailing logic
                if self.tp_stage == 0 and move_pct >= 0.01:
                    self.tp_stage = 1
                    self.sl = self.entry_price * (1.002 if self.position == 1 else 0.998)
                elif self.tp_stage == 1 and move_pct >= 0.02:
                    self.tp_stage = 2
                    self.sl = self.entry_price * (1.01 if self.position == 1 else 0.99)

                if move_pct >= 0.03:
                    self._close_pos(self.entry_price * (1 + self.position*0.03), t, "TP_QUICK")

                if self.position != 0:
                    if self.position == 1:
                        if row['low'] <= self.sl: self._close_pos(self.sl, t, "SL/Trailing")
                    else:
                        if row['high'] >= self.sl: self._close_pos(self.sl, t, "SL/Trailing")

            # --- ENTRY LOGIC ---
            # Rule: Only ONE trade per day
            if self.position == 0 and current_day != last_trade_day:
                # LONG: Cross Daily Open + Above EMA 200
                if row['open'] < row['daily_open'] and row['close'] > row['daily_open']:
                    if not pd.isna(row['ema200']) and row['close'] > row['ema200']:
                        self._open_pos(1, row['close'], t, margin_pct)
                        last_trade_day = current_day
                # SHORT: Cross Daily Open + Below EMA 200
                elif row['open'] > row['daily_open'] and row['close'] < row['daily_open']:
                    if not pd.isna(row['ema200']) and row['close'] < row['ema200']:
                        self._open_pos(-1, row['close'], t, margin_pct)
                        last_trade_day = current_day

        return self._results()

    def _results(self):
        if not self.trades: return {"roi": 0, "n": 0}
        tdf = pd.DataFrame([t for t in self.trades if 'pnl' in t])
        roi = (self.balance - self.initial_balance) / self.initial_balance * 100
        wr = len(tdf[tdf['pnl'] > 0]) / len(tdf) if not tdf.empty else 0
        return {'final_balance': self.balance, 'roi': roi, 'win_rate': wr, 'n_trades': len(tdf), 'trades': tdf}

if __name__ == "__main__":
    df = pd.read_csv('data/ROSEUSDT_15m_3y.csv', index_col='timestamp', parse_dates=True)
    print("Running Improved Daily Crossover V2 (1 Trade/Day + EMA Filter)...")
    res = DailyCrossoverV2().run_backtest(df)
    print(f"3-Year ROI: {res['roi']:.2f}% | Win Rate: {res['win_rate']:.2%} | Trades: {res['n_trades']}")
