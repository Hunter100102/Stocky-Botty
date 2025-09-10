import os
from .base import Broker
import alpaca_trade_api as tradeapi

class Alpaca(Broker):
    def __init__(self):
        key = os.getenv("ALPACA_KEY_ID","")
        secret = os.getenv("ALPACA_SECRET_KEY","")
        base = os.getenv("ALPACA_BASE_URL","https://paper-api.alpaca.markets")
        self.api = tradeapi.REST(key, secret, base_url=base, api_version='v2')

    def get_positions(self):
        out = []
        for p in self.api.list_positions():
            out.append({
                "symbol": p.symbol,
                "qty": float(p.qty),
                "avg_price": float(p.avg_entry_price),
            })
        return out

    def get_cash(self)->float:
        a = self.api.get_account()
        return float(a.cash)

    def market_buy(self, symbol:str, qty:float)->dict:
        if qty <= 0: return {"skipped":"nonpositive"}
        o = self.api.submit_order(symbol=symbol, qty=qty, side='buy', type='market', time_in_force='day')
        return {"order_id": o.id, "symbol":symbol, "qty":qty, "side":"buy"}

    def market_sell(self, symbol:str, qty:float)->dict:
        if qty <= 0: return {"skipped":"nonpositive"}
        o = self.api.submit_order(symbol=symbol, qty=qty, side='sell', type='market', time_in_force='day')
        return {"order_id": o.id, "symbol":symbol, "qty":qty, "side":"sell"}
