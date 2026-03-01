import pandas as pd
import pandas_ta as ta
import numpy as np

def ut_bot_signals(df, key_value=1.0, atr_period=10):
    """
    UT Bot Logic Translation:
    xATR = atr(c)
    nLoss = a * xATR
    xATRTrailingStop = ... (trailing stop logic)
    buy = price > trailing_stop and crossover(price, trailing_stop)
    """
    df = df.copy()
    atr = ta.atr(df['high'], df['low'], df['close'], length=atr_period)
    nLoss = key_value * atr

    src = df['close']
    trailing_stop = pd.Series(0.0, index=df.index)

    # Implementing the trailing stop loop
    for i in range(1, len(df)):
        prev_ts = trailing_stop.iloc[i-1]
        curr_src = src.iloc[i]
        prev_src = src.iloc[i-1]
        curr_loss = nLoss.iloc[i]

        if curr_src > prev_ts and prev_src > prev_ts:
            trailing_stop.iloc[i] = max(prev_ts, curr_src - curr_loss)
        elif curr_src < prev_ts and prev_src < prev_ts:
            trailing_stop.iloc[i] = min(prev_ts, curr_src + curr_loss)
        elif curr_src > prev_ts:
            trailing_stop.iloc[i] = curr_src - curr_loss
        else:
            trailing_stop.iloc[i] = curr_src + curr_loss

    # buy = src > trailing_stop and crossover
    buy = (src > trailing_stop) & (src.shift(1) <= trailing_stop.shift(1))
    sell = (src < trailing_stop) & (src.shift(1) >= trailing_stop.shift(1))

    signals = pd.Series(0, index=df.index)
    signals[buy] = 1
    signals[sell] = -1
    return signals

def imba_ut_bot_strategy(df, imba_sens=20, ut_key=1.0, ut_atr=10):
    df = df.copy()
    # 1. IMBA Trend Filter
    length = int(max(1, imba_sens * 10))
    high_line = df['high'].rolling(window=length).max()
    low_line = df['low'].rolling(window=length).min()
    imba_trend_line = high_line - (high_line - low_line) * 0.5
    is_imba_uptrend = df['close'] > imba_trend_line
    is_imba_downtrend = df['close'] < imba_trend_line

    # 2. UT Bot Signals
    ut_signals = ut_bot_signals(df, key_value=ut_key, atr_period=ut_atr)

    # 3. Combined Logic
    final_signals = pd.Series(0, index=df.index)
    # Entry only if in trend
    final_signals[(ut_signals == 1) & is_imba_uptrend] = 1
    final_signals[(ut_signals == -1) & is_imba_downtrend] = -1

    # Note:backtester needs to handle the "Close on opposite UT signal"
    # We will pass the raw UT signals as "exit signals"
    return final_signals, ut_signals

# ... (rest of the file remains same)
def high_vol_breakout_strategy(df, length=10, mult=3.0):
    df = df.copy()
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=length)
    df['sma'] = ta.sma(df['close'], length=length)
    adx = ta.adx(df['high'], df['low'], df['close'])['ADX_14']
    signals = pd.Series(0, index=df.index)
    buy_mask = (df['close'] > df['sma'] + mult * df['atr']) & (adx > 30)
    sell_mask = (df['close'] < df['sma'] - mult * df['atr']) & (adx > 30)
    signals[buy_mask & (~buy_mask.shift(1).fillna(False))] = 1
    signals[sell_mask & (~sell_mask.shift(1).fillna(False))] = -1
    return signals

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
