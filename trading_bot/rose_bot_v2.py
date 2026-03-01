import asyncio
import os
import pandas as pd
import pandas_ta as ta
import numpy as np
import logging
from binance.client import Client
from binance import BinanceSocketManager
from binance.enums import *

# --- SETTINGS ---
SYMBOL = 'ROSEUSDT'
TIMEFRAME = Client.KLINE_INTERVAL_1HOUR
LEVERAGE = 30
MARGIN_PCT = 0.10
TP_PCT = 0.05
SL_PCT = 0.03

# IMBA Parameters
SENSITIVITY = 20
EMA_LEN = 200

# API Credentials
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class RoseBotV2:
    def __init__(self):
        self.client = Client(API_KEY, API_SECRET)
        self.bsm = BinanceSocketManager(self.client)
        self.klines = []
        self.pos_side = None # 'LONG', 'SHORT', or None
        self.tick_size = None
        self.step_size = None

    def get_precision(self):
        try:
            info = self.client.futures_exchange_info()
            symbol_info = next(i for i in info['symbols'] if i['symbol'] == SYMBOL)

            price_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'PRICE_FILTER')
            self.tick_size = float(price_filter['tickSize'])

            lot_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE')
            self.step_size = float(lot_filter['stepSize'])

            logger.info(f"Precision Loaded: Tick={self.tick_size}, Step={self.step_size}")
        except Exception as e:
            logger.error(f"Error loading precision: {e}")

    def round_step(self, value, step):
        return round(value - (value % step), 8)

    def fetch_initial_data(self):
        logger.info("Fetching initial historical data...")
        bars = self.client.futures_klines(symbol=SYMBOL, interval=TIMEFRAME, limit=500)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base', 'taker_quote', 'ignore'])
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        df = df.astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    def calculate_signals(self, df):
        # 1. IMBA Logic
        length = int(max(1, SENSITIVITY * 10))
        df['high_line'] = df['high'].rolling(window=length).max()
        df['low_line'] = df['low'].rolling(window=length).min()
        df['imba_line'] = df['high_line'] - (df['high_line'] - df['low_line']) * 0.5

        is_uptrend = df['close'] > df['imba_line']
        is_downtrend = df['close'] < df['imba_line']

        # 2. Filters
        df['ema'] = ta.ema(df['close'], length=EMA_LEN)
        adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
        df['dmp'] = adx_df['DMP_14']
        df['dmn'] = adx_df['DMN_14']

        # 3. Confirmation (3 bars)
        df['uptrend_count'] = is_uptrend.rolling(3).sum()
        df['downtrend_count'] = is_downtrend.rolling(3).sum()

        can_long = (df['close'] > df['ema']) & (df['dmp'] > df['dmn'])
        can_short = (df['close'] < df['ema']) & (df['dmn'] > df['dmp'])

        long_signal = (df['uptrend_count'] == 3) & (df['uptrend_count'].shift(1) == 2) & can_long
        short_signal = (df['downtrend_count'] == 3) & (df['downtrend_count'].shift(1) == 2) & can_short

        exit_long = is_downtrend
        exit_short = is_uptrend

        return long_signal.iloc[-1], short_signal.iloc[-1], exit_long.iloc[-1], exit_short.iloc[-1]

    async def run(self):
        logger.info("Initializing RoseBot V2...")
        self.get_precision()
        self.client.futures_change_leverage(symbol=SYMBOL, leverage=LEVERAGE)

        # Initial State
        df = self.fetch_initial_data()

        socket = self.bsm.kline_socket(symbol=SYMBOL, interval=TIMEFRAME)
        async with socket as stream:
            while True:
                res = await stream.recv()
                k = res['k']

                # We only act on CANDLE CLOSE
                if k['x']:
                    logger.info(f"Candle Closed at {k['c']}. Evaluating strategy...")

                    # Update local DF
                    new_row = pd.DataFrame([{
                        'timestamp': pd.to_datetime(k['t'], unit='ms'),
                        'open': float(k['o']),
                        'high': float(k['h']),
                        'low': float(k['l']),
                        'close': float(k['c']),
                        'volume': float(k['v'])
                    }])
                    df = pd.concat([df, new_row]).tail(500)

                    long_sig, short_sig, exit_long, exit_short = self.calculate_signals(df)

                    # Check current position
                    pos = self.client.futures_position_information(symbol=SYMBOL)
                    sym_pos = next(p for p in pos if p['symbol'] == SYMBOL)
                    current_qty = float(sym_pos['positionAmt'])

                    if current_qty > 0: self.pos_side = 'LONG'
                    elif current_qty < 0: self.pos_side = 'SHORT'
                    else: self.pos_side = None

                    # 1. Exit Logic
                    if self.pos_side == 'LONG' and exit_long:
                        logger.info("Trend reversal. Closing LONG.")
                        self.client.futures_create_order(symbol=SYMBOL, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=abs(current_qty))
                    elif self.pos_side == 'SHORT' and exit_short:
                        logger.info("Trend reversal. Closing SHORT.")
                        self.client.futures_create_order(symbol=SYMBOL, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=abs(current_qty))

                    # 2. Entry Logic
                    if self.pos_side is None:
                        balances = self.client.futures_account_balance()
                        usdt_balance = float(next(b for b in balances if b['asset'] == 'USDT')['balance'])

                        price = float(k['c'])
                        amount_usdt = usdt_balance * MARGIN_PCT * LEVERAGE
                        qty = self.round_step(amount_usdt / price, self.step_size)

                        if long_sig:
                            logger.info(f"Opening LONG. Qty: {qty}")
                            self.client.futures_create_order(symbol=SYMBOL, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=qty)
                            # TP/SL
                            self.client.futures_create_order(symbol=SYMBOL, side=SIDE_SELL, type=FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET,
                                                            stopPrice=self.round_step(price * (1+TP_PCT), self.tick_size), closePosition=True)
                            self.client.futures_create_order(symbol=SYMBOL, side=SIDE_SELL, type=FUTURE_ORDER_TYPE_STOP_MARKET,
                                                            stopPrice=self.round_step(price * (1-SL_PCT), self.tick_size), closePosition=True)
                        elif short_sig:
                            logger.info(f"Opening SHORT. Qty: {qty}")
                            self.client.futures_create_order(symbol=SYMBOL, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=qty)
                            # TP/SL
                            self.client.futures_create_order(symbol=SYMBOL, side=SIDE_BUY, type=FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET,
                                                            stopPrice=self.round_step(price * (1-TP_PCT), self.tick_size), closePosition=True)
                            self.client.futures_create_order(symbol=SYMBOL, side=SIDE_BUY, type=FUTURE_ORDER_TYPE_STOP_MARKET,
                                                            stopPrice=self.round_step(price * (1+SL_PCT), self.tick_size), closePosition=True)

if __name__ == "__main__":
    if not API_KEY or not API_SECRET:
        print("Set BINANCE_API_KEY/SECRET.")
    else:
        bot = RoseBotV2()
        asyncio.run(bot.run())
