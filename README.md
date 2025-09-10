# Free Stock Robot (Paper/Signal-First) 🚀

This is a *free-first* stock bot you can deploy on **Render** (free web service + free cron**)** or **Heroku (hobby)**.  
It **does not** require paid data feeds: prices use `yfinance`; headlines use public RSS feeds + VADER sentiment.  
By default it runs in **DRY_RUN** mode (no orders placed). You can enable **Alpaca Paper** trading for free.

> ⚠️ **Not financial advice.** Educational template only. Markets are risky; test with paper first.

## What it does
- Pulls quotes with `yfinance` for your watchlist.
- Computes indicators (SMA20/SMA50, RSI14) and combines with quick headline sentiment per ticker.
- Decides BUY/HOLD/SELL signals with risk limits & position sizing.
- In DRY_RUN: logs signals to `logs/trades.csv`.  
- With Alpaca Paper: places market orders automatically.
- Exposes a tiny FastAPI dashboard at `/` and a job endpoint `/run` you can ping via Render Cron.

## Quick Start (Local)
1. **Python 3.10+** installed.
2. `pip install -r requirements.txt`
3. Copy `.env.example` → `.env`, fill the blanks (keep DRY_RUN=true to start).
4. Edit `app/config.yaml` → set your `watchlist` and `max_positions`.
5. Run the web server: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
6. Visit `http://localhost:8000` then trigger a run: `curl -X POST http://localhost:8000/run`

## Deploy to Render (Free)
1. Push this folder to a new GitHub repo.
2. In Render: **New → Web Service** → connect repo
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add **Environment** (Settings → Environment): paste your `.env` content.
4. Add **Cron Job** (Render → *Cron Jobs*): POST your-service `/run` every 15 min on weekdays.
   Example schedule: `*/15 13-20 * * 1-5` (13–20 UTC ≈ 9–4 ET).
5. Open the service URL → dashboard.

## Enable Alpaca Paper (optional & free)
- Set in `.env`:
  ```env
  DRY_RUN=false
  BROKER=alpaca
  ALPACA_KEY_ID=...
  ALPACA_SECRET_KEY=...
  ALPACA_BASE_URL=https://paper-api.alpaca.markets
  ```
- Create paper account: https://app.alpaca.markets/paper/dashboard

## Files you edit
- `.env` — secrets and behavior (dry-run vs broker).
- `app/config.yaml` — tickers, risk, sizing.
- `app/signals.py` — rule parameters if you want to tweak.
- `app/portfolio.py` — risk/position sizing knobs.

## Safety rails (default)
- Market-hours guard (US, weekdays, ~9:35–15:55 ET).
- Max positions / per-position risk caps.
- Cooldown after buys/sells; never goes all-in.
- DRY_RUN default.

## Notes
- RSS parsing is best-effort. For higher-quality signals, plug in APIs like Alpha Vantage or Finnhub (free tiers).
- You can also set `ALERT_EMAIL_TO` + `SENDGRID_API_KEY` to get email alerts instead of auto-trading.

---

## Legal
This is **educational software**, provided “as is”, **no warranty**. You are solely responsible for any use, configuration, and trading decisions. Past performance ≠ future results.
