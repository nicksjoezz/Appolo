# ALL TRADING STRATEGIES: RULES & LOGIC

This document provides the full technical rules for the top-performing strategies developed for ROSE/USDT 30x leverage.

---

## 1. IMBA + UT Bot (The Aggressive Winner)
- **Logic:** Combines the IMBA macro trend with UT Bot's precise entry/exit triggers.
- **Rules:**
  - **Trend Filter:** IMBA Algo Trend (Sensitivity 20). Only enter Long if Price > IMBA Line.
  - **Entry:** UT Bot Buy Signal (Key 5, ATR 10).
  - **Take Profit:** 20.0%
  - **Stop Loss:** 1.0%
  - **Forced Exit:** Close the position immediately if the opposite UT Bot signal (Sell) occurs, even if TP/SL hasn't been hit.
- **Performance:** 1,783% ROI (3 Years).

## 2. Filtered IMBA (The Robust Winner)
- **Logic:** Optimized for maximum stability and win rate over long periods.
- **Rules:**
  - **Trend Filter:** 200-period EMA.
  - **Momentum Filter:** DMI (DI+ > DI- for Longs).
  - **Confirmation:** Requires 3 consecutive 1H bars in the trend direction before entry.
  - **Take Profit:** 5.0%
  - **Stop Loss:** 3.0%
- **Performance:** 11,587% ROI (3 Years) | 50.21% Win Rate.

## 3. BB Width Expansion (Explosive Growth)
- **Logic:** Targets the volatility expansion following a Bollinger Band squeeze.
- **Rules:**
  - **Volatility:** Bollinger Bandwidth (20, 2) must be increasing.
  - **Trend:** ADX > 25.
  - **Entry:** Price breaks above/below the Upper/Lower Bollinger Band.
  - **Execution:** TP 10%, SL 1.5%.

## 4. RSI Momentum Scalper
- **Logic:** Captures rapid momentum shifts in a trending environment.
- **Rules:**
  - **Trend:** Price must be above/below 50 EMA.
  - **Trigger:** RSI (7) crosses above/below the 50 level.
  - **Execution:** TP 5%, SL 1.5%.

## 5. Aggressive Donchian Breakout
- **Logic:** Classic range-break strategy.
- **Rules:**
  - **Entry:** Price breaks the 10-hour High/Low range.
  - **Filter:** ADX > 25.
  - **Execution:** TP 5%, SL 1.5%.
