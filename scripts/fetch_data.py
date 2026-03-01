import requests
import os
import pandas as pd
from datetime import datetime, timedelta
import zipfile
import io

def download_daily_klines(symbol, timeframe, year, month, day):
    url = f"https://data.binance.vision/data/futures/um/daily/klines/{symbol}/{timeframe}/{symbol}-{timeframe}-{year}-{month:02d}-{day:02d}.zip"
    response = requests.get(url)
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            csv_name = z.namelist()[0]
            with z.open(csv_name) as f:
                # Check first line to skip header if it exists
                first_line = f.readline().decode('utf-8')
                f.seek(0)
                if first_line.startswith('open_time'):
                    df = pd.read_csv(f)
                else:
                    df = pd.read_csv(f, header=None)

                # Binance kline data format:
                # [0] Open time, [1] Open, [2] High, [3] Low, [4] Close, [5] Volume
                if df.columns[0] == 'open_time':
                    df = df[['open_time', 'open', 'high', 'low', 'close', 'volume']]
                else:
                    df = df[[0, 1, 2, 3, 4, 5]]

                df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df['timestamp'] = pd.to_numeric(df['timestamp'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                return df
    else:
        # print(f"Failed to download {url}: {response.status_code}")
        return None

def fetch_history(symbol, timeframe, days=60):
    all_dfs = []
    # Current date in simulation is Mar 1, 2026.
    # But binance vision data might be a few days behind or the date is different.
    # Let's use today's date and go back.
    end_date = datetime.now() - timedelta(days=2)
    start_date = end_date - timedelta(days=days)

    current_date = start_date
    print(f"Fetching from {start_date.date()} to {end_date.date()}...")
    while current_date <= end_date:
        df = download_daily_klines(symbol, timeframe, current_date.year, current_date.month, current_date.day)
        if df is not None:
            all_dfs.append(df)
            if len(all_dfs) % 10 == 0:
                print(f"Downloaded {len(all_dfs)} days...")
        current_date += timedelta(days=1)

    if all_dfs:
        final_df = pd.concat(all_dfs)
        final_df.set_index('timestamp', inplace=True)
        final_df.sort_index(inplace=True)
        return final_df
    return None

if __name__ == "__main__":
    symbol = 'ROSEUSDT'
    # 1h data for 120 days
    df_1h = fetch_history(symbol, '1h', days=120)
    if df_1h is not None:
        df_1h.to_csv('data/ROSEUSDT_1h.csv')
        print(f"Saved {len(df_1h)} rows of 1h data.")

    # 15m data for 30 days
    df_15m = fetch_history(symbol, '15m', days=30)
    if df_15m is not None:
        df_15m.to_csv('data/ROSEUSDT_15m.csv')
        print(f"Saved {len(df_15m)} rows of 15m data.")
