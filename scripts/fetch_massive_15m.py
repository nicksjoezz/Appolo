import requests
import os
import pandas as pd
from datetime import datetime, timedelta
import zipfile
import io

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

def fetch_history(symbol, timeframe, years=3):
    all_dfs = []
    end_date = datetime.now() - timedelta(days=2)
    start_date = end_date - timedelta(days=365*years)
    current_date = start_date
    print(f"Fetching {years} years of {timeframe} data for {symbol}...")
    while current_date <= end_date - timedelta(days=32):
        df = download_monthly_klines(symbol, timeframe, current_date.year, current_date.month)
        if df is not None:
            all_dfs.append(df)
            print(f"Downloaded {current_date.year}-{current_date.month:02d}")
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
        else:
            break
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        df = download_daily_klines(symbol, timeframe, date_str)
        if df is not None:
            all_dfs.append(df)
        current_date += timedelta(days=1)
    if all_dfs:
        final_df = pd.concat(all_dfs).drop_duplicates(subset='timestamp')
        final_df.set_index('timestamp', inplace=True)
        final_df.sort_index(inplace=True)
        return final_df
    return None

if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    symbol = 'ROSEUSDT'
    df_15m = fetch_history(symbol, '15m', years=3)
    if df_15m is not None:
        df_15m.to_csv('data/ROSEUSDT_15m_3y.csv')
        print(f"Saved {len(df_15m)} rows of 15m data.")
