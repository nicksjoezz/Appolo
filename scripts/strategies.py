import pandas as pd
import pandas_ta as ta
import numpy as np

# --- 1. Bollinger Band Width Expansion (Heavy ROI Winner) ---
def bb_width_expansion_strategy(df, length=20, std=2.0):
    df = df.copy()
    bb = ta.bbands(df['close'], length=length, std=std)
    width_col = [c for c in bb.columns if 'BBB' in c][0]
    u_col = [c for c in bb.columns if 'BBU' in c][0]
    l_col = [c for c in bb.columns if 'BBL' in c][0]
    adx = ta.adx(df['high'], df['low'], df['close'])['ADX_14']
    signals = pd.Series(0, index=df.index)
    expanding = bb[width_col] > bb[width_col].shift(1)
    # Long: Price breaks Upper BB + Width Increasing + Trending (ADX > 25)
    buy_mask = (df['close'] > bb[u_col]) & expanding & (adx > 25)
    # Short: Price breaks Lower BB + Width Increasing + Trending
    sell_mask = (df['close'] < bb[l_col]) & expanding & (adx > 25)
    signals[buy_mask & (~buy_mask.shift(1).fillna(False))] = 1
    signals[sell_mask & (~sell_mask.shift(1).fillna(False))] = -1
    return signals

# --- 2. RSI Momentum Scalper (High Frequency) ---
def rsi_momentum_scalper(df, rsi_len=7, ema_len=50):
    df = df.copy()
    df['rsi'] = ta.rsi(df['close'], length=rsi_len)
    df['ema'] = ta.ema(df['close'], length=ema_len)
    signals = pd.Series(0, index=df.index)
    buy_mask = (df['close'] > df['ema']) & (df['rsi'] > 50) & (df['rsi'].shift(1) <= 50)
    sell_mask = (df['close'] < df['ema']) & (df['rsi'] < 50) & (df['rsi'].shift(1) >= 50)
    signals[buy_mask] = 1
    signals[sell_mask] = -1
    return signals

# --- 3. Aggressive Donchian (Trend Breakout) ---
def aggressive_donchian_strategy(df, length=10):
    df = df.copy()
    df['upper'] = df['high'].rolling(window=length).max().shift(1)
    df['lower'] = df['low'].rolling(window=length).min().shift(1)
    adx = ta.adx(df['high'], df['low'], df['close'])['ADX_14']
    signals = pd.Series(0, index=df.index)
    buy_mask = (df['close'] > df['upper']) & (adx > 25)
    sell_mask = (df['close'] < df['lower']) & (adx > 25)
    signals[buy_mask] = 1
    signals[sell_mask] = -1
    return signals

# --- 4. Volume-Weighted MACD (Volume Confirmed) ---
def vw_macd_strategy(df):
    df = df.copy()
    df['vw_close'] = df['close'] * df['volume']
    ema12 = ta.ema(df['vw_close'], length=12) / ta.ema(df['volume'], length=12)
    ema26 = ta.ema(df['vw_close'], length=26) / ta.ema(df['volume'], length=26)
    macd = ema12 - ema26
    signal_line = ta.ema(macd, length=9)
    hist = macd - signal_line
    adx = ta.adx(df['high'], df['low'], df['close'])['ADX_14']
    signals = pd.Series(0, index=df.index)
    buy_mask = (hist > 0) & (hist.shift(1) <= 0) & (adx > 25)
    sell_mask = (hist < 0) & (hist.shift(1) >= 0) & (adx > 25)
    signals[buy_mask] = 1
    signals[sell_mask] = -1
    return signals

# --- 5. Filtered IMBA Algo Trend (Best Stability) ---
def imba_algo_trend_filtered(df, sensitivity=20, ema_filter=True, ema_len=200, trend_confirmation=True, dmi_filter=True):
    df = df.copy()
    length = int(max(1, sensitivity * 10))
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
    if dmi_filter:
        adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
        can_long &= (adx_df['DMP_14'] > adx_df['DMN_14'])
        can_short &= (adx_df['DMN_14'] > adx_df['DMP_14'])
    if trend_confirmation:
        # 3-bar confirmation
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
