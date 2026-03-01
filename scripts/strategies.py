import pandas as pd
import pandas_ta as ta
import numpy as np

def imba_algo_trend_filtered(df, sensitivity=20, ema_filter=False, ema_len=200, rsi_filter=False, rsi_len=14, rsi_ob=70, rsi_os=30, macd_filter=False, trend_confirmation=False, bb_filter=False, vol_filter=False, adx_filter=False, adx_min=20, adx_max=40, dmi_filter=False):
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

    if adx_filter:
        adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
        adx = adx_df['ADX_14']
        can_long &= (adx > adx_min) & (adx < adx_max)
        can_short &= (adx > adx_min) & (adx < adx_max)

    if dmi_filter:
        adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
        dmp = adx_df['DMP_14']
        dmn = adx_df['DMN_14']
        can_long &= (dmp > dmn)
        can_short &= (dmn > dmp)

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
