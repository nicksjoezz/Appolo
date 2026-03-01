# ALL TRADING STRATEGIES: RULES & LOGIC

This document provides the full technical rules for all strategies developed for ROSE/USDT 30x leverage.

---

## 1. IMBA Algo Trend (The Core)
- **Logic:** Ported from Pine Script. Calculates the 50% Fibonacci level of a high/low channel over a lookback period.
- **Rules:**
  - `Lookback = Sensitivity * 10`
  - `Trend Line = Highest(High, Lookback) - (Highest(High, Lookback) - Lowest(Low, Lookback)) * 0.5`
  - **Long:** Price crosses above Trend Line.
  - **Short:** Price crosses below Trend Line.

## 2. IMBA + UT Bot (Optimized Winner)
- **Logic:** Combines IMBA macro trend with UT Bot entry/exit signals.
- **Rules:**
  - **Trend Filter:** Close must be above IMBA Trend Line (Sens 20).
  - **Entry:** UT Bot Buy Signal (Key 5, ATR 10).
  - **Exit:**
    - TP 10% or SL 1%.
    - **Opposite Signal:** Close Long immediately if UT Bot Sell Signal appears.
- **Best Use:** Long-term trend following with early exit protection.

## 3. BB Width Expansion (Explosive Growth)
- **Logic:** Targets the volatility breakout following a Bollinger Band squeeze.
- **Rules:**
  - **Volatility Filter:** Bollinger Bandwidth (20, 2) must be increasing (Expansion).
  - **Trend Filter:** ADX > 25.
  - **Entry (Long):** Price breaks above Upper BB.
  - **Execution:** TP 10%, SL 1.5%.

## 4. RSI Momentum Scalper (High Frequency)
- **Logic:** Captures momentum shifts in a trending environment.
- **Rules:**
  - **Trend Filter:** Price above 50 EMA.
  - **Entry (Long):** RSI (7) crosses above 50.
  - **Execution:** TP 5%, SL 1.5%.

## 5. Aggressive Donchian Breakout
- **Logic:** Classic range-break strategy optimized for ROSE volatility.
- **Rules:**
  - **Entry (Long):** Price exceeds the 10-hour Highest High.
  - **Filter:** ADX > 25.
  - **Execution:** TP 5%, SL 1.5%.

## 6. VW-MACD (Volume Confirmed)
- **Logic:** MACD Histogram calculated using Volume-Weighted prices.
- **Rules:**
  - **Entry:** MACD Histogram (12, 26, 9) crosses above 0.
  - **Filter:** ADX > 25.
  - **Execution:** TP 10%, SL 1.5%.

## 7. Filtered IMBA (Balanced Stability)
- **Logic:** IMBA with conservative filters for maximum drawdown protection.
- **Rules:**
  - Sens 20, 200 EMA Filter, 3-Bar Confirmation, DMI Alignment.
  - **Execution:** TP 5%, SL 3%.
