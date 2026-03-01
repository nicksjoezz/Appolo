import pandas as pd
import pandas_ta as ta

def ema_cross_strategy(df, fast=9, slow=21):
    df = df.copy()
    df['ema_fast'] = ta.ema(df['close'], length=fast)
    df['ema_slow'] = ta.ema(df['close'], length=slow)
    signals = pd.Series(0, index=df.index)
    long_mask = (df['ema_fast'] > df['ema_slow']) & (df['ema_fast'].shift(1) <= df['ema_slow'].shift(1))
    short_mask = (df['ema_fast'] < df['ema_slow']) & (df['ema_fast'].shift(1) >= df['ema_slow'].shift(1))
    signals[long_mask] = 1
    signals[short_mask] = -1
    return signals

def rsi_bb_strategy(df, rsi_len=14, rsi_ob=70, rsi_os=30, bb_len=20, bb_std=2):
    df = df.copy()
    df['rsi'] = ta.rsi(df['close'], length=rsi_len)
    bb = ta.bbands(df['close'], length=bb_len, std=bb_std)
    df = pd.concat([df, bb], axis=1)
    l_col = f'BBL_{bb_len}_{bb_std}'
    u_col = f'BBU_{bb_len}_{bb_std}'
    if l_col not in df.columns:
        for col in df.columns:
            if col.startswith(f'BBL_{bb_len}'): l_col = col
            if col.startswith(f'BBU_{bb_len}'): u_col = col
    signals = pd.Series(0, index=df.index)
    long_mask = (df['rsi'] < rsi_os) & (df['close'] < df[l_col])
    short_mask = (df['rsi'] > rsi_ob) & (df['close'] > df[u_col])
    signals[long_mask & (~long_mask.shift(1).fillna(False))] = 1
    signals[short_mask & (~short_mask.shift(1).fillna(False))] = -1
    return signals

def daily_high_low_breakout(df):
    df = df.copy()
    daily = df.resample('D').agg({'high': 'max', 'low': 'min'})
    daily_h = daily['high'].shift(1).reindex(df.index, method='ffill')
    daily_l = daily['low'].shift(1).reindex(df.index, method='ffill')
    signals = pd.Series(0, index=df.index)
    long_mask = (df['close'] > daily_h) & (df['close'].shift(1) <= daily_h.shift(1))
    short_mask = (df['close'] < daily_l) & (df['close'].shift(1) >= daily_l.shift(1))
    signals[long_mask] = 1
    signals[short_mask] = -1
    return signals

def supertrend_strategy(df, length=10, multiplier=3):
    df = df.copy()
    st = ta.supertrend(df['high'], df['low'], df['close'], length=length, multiplier=multiplier)
    d_col = [c for c in st.columns if c.startswith('SUPERTd')][0]
    signals = pd.Series(0, index=df.index)
    signals[ (st[d_col] == 1) & (st[d_col].shift(1) == -1) ] = 1
    signals[ (st[d_col] == -1) & (st[d_col].shift(1) == 1) ] = -1
    return signals

def macd_strategy(df, fast=12, slow=26, signal=9):
    df = df.copy()
    macd = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
    h_col = [c for c in macd.columns if c.startswith('MACDh')][0]
    signals = pd.Series(0, index=df.index)
    signals[ (macd[h_col] > 0) & (macd[h_col].shift(1) <= 0) ] = 1
    signals[ (macd[h_col] < 0) & (macd[h_col].shift(1) >= 0) ] = -1
    return signals
