# ROSEUSDT Strategy Report - No Trend Confirmation

## Executive Summary (No-TC)

This report documents the performance of the **IMBA Algo Trend** strategy WITHOUT the 3-bar Trend Confirmation filter. As requested, we focused on alternative filtering methods to maintain a **1% Stop Loss** on **30x leverage**.

### Best "No-TC" Configuration
| Parameter | Value |
|-----------|-------|
| **Sensitivity Factor** | 15 |
| **EMA Trend Filter** | 500 Period |
| **RSI Momentum Filter** | Enabled (Length 14) |
| **Take Profit** | 10.0% |
| **Stop Loss** | 1.0% |

### Performance Metrics (Realistic Backtest)
- **Total ROI (120 Days):** **62.36%**
- **Win Rate:** 12.21%
- **Sharpe Ratio:** 1.70
- **Max Drawdown:** -71.57%
- **Number of Trades:** 213

---

## Alternative Configurations

### 1. Sensitivity 18 (User Preferred)
- **Filters:** EMA 500 + RSI
- **ROI:** 10.93%
- **Win Rate:** 19.81%
- **MDD:** -78.05%
- **Analysis:** Less profitable than Sens 15 but offers a higher Win Rate.

### 2. Sensitivity 20
- **Filters:** EMA 500 + RSI
- **ROI:** 35.01%
- **Win Rate:** 11.86%
- **MDD:** -79.84%
- **Analysis:** Moderate performance, survives the chop better than Sens 18 without confirmation.

---

## Technical Comparison: Why Trend Confirmation Matters
Without the 3-bar Trend Confirmation, the strategy is exposed to significantly more "false flips" during sideways consolidation.
- **With TC:** We achieved ~52% ROI with only **-18% Drawdown**.
- **Without TC:** We achieved ~62% ROI but suffered **-71% Drawdown**.

**Recommendation:** While ROI can be regained using EMA 500 and RSI filters, the **Trend Confirmation** filter is superior for risk-adjusted returns (Sharpe) and protecting capital from large drawdowns at 30x leverage.
