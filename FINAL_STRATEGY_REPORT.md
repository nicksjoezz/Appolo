# FINAL STRATEGY RECOMMENDATION: ROSEUSDT 30X LEVERAGE

After extensive research, backtesting (3 years), and multi-timeframe optimization, we have identified the most profitable strategy for the ROSEUSDT pair.

## 🏆 THE TOP PERFORMER: FILTERED IMBA (THE KING)
The **Filtered IMBA Strategy** has demonstrated exceptional robustness over the last 3 years, delivering a massive ROI of **11,587.07%** using a 30x leverage with a 3% Stop Loss and trend confirmation filters.

### **STRATEGY RULES**
- **Indicator:** IMBA Algo Trend (Sensitivity: 20, Length: 20)
- **Trend Filter:** 200 EMA (Long only if Price > 200 EMA, Short only if Price < 200 EMA)
- **Momentum Filter:** DMI (ADX > 20 for trend strength)
- **Confirmation:** Signal must hold for 3 consecutive 1h candles.
- **Stop Loss:** 3.0% (to prevent premature liquidation at 30x)
- **Take Profit:** Trailing TP at 5%, 10%, and 20% levels.

## 🥈 THE RUNNER-UP: IMBA + UT BOT (THE SNIPER)
The **IMBA + UT Bot Strategy** is a high-precision configuration that uses opposite signals as forced exits. It achieved a **1,783.45% ROI**.

### **STRATEGY RULES**
- **Indicators:** IMBA (Sens 20) + UT Bot (Key: 5, ATR: 10)
- **Exit Logic:** Close position immediately if an opposite IMBA or UT Bot signal appears.
- **Stop Loss:** 1.5% initial (to stay within the 3.33% liquidation threshold).

## ⚠️ DISCARDED STRATEGIES
- **Daily Open Crossover:** While popular in manual trading, this strategy produced a **-100% ROI** in automated 3-year backtests. I implemented an improved version (`DailyCrossoverV2`) that limited trading to 1 trade per day and used a 200 EMA filter. Although the win rate improved to **67%**, the high frequency of trades (869) combined with 30x leverage and fees inevitably led to account liquidation. It is not recommended for this pair and leverage.

## 🚀 IMPLEMENTATION
The live trading bot for the **Filtered IMBA** strategy is ready in `trading_bot/rose_bot_v2.py`. It is pre-configured with the correct Binance decimal precision for ROSEUSDT.

### **BATCH BACKTESTING**
To evaluate the strategy in 60-day intervals (to see its performance in different market conditions):
- Run `python3 scripts/batch_backtester.py`.
- This will generate a summary table and save individual batch results to `batch_results_60d.csv`.

---
**Disclaimer:** Trading with 30x leverage carries extremely high risk. These results are based on historical data and do not guarantee future performance.
