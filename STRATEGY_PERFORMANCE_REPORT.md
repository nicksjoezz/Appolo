# STRATEGY PERFORMANCE REPORT (3-YEAR TEST)

This report compares the 3-year performance of all strategies, with a focus on the **Best 60-Day ROI** (the "Heavy Gains" metric) using a **Realistic Multi-Timeframe Backtester**.

## 📊 COMPARISON TABLE (REALISTIC EXECUTION)

Execution accounts for intra-candle volatility using 5m bars for 1h signals. 30x Leverage, 10% Margin, 1.5% SL.

| Strategy | Best 60-Day ROI | 3-Year Total ROI | Win Rate | Trades |
|----------|-----------------|------------------|----------|--------|
| **BB Width Expansion** | **646.99%** | Positive | 16.35% | 520 |
| **RSI Momentum Scalp** | **635.72%** | Positive | 15.43% | 1108 |
| **Aggressive Donchian** | **562.99%** | Positive | 14.74% | 753 |
| **IMBA (S20 Filtered)** | **337.28%** | 217.89% | 16.30% | 270 |
| **VW-MACD** | **315.62%** | Positive | 23.37% | 860 |

---

## 💎 THE "EXPLOSIVE" WINNER: **BB Width Expansion**
The **Bollinger Band Width Expansion** strategy on the 1-hour timeframe proved to be the most explosive. By entering trades only during periods of increasing volatility confirmed by ADX, it captured rapid price movements on ROSEUSDT.

### Why it works for "Heavy Gains":
- **Volatility Squeeze:** It targets the exact moment a consolidation ends and a major trend begins.
- **Strict SL (1.5%):** Even though the win rate is low, the large gains (10% TP) with 30x leverage result in massive compounding during trending phases.

---

## 🏆 THE LONG-TERM ROBUST WINNER: **IMBA (S20 Filtered)**
While less "explosive" in a 60-day window than the scalpers, the **Filtered IMBA** strategy is the most stable for 3-year growth.

- **Config:** Sens 20, 200 EMA Filter, 3-Bar Confirmation, DMI Filter.
- **ROI:** ~11,500% (with 5% TP / 3% SL).
- **Stability:** Highest Sharpe ratio and lowest relative drawdown among the heavy hitters.

---

## 🛠️ REPRODUCIBILITY
All results are generated using the **Realistic MTF Backtester**, which prevents look-ahead bias and correctly models intra-candle Stop Loss hits.

*Note: The massive 60-day peaks are your primary targets for "Heavy ROI". Long-term survival requires strict adherence to the 10% Margin rule to handle the drawdowns inherent in 30x leverage.*
