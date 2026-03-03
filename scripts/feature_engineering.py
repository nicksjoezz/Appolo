import pandas as pd
import pandas_ta as ta
import numpy as np

def generate_features(df):
    """Generate technical indicators for ML analysis."""
    # 1. Moving Averages
    for p in [9, 21, 50, 100, 200]:
        df[f'ema_{p}'] = ta.ema(df['close'], length=p)
        df[f'sma_{p}'] = ta.sma(df['close'], length=p)
        df[f'dist_ema_{p}'] = (df['close'] - df[f'ema_{p}']) / df[f'ema_{p}']

    # 2. Oscillators
    df['rsi'] = ta.rsi(df['close'], length=14)

    stoch = ta.stoch(df['high'], df['low'], df['close'])
    df = pd.concat([df, stoch], axis=1)

    df['cci'] = ta.cci(df['high'], df['low'], df['close'], length=20)
    df['mfi'] = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14)
    df['willr'] = ta.willr(df['high'], df['low'], df['close'], length=14)

    # 3. Volatility
    bbands = ta.bbands(df['close'], length=20, std=2)
    df = pd.concat([df, bbands], axis=1)
    u_col = [c for c in bbands.columns if 'BBU' in c][0]
    l_col = [c for c in bbands.columns if 'BBL' in c][0]
    m_col = [c for c in bbands.columns if 'BBM' in c][0]
    df['bb_width'] = (df[u_col] - df[l_col]) / df[m_col]

    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    df['natr'] = ta.natr(df['high'], df['low'], df['close'], length=14)

    kc = ta.kc(df['high'], df['low'], df['close'], length=20, scalar=2)
    df = pd.concat([df, kc], axis=1)

    # 4. Trend/Momentum
    adx = ta.adx(df['high'], df['low'], df['close'], length=14)
    df = pd.concat([df, adx], axis=1)

    macd = ta.macd(df['close'])
    df = pd.concat([df, macd], axis=1)

    st = ta.supertrend(df['high'], df['low'], df['close'])
    st_col = [c for c in st.columns if 'SUPERT_' in c][0]
    df['supertrend'] = st[st_col]
    df['dist_super'] = (df['close'] - df['supertrend']) / df['supertrend']

    df['dpo'] = ta.dpo(df['close'], length=20)
    df['mom'] = ta.mom(df['close'], length=10)
    df['roc'] = ta.roc(df['close'], length=10)

    # 5. Volume
    df['obv'] = ta.obv(df['close'], df['volume'])
    df['efi'] = ta.efi(df['close'], df['volume'], length=13)
    df['ad'] = ta.ad(df['high'], df['low'], df['close'], df['volume'])
    df['cmf'] = ta.cmf(df['high'], df['low'], df['close'], df['volume'], length=20)

    # 6. Candlestick/Statistical
    df['vol_z'] = (df['volume'] - df['volume'].rolling(20).mean()) / df['volume'].rolling(20).std()
    df['range'] = (df['high'] - df['low']) / df['low']
    df['body'] = (df['close'] - df['open']) / df['open']
    df['shadow_up'] = (df['high'] - np.maximum(df['close'], df['open'])) / df['low']
    df['shadow_low'] = (np.minimum(df['close'], df['open']) - df['low']) / df['low']

    # 7. Daily Context
    df['day'] = df.index.date
    df['daily_open'] = df.groupby('day')['open'].transform('first')
    df['dist_daily_open'] = (df['close'] - df['daily_open']) / df['daily_open']
    df['hour'] = df.index.hour

    return df

if __name__ == "__main__":
    print("Loading data...")
    df = pd.read_csv('data/ROSEUSDT_15m_3y.csv', index_col='timestamp', parse_dates=True)
    print("Generating features...")
    df_feat = generate_features(df)
    print(f"Features generated: {df_feat.shape[1]}")
    df_feat = df_feat.dropna()
    print(f"Rows after dropping NaNs: {len(df_feat)}")
    df_feat.to_pickle('data/ROSEUSDT_15m_features.pkl')
    print("Saved features to data/ROSEUSDT_15m_features.pkl")
