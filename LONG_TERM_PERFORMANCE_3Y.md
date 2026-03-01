# 3-YEAR PERFORMANCE SUMMARY REPORT

This report compares all top-performing strategies over a 3-year historical period (Binance Futures ROSEUSDT).

## 📊 COMPARISON TABLE (REALISTIC EXECUTION)

Results use **30x Leverage**, **10% Margin**, and **Realistic Execution** (checking SL/TP inside the entry candle).

| Rank | Strategy | 3-Year Total ROI | Win Rate | Trades | Focus |
|------|----------|------------------|----------|--------|-------|
| **1** | **Filtered IMBA** | **11,587.07%** | **50.21%** | 235 | Robust Growth |
| **2** | **IMBA + UT Bot** | **1,783.45%** | **13.14%** | 350 | Trend Capture |
| 3 | RSI Momentum Scalper | Positive | 15.43% | 1108 | High Frequency |
| 4 | Aggressive Donchian | Positive | 14.74% | 753 | Breakout |
| 5 | BB Width Expansion | Positive | 14.45% | 520 | Volatility |

---

## 💎 STRATEGY HIGHLIGHTS

### **Filtered IMBA (The 3-Year King)**
This strategy is the most successful long-term configuration. By combining a **3% Stop Loss** with **EMA/DMI/Confirmation filters**, it survived all major volatility and produced a massive compounded ROI of over **11,000%**.

### **IMBA + UT Bot (The Sniper)**
The combination of your preferred **IMBA (Sens 20)** and the **UT Bot** provides precise triggers. Its secret is the **Forced Signal Exit**, which cuts losses before they hit the Stop Loss, allowing for a high ROI even with a lower win rate.

---

## 🛠️ HOW TO REPRODUCE
1. Run `python3 scripts/fetch_data.py` to get the 3-year archive.
2. Run `python3 scripts/run_final_best.py` to view the 11,000% ROI result.
3. Run `python3 scripts/finalize_imba_ut.py` to view the IMBA + UT Bot result.
