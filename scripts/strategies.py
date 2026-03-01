import pandas as pd
import pandas_ta as ta
import numpy as np

def imba_algo_trend_filtered(df, sensitivity=18, ema_filter=True, ema_len=200, rsi_filter=False, rsi_len=14, rsi_ob=70, rsi_os=30, macd_filter=False, trend_confirmation=False, bb_filter=False, vol_filter=False, trailing_sl=False):
    df = df.copy()
    length = int(max(1, sensitivity * 10))

    # IMBA Base Calculation
    high_line = df['high'].rolling(window=length).max()
    low_line = df['low'].rolling(window=length).min()
    imba_trend_line = high_line - (high_line - low_line) * 0.5

    is_imba_uptrend = df['close'] > imba_trend_line
    is_imba_downtrend = df['close'] < imba_trend_line

    can_long = pd.Series(True, index=df.index)
    can_short = pd.Series(True, index=df.index)

    if ema_filter:
        df['ema'] = ta.ema(df['close'], length=ema_len)
        can_long &= (df['close'] > df['ema'])
        can_short &= (df['close'] < df['ema'])

    if rsi_filter:
        df['rsi'] = ta.rsi(df['close'], length=rsi_len)
        can_long &= (df['rsi'] < rsi_ob)
        can_short &= (df['rsi'] > rsi_os)

    if macd_filter:
        macd = ta.macd(df['close'])
        hist_col = [c for c in macd.columns if 'MACDh' in c][0]
        can_long &= (macd[hist_col] > 0)
        can_short &= (macd[hist_col] < 0)

    if vol_filter:
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        df['atr_sma'] = ta.sma(df['atr'], length=20)
        can_long &= (df['atr'] > df['atr_sma'])
        can_short &= (df['atr'] > df['atr_sma'])

    if trend_confirmation:
        imba_uptrend_count = is_imba_uptrend.rolling(3).sum()
        imba_downtrend_count = is_imba_downtrend.rolling(3).sum()
        buy_mask = (imba_uptrend_count == 3) & (imba_uptrend_count.shift(1) == 2) & can_long
        sell_mask = (imba_downtrend_count == 3) & (imba_downtrend_count.shift(1) == 2) & can_short
    else:
        buy_mask = is_imba_uptrend & (~is_imba_uptrend.shift(1).fillna(False)) & can_long
        sell_mask = is_imba_downtrend & (~is_imba_downtrend.shift(1).fillna(False)) & can_short

    signals = pd.Series(0, index=df.index)
    signals[buy_mask] = 1
    signals[sell_mask] = -1

    return signals

def imba_algo_trend(df, sensitivity=18):
    return imba_algo_trend_filtered(df, sensitivity=sensitivity, ema_filter=False, rsi_filter=False)

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

def bb_breakout_aggressive(df, length=20, std=2):
    df = df.copy()
    bb = ta.bbands(df['close'], length=length, std=std)
    df = pd.concat([df, bb], axis=1)
    l_col = [c for c in bb.columns if c.startswith('BBL')][0]
    u_col = [c for c in bb.columns if c.startswith('BBU')][0]
    signals = pd.Series(0, index=df.index)
    signals[ (df['close'] > df[u_col]) & (df['close'].shift(1) <= df[u_col].shift(1)) ] = 1
    signals[ (df['close'] < df[l_col]) & (df['close'].shift(1) >= df[l_col].shift(1)) ] = -1
    return signals

def volatility_trend(df, length=10, vol_mult=2):
    df = df.copy()
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=length)
    df['sma'] = ta.sma(df['close'], length=length)
    signals = pd.Series(0, index=df.index)
    long_mask = (df['close'] > df['sma'] + vol_mult * df['atr'])
    short_mask = (df['close'] < df['sma'] - vol_mult * df['atr'])
    signals[long_mask & (~long_mask.shift(1).fillna(False))] = 1
    signals[short_mask & (~short_mask.shift(1).fillna(False))] = -1
    return signals
