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
def imba_ut_bot_strategy(df, imba_sens=20, ut_key=5.0, ut_atr=10,
                         ema_filter=False, adx_filter=False, squeeze_filter=False, volume_filter=False):
    df = df.copy()
    length = int(max(1, imba_sens * 10))
    high_line = df['high'].rolling(window=length).max()
    low_line = df['low'].rolling(window=length).min()
    imba_trend_line = high_line - (high_line - low_line) * 0.5
    is_imba_uptrend = df['close'] > imba_trend_line
    is_imba_downtrend = df['close'] < imba_trend_line
    ut_signals = ut_bot_signals(df, key_value=ut_key, atr_period=ut_atr)

    can_long = pd.Series(True, index=df.index)
    can_short = pd.Series(True, index=df.index)
    if ema_filter:
        df['ema_200'] = ta.ema(df['close'], length=200)
        can_long &= (df['close'] > df['ema_200'])
        can_short &= (df['close'] < df['ema_200'])
    if adx_filter:
        adx_df = ta.adx(df['high'], df['low'], df['close'])
        can_long &= (adx_df['ADX_14'] > 25)
        can_short &= (adx_df['ADX_14'] > 25)
    if volume_filter:
        df['vol_ema'] = ta.ema(df['volume'], length=20)
        can_long &= (df['volume'] > df['vol_ema'] * 1.5)
        can_short &= (df['volume'] > df['vol_ema'] * 1.5)
    if squeeze_filter:
        bb = ta.bbands(df['close'], length=20, std=2)
        kc = ta.kc(df['high'], df['low'], df['close'], length=20, scalar=1.5)
        bbu_col = [c for c in bb.columns if 'BBU' in c][0]
        bbl_col = [c for c in bb.columns if 'BBL' in c][0]
        kcu_col = [c for c in kc.columns if 'KCU' in c][0]
        kcl_col = [c for c in kc.columns if 'KCL' in c][0]
        squeeze_on = (bb[bbu_col] < kc[kcu_col]) & (bb[bbl_col] > kc[kcl_col])
        can_long &= ~squeeze_on
        can_short &= ~squeeze_on

    final_signals = pd.Series(0, index=df.index)
    final_signals[(ut_signals == 1) & is_imba_uptrend & can_long] = 1
    final_signals[(ut_signals == -1) & is_imba_downtrend & can_short] = -1
    return final_signals, ut_signals

# --- 3. Filtered IMBA (Winner) ---
def imba_algo_trend_filtered(df, sensitivity=20, ema_filter=True, ema_len=200, trend_confirmation=True, dmi_filter=True, rsi_filter=False, rsi_ob=70, rsi_os=30, macd_filter=False, vol_filter=False):
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
    if rsi_filter:
        df['rsi'] = ta.rsi(df['close'], length=14)
        can_long &= (df['rsi'] < rsi_ob)
        can_short &= (df['rsi'] > rsi_os)
    if macd_filter:
        macd = ta.macd(df['close'])
        h_col = [c for c in macd.columns if 'MACDh' in c][0]
        can_long &= (macd[h_col] > 0)
        can_short &= (macd[h_col] < 0)
    if vol_filter:
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        df['atr_sma'] = ta.sma(df['atr'], length=20)
        can_long &= (df['atr'] > df['atr_sma'])
        can_short &= (df['atr'] > df['atr_sma'])

    if trend_confirmation:
        buy_mask = (is_imba_uptrend.rolling(3).sum() == 3) & (is_imba_uptrend.rolling(3).sum().shift(1) == 2) & can_long
        sell_mask = (is_imba_downtrend.rolling(3).sum() == 3) & (is_imba_downtrend.rolling(3).sum().shift(1) == 2) & can_short
    else:
        buy_mask = is_imba_uptrend & (~is_imba_uptrend.shift(1).fillna(False)) & can_long
        sell_mask = is_imba_downtrend & (~is_imba_downtrend.shift(1).fillna(False)) & can_short

    signals = pd.Series(0, index=df.index)
    signals[buy_mask] = 1
    signals[sell_mask] = -1
    return signals

# --- 4. Explosive Strategies ---
def bb_width_expansion_strategy(df, length=20, std=2.0):
    df = df.copy()
    bb = ta.bbands(df['close'], length=length, std=std)
    width_col = [c for c in bb.columns if 'BBB' in c][0]
    expanding = bb[width_col] > bb[width_col].shift(1)
    adx = ta.adx(df['high'], df['low'], df['close'])['ADX_14']
    buy_mask = (df['close'] > bb[f'BBU_{length}_{std}']) & expanding & (adx > 25)
    sell_mask = (df['close'] < bb[f'BBL_{length}_{std}']) & expanding & (adx > 25)
    signals = pd.Series(0, index=df.index)
    signals[buy_mask & (~buy_mask.shift(1).fillna(False))] = 1
    signals[sell_mask & (~sell_mask.shift(1).fillna(False))] = -1
    return signals

def rsi_momentum_scalper(df, rsi_len=7, ema_len=50):
    df = df.copy()
    df['rsi'] = ta.rsi(df['close'], length=rsi_len)
    df['ema'] = ta.ema(df['close'], length=ema_len)
    buy_mask = (df['close'] > df['ema']) & (df['rsi'] > 50) & (df['rsi'].shift(1) <= 50)
    sell_mask = (df['close'] < df['ema']) & (df['rsi'] < 50) & (df['rsi'].shift(1) >= 50)
    signals = pd.Series(0, index=df.index)
    signals[buy_mask] = 1
    signals[sell_mask] = -1
    return signals

def aggressive_donchian_strategy(df, length=10):
    df = df.copy()
    df['upper'] = df['high'].rolling(window=length).max().shift(1)
    df['lower'] = df['low'].rolling(window=length).min().shift(1)
    adx = ta.adx(df['high'], df['low'], df['close'])['ADX_14']
    buy_mask = (df['close'] > df['upper']) & (adx > 25)
    sell_mask = (df['close'] < df['lower']) & (adx > 25)
    signals = pd.Series(0, index=df.index)
    signals[buy_mask] = 1
    signals[sell_mask] = -1
    return signals

def vw_macd_strategy(df):
    df = df.copy()
    df['vw_close'] = df['close'] * df['volume']
    ema12 = ta.ema(df['vw_close'], length=12) / ta.ema(df['volume'], length=12)
    ema26 = ta.ema(df['vw_close'], length=26) / ta.ema(df['volume'], length=26)
    macd = ema12 - ema26
    sig = ta.ema(macd, length=9)
    hist = macd - sig
    adx = ta.adx(df['high'], df['low'], df['close'])['ADX_14']
    buy_mask = (hist > 0) & (hist.shift(1) <= 0) & (adx > 25)
    sell_mask = (hist < 0) & (hist.shift(1) >= 0) & (adx > 25)
    signals = pd.Series(0, index=df.index)
    signals[buy_mask] = 1
    signals[sell_mask] = -1
    return signals

def high_vol_breakout_strategy(df, length=10, mult=3.0):
    df = df.copy()
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=length)
    df['sma'] = ta.sma(df['close'], length=length)
    buy_mask = (df['close'] > df['sma'] + mult * df['atr'])
    sell_mask = (df['close'] < df['sma'] - mult * df['atr'])
    signals = pd.Series(0, index=df.index)
    signals[buy_mask & (~buy_mask.shift(1).fillna(False))] = 1
    signals[sell_mask & (~sell_mask.shift(1).fillna(False))] = -1
    return signals

def get_analysis_indicators(df):
    df = df.copy()
    df['rsi'] = ta.rsi(df['close'], length=14)
    df['adx'] = ta.adx(df['high'], df['low'], df['close'])['ADX_14']
    df['volume_ema'] = df['volume'] / ta.ema(df['volume'], length=20)
    return df
