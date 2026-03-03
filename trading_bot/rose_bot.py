import ccxt
import pandas as pd
import pandas_ta as ta
import time
import logging
import os
from datetime import datetime

# --- SETTINGS ---
SYMBOL = 'ROSE/USDT'
TIMEFRAME = '1h'
LEVERAGE = 30
MARGIN_PCT = 0.10 # Use 10% of total balance as margin
TP_PCT = 0.05     # 5% Take Profit
SL_PCT = 0.03     # 3% Stop Loss

# IMBA Parameters
SENSITIVITY = 20
EMA_LEN = 200

# API Credentials
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class RoseBot:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'options': {'defaultType': 'future'},
            'enableRateLimit': True
        })
        self.market = None
        self.pos_side = None

    def load_market_info(self):
        try:
            markets = self.exchange.load_markets()
            self.market = markets[SYMBOL]
            logger.info(f"Market info loaded for {SYMBOL}")
        except Exception as e:
            logger.error(f"Error loading markets: {e}")

    def fetch_data(self, limit=500):
        try:
            ohlcv = self.exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None

    def calculate_signals(self, df):
        df = df.copy()
        length = int(max(1, SENSITIVITY * 10))
        df['high_line'] = df['high'].rolling(window=length).max()
        df['low_line'] = df['low'].rolling(window=length).min()
        df['imba_line'] = df['high_line'] - (df['high_line'] - df['low_line']) * 0.5

        df['is_uptrend'] = df['close'] > df['imba_line']
        df['is_downtrend'] = df['close'] < df['imba_line']

        df['ema'] = ta.ema(df['close'], length=EMA_LEN)
        adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
        df['dmp'] = adx_df['DMP_14']
        df['dmn'] = adx_df['DMN_14']

        df['uptrend_count'] = df['is_uptrend'].rolling(3).sum()
        df['downtrend_count'] = df['is_downtrend'].rolling(3).sum()

        can_long = (df['close'] > df['ema']) & (df['dmp'] > df['dmn'])
        can_short = (df['close'] < df['ema']) & (df['dmn'] > df['dmp'])

        long_signal = (df['uptrend_count'] == 3) & (df['uptrend_count'].shift(1) == 2) & can_long
        short_signal = (df['downtrend_count'] == 3) & (df['downtrend_count'].shift(1) == 2) & can_short

        exit_long = df['is_downtrend']
        exit_short = df['is_uptrend']

        return long_signal.iloc[-1], short_signal.iloc[-1], exit_long.iloc[-1], exit_short.iloc[-1]

    def set_leverage(self):
        try:
            self.exchange.set_leverage(LEVERAGE, SYMBOL)
            logger.info(f"Leverage set to {LEVERAGE}x")
        except Exception as e:
            logger.error(f"Error setting leverage: {e}")

    def amount_to_precision(self, amount):
        return float(self.exchange.amount_to_precision(SYMBOL, amount))

    def price_to_precision(self, price):
        return float(self.exchange.price_to_precision(SYMBOL, price))

    def execute_trade(self, side, amount):
        try:
            amount = self.amount_to_precision(amount)
            logger.info(f"Executing {side.upper()} order for {amount} {SYMBOL}")
            order = self.exchange.create_market_order(SYMBOL, side, amount)
            return order
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return None

    def run(self):
        logger.info("Starting RoseBot...")
        self.load_market_info()
        self.set_leverage()

        while True:
            try:
                df = self.fetch_data()
                if df is None: continue

                long_sig, short_sig, exit_long, exit_short = self.calculate_signals(df)

                balance = self.exchange.fetch_balance()
                usdt_balance = balance['total']['USDT']

                # Fetch positions using standard CCXT method
                positions = self.exchange.fetch_positions([SYMBOL])
                current_qty = 0
                if positions:
                    current_qty = float(positions[0]['info']['positionAmt'])

                if current_qty > 0: self.pos_side = 'long'
                elif current_qty < 0: self.pos_side = 'short'
                else: self.pos_side = None

                # 1. Exit Logic
                if self.pos_side == 'long' and exit_long:
                    self.execute_trade('sell', abs(current_qty))
                elif self.pos_side == 'short' and exit_short:
                    self.execute_trade('buy', abs(current_qty))

                # 2. Entry Logic
                if self.pos_side is None:
                    price = df['close'].iloc[-1]
                    pos_size_usdt = usdt_balance * MARGIN_PCT * LEVERAGE
                    amount = pos_size_usdt / price

                    if long_sig:
                        order = self.execute_trade('buy', amount)
                        if order:
                            self.exchange.create_order(SYMBOL, 'TAKE_PROFIT_MARKET', 'sell', self.amount_to_precision(amount),
                                                      params={'stopPrice': self.price_to_precision(price * (1 + TP_PCT))})
                            self.exchange.create_order(SYMBOL, 'STOP_MARKET', 'sell', self.amount_to_precision(amount),
                                                      params={'stopPrice': self.price_to_precision(price * (1 - SL_PCT))})
                    elif short_sig:
                        order = self.execute_trade('sell', amount)
                        if order:
                            self.exchange.create_order(SYMBOL, 'TAKE_PROFIT_MARKET', 'buy', self.amount_to_precision(amount),
                                                      params={'stopPrice': self.price_to_precision(price * (1 - TP_PCT))})
                            self.exchange.create_order(SYMBOL, 'STOP_MARKET', 'buy', self.amount_to_precision(amount),
                                                      params={'stopPrice': self.price_to_precision(price * (1 + SL_PCT))})

                time.sleep(300)
            except Exception as e:
                logger.error(f"Bot error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    if not API_KEY or not API_SECRET:
        print("CRITICAL: Set BINANCE_API_KEY and BINANCE_API_SECRET.")
    else:
        RoseBot().run()
