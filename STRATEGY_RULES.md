# STRATEGY RULES & PARAMETERS

This document defines the rules for all 5 new aggressive strategies plus the optimized IMBA configuration.

## 1. Aggressive Donchian (Top Performer)
- **Concept:** Captures immediate momentum after price breaks the recent high/low range.
- **Entry (Long):** Price exceeds the highest high of the last 10 hours.
- **Entry (Short):** Price falls below the lowest low of the last 10 hours.
- **Winner Filter:** ADX > 25 (Trend confirmation).
- **Execution:** 30x Leverage, 10% Margin, 5% TP, 1.5% SL.

## 2. BB Width Expansion (Explosive Growth)
- **Concept:** Trades volatility "squeezes" that lead to explosive expansion.
- **Entry (Long):** Price breaks above the Upper Bollinger Band (20, 2) WHILE Bandwidth is increasing.
- **Entry (Short):** Price breaks below the Lower Bollinger Band WHILE Bandwidth is increasing.
- **Winner Filter:** ADX > 25.
- **Execution:** 30x Leverage, 10% Margin, 5% TP, 1.5% SL.

## 3. RSI Momentum Scalper
- **Concept:** Uses RSI crossings as a proxy for a surge in buying/selling pressure.
- **Entry (Long):** Price is above the 50 EMA and RSI (7) crosses above 50.
- **Entry (Short):** Price is below the 50 EMA and RSI (7) crosses below 50.
- **Execution:** 30x Leverage, 10% Margin, 5% TP, 1.5% SL.

## 4. VW-MACD (Volume Confirmed)
- **Concept:** Traditional MACD logic but weighted by Volume to ensure trades happen on high conviction.
- **Logic:** MACD calculation uses `Price * Volume` to find the volume-weighted histogram.
- **Entry:** Signal line crossing or histogram flip.
- **Winner Filter:** ADX > 25.
- **Execution:** 30x Leverage, 10% Margin, 10% TP, 1.5% SL.

## 5. IMBA Algo Trend (Sensitivity 20)
- **Concept:** Fibonacci 50% channel level trend tracking.
- **Entry:** Price flips above/below the 50% level of the lookback period.
- **Winner Filters:** 200 EMA + DMI DI Alignment + 3-Bar Confirmation.
- **Execution:** 30x Leverage, 10% Margin, 5% TP, 3.0% SL.
