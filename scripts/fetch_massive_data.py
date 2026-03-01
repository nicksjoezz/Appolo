import requests
import os
import pandas as pd
from datetime import datetime, timedelta
import zipfile
import io
import sys

def download_daily_klines(symbol, timeframe, date_str):
    url = f"https://data.binance.vision/data/futures/um/daily/klines/{symbol}/{timeframe}/{symbol}-{timeframe}-{date_str}.zip"
    response = requests.get(url)
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            csv_name = z.namelist()[0]
            with z.open(csv_name) as f:
                first_line = f.readline().decode('utf-8')
                f.seek(0)
                df = pd.read_csv(f, header=None if not first_line.startswith('open_time') else 0)
                if first_line.startswith('open_time'):
                    df = df[['open_time', 'open', 'high', 'low', 'close', 'volume']]
                else:
                    df = df[[0, 1, 2, 3, 4, 5]]
                df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df['timestamp'] = pd.to_numeric(df['timestamp'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                return df
    return None

def download_monthly_klines(symbol, timeframe, year, month):
    url = f"https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/{timeframe}/{symbol}-{timeframe}-{year}-{month:02d}.zip"
    response = requests.get(url)
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            csv_name = z.namelist()[0]
            with z.open(csv_name) as f:
                first_line = f.readline().decode('utf-8')
                f.seek(0)
                df = pd.read_csv(f, header=None if not first_line.startswith('open_time') else 0)
                if first_line.startswith('open_time'):
                    df = df[['open_time', 'open', 'high', 'low', 'close', 'volume']]
                else:
                    df = df[[0, 1, 2, 3, 4, 5]]
                df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df['timestamp'] = pd.to_numeric(df['timestamp'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                return df
    return None

def fetch_years(symbol, timeframe, years=3):
    all_dfs = []
    end_date = datetime.now() - timedelta(days=2)
    start_date = end_date - timedelta(days=365*years)

    current_date = start_date
    print(f"Fetching {years} years of {timeframe} data for {symbol}...")

    # Try monthly first for speed
    while current_date <= end_date - timedelta(days=32):
        df = download_monthly_klines(symbol, timeframe, current_date.year, current_date.month)
        if df is not None:
            all_dfs.append(df)
            print(f"Downloaded {current_date.year}-{current_date.month:02d} (Monthly)")
            # Move to next month
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
        else:
            # If monthly fails, try daily for this month
            print(f"Monthly {current_date.year}-{current_date.month:02d} failed, trying daily...")
            break

    # Then catch up with daily
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        df = download_daily_klines(symbol, timeframe, date_str)
        if df is not None:
            all_dfs.append(df)
            if len(all_dfs) % 30 == 0:
                print(f"Downloaded {date_str} (Daily)...")
        current_date += timedelta(days=1)

    if all_dfs:
        final_df = pd.concat(all_dfs).drop_duplicates(subset='timestamp')
        final_df.set_index('timestamp', inplace=True)
        final_df.sort_index(inplace=True)
        return final_df
    return None

if __name__ == "__main__":
    symbol = 'ROSEUSDT'
    # 1h data for 3 years
    df_1h = fetch_years(symbol, '1h', years=3)
    if df_1h is not None:
        df_1h.to_csv('data/ROSEUSDT_1h_3y.csv')
        print(f"Saved {len(df_1h)} rows of 1h data.")

    # 5m data for 1 year (to avoid memory issues and disk limits)
    df_5m = fetch_years(symbol, '5m', years=1)
    if df_5m is not None:
        df_5m.to_csv('data/ROSEUSDT_5m_1y.csv')
        print(f"Saved {len(df_5m)} rows of 5m data.")
