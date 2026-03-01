import pandas as pd
import pandas_ta as ta
import numpy as np

# --- 1. UT Bot Indicator ---
def ut_bot_signals(df, key_value=1.0, atr_period=10):
    df = df.copy()
    atr = ta.atr(df['high'], df['low'], df['close'], length=atr_period)
    nLoss = key_value * atr
    src = df['close']
    trailing_stop = pd.Series(0.0, index=df.index)
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
    buy = (src > trailing_stop) & (src.shift(1) <= trailing_stop.shift(1))
    sell = (src < trailing_stop) & (src.shift(1) >= trailing_stop.shift(1))
    signals = pd.Series(0, index=df.index)
    signals[buy] = 1
    signals[sell] = -1
    return signals

# --- 2. IMBA + UT Bot Combo ---
def imba_ut_bot_strategy(df, imba_sens=20, ut_key=5.0, ut_atr=10):
    df = df.copy()
    length = int(max(1, imba_sens * 10))
    high_line = df['high'].rolling(window=length).max()
    low_line = df['low'].rolling(window=length).min()
    imba_trend_line = high_line - (high_line - low_line) * 0.5
    is_imba_uptrend = df['close'] > imba_trend_line
    is_imba_downtrend = df['close'] < imba_trend_line
    ut_signals = ut_bot_signals(df, key_value=ut_key, atr_period=ut_atr)
    final_signals = pd.Series(0, index=df.index)
    final_signals[(ut_signals == 1) & is_imba_uptrend] = 1
    final_signals[(ut_signals == -1) & is_imba_downtrend] = -1
    return final_signals, ut_signals

# --- 3. Filtered IMBA (Balanced Winner) ---
def imba_algo_trend_filtered(df, sensitivity=20, ema_len=200):
    df = df.copy()
    length = int(max(1, sensitivity * 10))
    high_line = df['high'].rolling(window=length).max()
    low_line = df['low'].rolling(window=length).min()
    imba_trend_line = high_line - (high_line - low_line) * 0.5
    is_imba_uptrend = df['close'] > imba_trend_line
    is_imba_downtrend = df['close'] < imba_trend_line
    df['ema'] = ta.ema(df['close'], length=ema_len)
    adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
    can_long = (df['close'] > df['ema']) & (adx_df['DMP_14'] > adx_df['DMN_14'])
    can_short = (df['close'] < df['ema']) & (adx_df['DMN_14'] > adx_df['DMP_14'])
    # 3-bar confirmation
    imba_uptrend_count = is_imba_uptrend.rolling(3).sum()
    imba_downtrend_count = is_imba_downtrend.rolling(3).sum()
    buy_mask = (imba_uptrend_count == 3) & (imba_uptrend_count.shift(1) == 2) & can_long
    sell_mask = (imba_downtrend_count == 3) & (imba_downtrend_count.shift(1) == 2) & can_short
    signals = pd.Series(0, index=df.index)
    signals[buy_mask] = 1
    signals[sell_mask] = -1
    return signals

# --- 4. BB Width Expansion (Explosive Winner) ---
def bb_width_expansion_strategy(df):
    df = df.copy()
    bb = ta.bbands(df['close'], length=20, std=2)
    width_col = [c for c in bb.columns if 'BBB' in c][0]
    u_col = [c for c in bb.columns if 'BBU' in c][0]
    l_col = [c for c in bb.columns if 'BBL' in c][0]
    adx = ta.adx(df['high'], df['low'], df['close'])['ADX_14']
    expanding = bb[width_col] > bb[width_col].shift(1)
    buy_mask = (df['close'] > bb[u_col]) & expanding & (adx > 25)
    sell_mask = (df['close'] < bb[l_col]) & expanding & (adx > 25)
    signals = pd.Series(0, index=df.index)
    signals[buy_mask & (~buy_mask.shift(1).fillna(False))] = 1
    signals[sell_mask & (~sell_mask.shift(1).fillna(False))] = -1
    return signals
