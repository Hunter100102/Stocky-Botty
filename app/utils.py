import os, math, time, csv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def get_tz():
    return os.getenv("TZ","America/New_York")

def now_tz():
    return datetime.now(ZoneInfo(get_tz()))

def is_market_hours(dt=None):
    dt = dt or now_tz()
    # Rough US market guard: Mon-Fri, 9:35–15:55 ET
    if dt.weekday() >= 5:  # 5=Sat,6=Sun
        return False
    open_t = dt.replace(hour=9, minute=35, second=0, microsecond=0)
    close_t = dt.replace(hour=15, minute=55, second=0, microsecond=0)
    return open_t <= dt <= close_t

def ensure_logs():
    os.makedirs("logs", exist_ok=True)
    f = "logs/trades.csv"
    if not os.path.exists(f):
        with open(f,"w",newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["ts","symbol","action","qty","price","reason","mode"])

def log_trade(symbol, action, qty, price, reason, mode):
    ensure_logs()
    with open("logs/trades.csv","a",newline="") as fh:
        w = csv.writer(fh)
        w.writerow([now_tz().isoformat(), symbol, action, f"{qty:.6f}", f"{price:.4f}", reason, mode])
