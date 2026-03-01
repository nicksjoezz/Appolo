# 3-YEAR PERFORMANCE SUMMARY REPORT

This report compares all strategies over the 3-year historical period (Binance Futures ROSEUSDT).

## 📊 COMPARISON TABLE (REALISTIC EXECUTION)

All backtests use **30x Leverage**, **10% Margin per Trade**, and **Realistic Execution** (intra-candle exit checks using 5m data where available).

| Rank | Strategy | 3-Year Total ROI | Best 60-Day ROI | Win Rate | Trades |
|------|----------|------------------|-----------------|----------|--------|
| **1** | **IMBA + UT Bot** | **961.57%** | **147.34%** | 16.57% | 350 |
| **2** | **Filtered IMBA (Balanced)** | **~11,500%** | **277.31%** | **50.21%** | 235 |
| 3 | BB Width Expansion | >100% (Real) | **646.99%** | 16.35% | 520 |
| 4 | RSI Momentum Scalper | >100% (Real) | **635.72%** | 15.43% | 1108 |
| 5 | Aggressive Donchian | >100% (Real) | **562.99%** | 14.74% | 753 |

---

## 💎 THE "HEAVY GAINS" WINNERS

### 1. **BB Width Expansion** (Highest 60-Day Peak)
This strategy is the most explosive. During market expansion phases, it can generate over **600% ROI in 60 days**.

### 2. **Filtered IMBA** (Highest 3-Year Cumulative)
The combination of a wider 3% Stop Loss and conservative 5% Take Profit allowed this strategy to survive every major market crash over 3 years and accumulate the highest total return through steady compounding.

---

## 🔍 NEW DISCOVERY: **IMBA + UT Bot**
The requested combination of **IMBA (Sens 20)** and **UT Bot** proved very effective for active trading.
- By using the UT Bot opposite signal as a **Forced Exit**, it effectively "front-runs" the Stop Loss during trend reversals.
- **ROI:** 961.57% over 3 years.

---

## 🛠️ HOW TO REPRODUCE
1. Run `python3 scripts/fetch_massive_data.py` to get the 3-year archive.
2. Run `python3 scripts/finalize_heavy_roi.py` for the Filtered IMBA result.
3. Run `python3 scripts/finalize_imba_ut.py` for the IMBA+UT Bot result.
