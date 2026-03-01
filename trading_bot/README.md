# ROSEUSDT Filtered IMBA Trading Bot

This bot executes the **Filtered IMBA (The King)** strategy on Binance Futures with 30x leverage.

## 🚀 Strategy Overview
- **Core Indicator:** IMBA Algo Trend (Sensitivity 20).
- **Filters:** 200 EMA + DMI Alignment + 3-Bar Confirmation.
- **Risk Management:** 10% Margin per trade, 5% TP, 3% SL.
- **Auto-Exit:** Closes position on trend reversal signals.

## 🛠️ Setup
1. **Install Dependencies:**
   ```bash
   pip install ccxt pandas pandas-ta
   ```

2. **Environment Variables:**
   Set your Binance API credentials:
   ```bash
   export BINANCE_API_KEY='your_key'
   export BINANCE_API_SECRET='your_secret'
   ```

3. **Run the Bot:**
   ```bash
   python3 trading_bot/rose_bot.py
   ```

## ⚠️ Important Safety Warnings
- **High Leverage:** 30x leverage is extremely risky. Ensure you understand the liquidation risks.
- **Margin Rule:** This bot is hardcoded to use 10% of your USDT balance. Do not exceed this to avoid account-wide liquidation.
- **Monitor:** Always monitor the bot's logs and your Binance dashboard during the first few trades.

## 📁 File Structure
- `rose_bot.py`: The main execution script.
- `README.md`: This instruction file.
