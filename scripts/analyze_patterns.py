import pandas as pd
import pandas_ta as ta
from strategies import imba_algo_trend_filtered
from mtf_backtester import MTFBacktester

def analyze_patterns():
    df_1h = pd.read_csv('data/ROSEUSDT_1h_3y.csv', index_col='timestamp', parse_dates=True)
    df_5m = pd.read_csv('data/ROSEUSDT_5m_1y.csv', index_col='timestamp', parse_dates=True)
    df_1h_sub = df_1h.loc[df_5m.index[0] : df_5m.index[-1]]

    signals = imba_algo_trend_filtered(df_1h_sub, sensitivity=20, ema_filter=False)

    df_1h_sub = df_1h_sub.copy()
    df_1h_sub['rsi'] = ta.rsi(df_1h_sub['close'], length=14)
    adx_df = ta.adx(df_1h_sub['high'], df_1h_sub['low'], df_1h_sub['close'], length=14)
    df_1h_sub['adx'] = adx_df['ADX_14']
    df_1h_sub['dmp'] = adx_df['DMP_14']
    df_1h_sub['dmn'] = adx_df['DMN_14']
    df_1h_sub['atr_pct'] = ta.atr(df_1h_sub['high'], df_1h_sub['low'], df_1h_sub['close'], length=14) / df_1h_sub['close']

    bt = MTFBacktester(leverage=30)
    # Target 10% ROI
    res = bt.run_backtest(df_1h_sub, signals, df_5m, tp_pct=0.10, sl_pct=0.01, margin_pct=0.1)

    trades = res['trades']
    trades['entry_time'] = pd.to_datetime(trades['entry_time'])
    merged = pd.merge(trades, df_1h_sub, left_on='entry_time', right_index=True)

    # Winners = TP Hit
    # Losers = SL Hit

    print("\nMULTIVARIATE PATTERN ANALYSIS")
    print("="*40)

    # Check "High ADX + Moderate RSI"
    sub = merged[(merged['adx'] > 20) & (merged['adx'] < 40) & (merged['rsi'] > 45) & (merged['rsi'] < 65)]
    if not sub.empty:
        wr = len(sub[sub['pnl']>0])/len(sub)
        print(f"ADX (20-40) + RSI (45-65): WR {wr:.2%} (n={len(sub)})")

    # Check "DMP > DMN" for Longs, etc. (Directional filter)
    longs = merged[merged['side'] == 'LONG']
    sub_long = longs[longs['dmp'] > longs['dmn']]
    if not sub_long.empty:
        wr = len(sub_long[sub_long['pnl']>0])/len(sub_long)
        print(f"Longs where DMP > DMN: WR {wr:.2%} (n={len(sub_long)})")

    shorts = merged[merged['side'] == 'SHORT']
    sub_short = shorts[shorts['dmn'] > shorts['dmp']]
    if not sub_short.empty:
        wr = len(sub_short[sub_short['pnl']>0])/len(sub_short)
        print(f"Shorts where DMN > DMP: WR {wr:.2%} (n={len(sub_short)})")

if __name__ == "__main__":
    analyze_patterns()
