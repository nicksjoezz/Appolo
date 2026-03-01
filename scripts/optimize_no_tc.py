import pandas as pd
import numpy as np
from backtester import Backtester
from strategies import imba_algo_trend_filtered
import sys

def optimize_no_tc():
    df_1h = pd.read_csv('data/ROSEUSDT_1h.csv', index_col='timestamp', parse_dates=True)

    sensitivity = 18
    tp = 0.05
    sl = 0.01
    leverage = 30
    margin_pct = 0.1

    results = []

    print("Optimizing Filters (No Trend Confirmation)...", file=sys.stderr)

    # 1. EMA Filters
    for el in [100, 200, 300, 500]:
        signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity, ema_filter=True, ema_len=el, trend_confirmation=False)
        bt = Backtester(leverage=leverage)
        res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
        results.append({'type': f'EMA_{el}', 'res': res})

    # 2. RSI Filters
    for rc in [(14, 70, 30), (14, 60, 40)]:
        signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity, ema_filter=False, rsi_filter=True, rsi_len=rc[0], rsi_ob=rc[1], rsi_os=rc[2], trend_confirmation=False)
        bt = Backtester(leverage=leverage)
        res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
        results.append({'type': f'RSI_{rc[1]}', 'res': res})

    # 3. MACD Filter
    signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity, ema_filter=False, macd_filter=True, trend_confirmation=False)
    bt = Backtester(leverage=leverage)
    res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
    results.append({'type': 'MACD', 'res': res})

    # 4. Volatility Filter
    signals = imba_algo_trend_filtered(df_1h, sensitivity=sensitivity, ema_filter=False, vol_filter=True, trend_confirmation=False)
    bt = Backtester(leverage=leverage)
    res = bt.run_backtest(df_1h, signals, tp_pct=tp, sl_pct=sl, margin_pct=margin_pct)
    results.append({'type': 'VOL', 'res': res})

    # Sort by Win Rate and Sharpe
    results.sort(key=lambda x: (x['res']['win_rate'], x['res']['sharpe_ratio']), reverse=True)

    print("\nTOP NO-TC RESULTS (SENS 18)")
    print("="*60)
    for i, item in enumerate(results[:10]):
        r = item['res']
        print(f"{i+1}. Filter: {item['type']}")
        print(f"   ROI: {r['total_return_pct']:.2f}% | Win Rate: {r['win_rate']:.2%} | MDD: {r['max_drawdown_pct']:.2f}%")
        print(f"   Sharpe: {r['sharpe_ratio']:.4f} | Trades: {r['n_trades']}")
        print("-" * 50)

if __name__ == "__main__":
    optimize_no_tc()
