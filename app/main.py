import os, yaml, math
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, PlainTextResponse
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime, timedelta
from app import data_fetch, signals as sig, sentiment as sent, portfolio as port, utils
from app.broker.alpaca import Alpaca
from app.broker.dry import Dry

load_dotenv()

app = FastAPI()
env = Environment(loader=FileSystemLoader('templates'), autoescape=select_autoescape())

with open('app/config.yaml','r') as fh:
    CFG = yaml.safe_load(fh)

MODE = os.getenv("BROKER","dry").lower()
DRY_RUN = os.getenv("DRY_RUN","true").lower() == "true"

def get_broker():
    if DRY_RUN or MODE == "dry":
        return Dry(), "dry"
    if MODE == "alpaca":
        return Alpaca(), "alpaca"
    return Dry(), "dry"

@app.get("/", response_class=HTMLResponse)
def home():
    broker, mode = get_broker()
    watch = CFG['watchlist']
    # Build positions table with live quotes
    positions = []
    for p in broker.get_positions():
        mp = data_fetch.latest_price(p['symbol']) or p['avg_price']
        val = p['qty'] * mp
        pl = (mp - p['avg_price']) * p['qty']
        positions.append({"symbol":p['symbol'], "qty":p['qty'], "avg_price":p['avg_price'], "market_price":mp, "value":val, "pl":pl})
    # Recent signals from log (if present)
    utils.ensure_logs()
    sigs = []
    try:
        import csv
        with open("logs/trades.csv") as fh:
            r = list(csv.DictReader(fh))
            for row in r[-50:]:
                sigs.append({"ts": row["ts"], "symbol": row["symbol"], "action": row["action"], "reason": row["reason"]})
    except:
        pass
    tpl = env.get_template("index.html")
    return tpl.render(status="OK", mode="DRY_RUN" if DRY_RUN else mode.upper(), watchlist=", ".join(watch), positions=positions, signals=list(reversed(sigs)))

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/run", response_class=PlainTextResponse)
def run_job():
    # Guard market hours
    if not utils.is_market_hours():
        return "Skipped: outside market hours."
    broker, mode = get_broker()
    watch = CFG['watchlist']
    ind_cfg = CFG['indicators']
    news_cfg = CFG.get('news_rss', [])
    risk_cfg = CFG['risk']
    max_positions = CFG['max_positions']
    min_trade_usd = CFG.get('min_trade_usd', 20.0)

    # Gather data & signals
    buy_candidates = []
    sell_candidates = []
    last_prices = {}

    for sym in watch:
        df = data_fetch.candles(sym, 200)
        if df.empty or len(df) < max(ind_cfg['sma_fast'], ind_cfg['sma_slow']) + 2:
            continue
        df = sig.compute_indicators(df, ind_cfg['sma_fast'], ind_cfg['sma_slow'], ind_cfg['rsi_len'])
        last = df.iloc[-1]
        price = float(last['Close'])
        last_prices[sym] = price
        sscore, n = sent.score_for_symbol(sym, news_cfg)
        action, reason = sig.decide_action(sym, last, CFG, sscore)
        if action == "BUY":
            buy_candidates.append((sym, price, sscore if sscore is not None else 0.0, reason))
        elif action == "SELL":
            sell_candidates.append((sym, price, sscore if sscore is not None else 0.0, reason))

    # Existing positions
    positions = {p['symbol']: p for p in broker.get_positions()}
    cash = float(broker.get_cash())

    # SELL first (risk-off)
    sold = 0
    for sym, price, sscore, reason in sell_candidates:
        if sym in positions:
            qty = positions[sym]['qty']
            if qty > 0:
                if DRY_RUN:
                    # simulate credit
                    cash += qty * price
                    utils.log_trade(sym, "SELL", qty, price, reason, "DRY")
                    del positions[sym]
                else:
                    broker.market_sell(sym, qty)
                    utils.log_trade(sym, "SELL", qty, price, reason, "LIVE")
                sold += 1

    # BUY next (respect caps, cash buffer)
    # Decide which to buy (rank by sentiment then momentum-ish price/ SMA ratio)
    buy_candidates.sort(key=lambda x: (x[2], x[1]), reverse=True)
    to_buy = [b for b in buy_candidates if b[0] not in positions]
    # respect max_positions
    slots = max(0, max_positions - len(positions))
    picks = to_buy[:slots]

    # Keep cash buffer
    target_cash = cash * CFG.get('target_cash_pct', 0.15)
    budget = max(0.0, cash - target_cash)

    if picks and budget >= min_trade_usd:
        per_limit = budget * risk_cfg.get('max_per_position_pct', 0.2)
        per = min(budget/len(picks), per_limit)
        for sym, price, sscore, reason in picks:
            dollars = max(0.0, per)
            if dollars < min_trade_usd: 
                continue
            qty = dollars / price
            if DRY_RUN:
                cash -= qty * price
                positions[sym] = {"symbol":sym, "qty":qty, "avg_price":price}
                utils.log_trade(sym, "BUY", qty, price, reason, "DRY")
            else:
                broker.market_buy(sym, qty)
                utils.log_trade(sym, "BUY", qty, price, reason, "LIVE")

    return "Run complete."
