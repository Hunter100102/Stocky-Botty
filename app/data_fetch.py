import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def latest_price(symbol:str)->float:
    t = yf.Ticker(symbol)
    # yfinance sometimes returns None for fast data; fallback to close
    p = t.fast_info.get('lastPrice', None)
    if p is None:
        hist = t.history(period='2d', interval='1m')
        if len(hist):
            p = float(hist['Close'].iloc[-1])
    return float(p) if p is not None else None

def candles(symbol:str, lookback_days:int=120)->pd.DataFrame:
    end = datetime.utcnow()
    start = end - timedelta(days=lookback_days)
    df = yf.download(symbol, start=start, end=end, interval='1d', progress=False, auto_adjust=True)
    df = df.rename(columns=str.title)
    return df
