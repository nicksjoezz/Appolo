import pandas as pd
import numpy as np

class RealisticBacktester:
    def __init__(self, initial_balance=1000, fee=0.0005, leverage=30):
        self.initial_balance = initial_balance
        self.fee = fee
        self.leverage = leverage

    def run_variant(self, df, name, filter_func, sl_pct=0.02, tp_pct=0.04, margin_pct=0.1):
        balance = self.initial_balance
        position = 0
        entry_price = 0
        sl_price = 0
        tp_price = 0
        trades = []
        last_trade_day = None

        for i in range(len(df)):
            row = df.iloc[i]

            # 1. Exit Logic (Intra-bar)
            if position != 0:
                if position == 1:
                    if row['low'] <= sl_price:
                        balance = self._calc_balance(balance, 1, entry_price, sl_price, margin_pct)
                        trades.append(0); position = 0
                    elif row['high'] >= tp_price:
                        balance = self._calc_balance(balance, 1, entry_price, tp_price, margin_pct)
                        trades.append(1); position = 0
                else: # Short
                    if row['high'] >= sl_price:
                        balance = self._calc_balance(balance, -1, entry_price, sl_price, margin_pct)
                        trades.append(0); position = 0
                    elif row['low'] <= tp_price:
                        balance = self._calc_balance(balance, -1, entry_price, tp_price, margin_pct)
                        trades.append(1); position = 0

                if balance <= 0: return {'name': name, 'roi': -100, 'wr': 0, 'n': len(trades)}

            # 2. Entry Logic
            if position == 0 and row['day'] != last_trade_day:
                is_long = row['open'] < row['daily_open'] and row['close'] > row['daily_open']
                is_short = row['open'] > row['daily_open'] and row['close'] < row['daily_open']

                if (is_long or is_short) and filter_func(row, is_long):
                    position = 1 if is_long else -1
                    entry_price = row['close']
                    sl_price = entry_price * (1 - sl_pct if is_long else 1 + sl_pct)
                    tp_price = entry_price * (1 + tp_pct if is_long else 1 - tp_pct)

                    pos_value = balance * margin_pct * self.leverage
                    balance -= pos_value * self.fee
                    last_trade_day = row['day']

        roi = (balance - self.initial_balance) / self.initial_balance * 100
        wr = np.mean(trades) if trades else 0
        return {'name': name, 'roi': roi, 'wr': wr, 'n': len(trades)}

    def _calc_balance(self, balance, side, entry, exit, margin_pct):
        pos_value_entry = balance * margin_pct * self.leverage
        pnl_pct = side * (exit / entry - 1)
        pnl_amount = pnl_pct * pos_value_entry
        exit_fee = (pos_value_entry + pnl_amount) * self.fee
        new_balance = balance + pnl_amount - exit_fee
        return max(0, new_balance)

def run_all_variants():
    df = pd.read_pickle('data/ROSEUSDT_15m_features.pkl')
    bt = RealisticBacktester()

    variants = [
        ('Baseline', lambda r, l: True),
        ('Vol_NATR_1.2', lambda r, l: r['natr'] > 1.2),
        ('Vol_NATR_1.5', lambda r, l: r['natr'] > 1.5),
        ('Trend_EMA_200', lambda r, l: (r['close'] > r['ema_200']) if l else (r['close'] < r['ema_200'])),
        ('RSI_Extreme_40_60', lambda r, l: (r['rsi'] < 40) if l else (r['rsi'] > 60)),
        ('Time_12_16_UTC', lambda r, l: r['hour'] in [12, 13, 14, 15]),
        ('Combo_EMA_NATR', lambda r, l: ((r['close'] > r['ema_200']) if l else (r['close'] < r['ema_200'])) and r['natr'] > 0.8),
        ('ADX_Strength_25', lambda r, l: r['ADX_14'] > 25),
        ('Volume_Z_1.5', lambda r, l: r['vol_z'] > 1.5),
        ('MACD_Confirm', lambda r, l: (r['MACD_12_26_9'] > 0) if l else (r['MACD_12_26_9'] < 0)),
        ('Body_Momentum_0.3%', lambda r, l: abs(r['body']) > 0.003)
    ]

    results = []
    for name, f_func in variants:
        res = bt.run_variant(df, name, f_func)
        results.append(res)
        print(f"Finished {name}: ROI {res['roi']:.2f}% | WR {res['wr']:.2%} | n {res['n']}")

    return pd.DataFrame(results)

if __name__ == "__main__":
    res_df = run_all_variants()
    print("\n--- FINAL COMPARISON ---")
    print(res_df.to_string(index=False))
