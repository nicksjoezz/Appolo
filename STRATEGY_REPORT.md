# ROSEUSDT Strategy Comparison Report

## Summary of Best Configurations (Sensitivity 18, 10% Margin, 30x Leverage, 1% SL)

| Strategy Variant | Filter(s) | ROI % | Win Rate % | Max Drawdown % | Sharpe |
|------------------|-----------|-------|------------|----------------|--------|
| **Best Balanced** | EMA 300 + TC | 52.86% | 28.57% | -15.57% | 2.02 |
| **Best Win Rate** | EMA 300 + TC (TP 3%) | 36.81% | 37.93% | -15.57% | 1.95 |
| **Highest ROI** | EMA 300 + TC | 52.86% | 28.57% | -15.57% | 2.02 |

## Detailed Performance Documentation

### 1. IMBA Algo Trend (Sensitivity 18) - Baseline
- **Description:** Original strategy without additional filtering.
- **ROI:** -83.09%
- **Win Rate:** 18.17%
- **MDD:** -91.01%
- **Analysis:** High trade frequency and high noise lead to rapid equity erosion under realistic 1% Stop Loss constraints.

### 2. IMBA + EMA 300 Filter
- **Description:** Only enters trades that align with the 300-period EMA trend.
- **ROI:** -85.83%
- **Win Rate:** 17.66%
- **MDD:** -87.64%
- **Analysis:** EMA alone improves drawdown slightly but doesn't solve the win rate issue on its own.

### 3. IMBA + Trend Confirmation (TC)
- **Description:** Requires 3 consecutive bars in the trend direction before entry.
- **ROI:** 29.64%
- **Win Rate:** 23.68%
- **MDD:** -18.35%
- **Analysis:** TC significantly reduces noise and prevents entries into false flips, vastly improving Drawdown.

### 4. IMBA + EMA 300 + Trend Confirmation (TC)
- **Description:** Combined Trend and Noise filtering.
- **ROI:** 52.86%
- **Win Rate:** 28.57%
- **MDD:** -15.57%
- **Analysis:** **Best Overall.** The combination of trend alignment and noise reduction produces a stable equity curve and positive ROI while respecting the strict 1% SL requirement for 30x leverage.

## Conclusion
For ROSEUSDT at 30x leverage, **IMBA Sensitivity 18** works best when combined with an **EMA 300 trend filter** and **3-bar Trend Confirmation**. This setup filters out the volatile chop that typically liquidates 30x positions.
