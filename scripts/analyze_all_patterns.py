import pandas as pd
import pandas_ta as ta
from mtf_backtester import MTFBacktester
from strategies import *

def analyze_all_patterns():
    df_1h = pd.read_csv('data/ROSEUSDT_1h_3y.csv', index_col='timestamp', parse_dates=True)
    df_5m = pd.read_csv('data/ROSEUSDT_5m_1y.csv', index_col='timestamp', parse_dates=True)
    df_1h_sub = df_1h.loc[df_5m.index[0] : df_5m.index[-1]].copy()

    # Pre-calculate common filter indicators
    df_1h_sub['adx'] = ta.adx(df_1h_sub['high'], df_1h_sub['low'], df_1h_sub['close'])['ADX_14']
    df_1h_sub['rsi'] = ta.rsi(df_1h_sub['close'])

    strats = [
        ('High_Vol', high_vol_breakout_strategy),
        ('RSI_Scalp', rsi_momentum_scalper),
        ('VW_MACD', vw_macd_strategy),
        ('BB_Width', bb_width_expansion_strategy),
        ('Agg_Donchian', aggressive_donchian_strategy)
    ]

    for name, s_func in strats:
        signals = s_func(df_1h_sub)
        bt = MTFBacktester(leverage=30)
        res = bt.run_backtest(df_1h_sub, signals, df_5m, tp_pct=0.05, sl_pct=0.015, margin_pct=0.1)

        trades = res['trades']
        if trades.empty: continue
        trades['entry_time'] = pd.to_datetime(trades['entry_time'])
        merged = pd.merge(trades, df_1h_sub, left_on='entry_time', right_index=True)

        winners = merged[merged['pnl'] > 0]
        losers = merged[merged['pnl'] <= 0]

        print(f"\n[{name}] Pattern Analysis:")
        print(f"  Avg ADX - Winners: {winners['adx'].mean():.2f} | Losers: {losers['adx'].mean():.2f}")
        print(f"  Avg RSI - Winners: {winners['rsi'].mean():.2f} | Losers: {losers['rsi'].mean():.2f}")

if __name__ == "__main__":
    analyze_all_patterns()
