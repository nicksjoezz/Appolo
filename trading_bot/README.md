# ROSEUSDT Filtered IMBA Trading Bot (v2)

This bot executes the **Filtered IMBA (The King)** strategy on Binance Futures with 30x leverage. It uses the `python-binance` library for high-performance WebSocket data and REST API orders.

## 🚀 Strategy Overview
- **Core Indicator:** IMBA Algo Trend (Sensitivity 20).
- **Filters:** 200 EMA + DMI Alignment + 3-Bar Confirmation.
- **Risk Management:** 10% Margin per trade, 5% TP, 3% SL.
- **Auto-Exit:** Closes position on trend reversal signals.

## 🛠️ Features (v2)
- **WebSockets:** Real-time data processing for accurate candle-close entries.
- **Precision Management:** Automatically handles Binance's Tick Size and Lot Size requirements.
- **Realistic Entries:** Logic is only evaluated once a candle actually closes.

## 📦 Setup
1. **Install Dependencies:**
   ```bash
   pip install python-binance pandas pandas-ta numpy
   ```

2. **Environment Variables:**
   Set your Binance API credentials:
   ```bash
   export BINANCE_API_KEY='your_key'
   export BINANCE_API_SECRET='your_secret'
   ```

3. **Run the Bot:**
   ```bash
   python3 trading_bot/rose_bot_v2.py
   ```

## ⚠️ Important Safety Warnings
- **High Leverage:** 30x leverage is extremely risky. Ensure you understand the liquidation risks.
- **Margin Rule:** This bot is hardcoded to use 10% of your USDT balance. Do not exceed this to avoid account-wide liquidation.
- **Market Orders:** This bot uses Market orders for entry and TP/SL for exit. Be aware of potential slippage.

## 📁 File Structure
- `rose_bot_v2.py`: The main execution script (WebSockets + python-binance).
- `README.md`: This instruction file.
