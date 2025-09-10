import os, json
from .base import Broker

class Dry(Broker):
    def __init__(self):
        self.cash = float(os.getenv("INITIAL_CASH", "1000"))
        self._positions = {}  # symbol -> (qty, avg_price)

    def get_positions(self):
        return [{"symbol":s,"qty":q,"avg_price":ap} for s,(q,ap) in self._positions.items()]

    def get_cash(self)->float:
        return self.cash

    def market_buy(self, symbol:str, qty:float)->dict:
        if qty <= 0: 
            return {"skipped":"nonpositive"}
        # Assume price filled at market is passed in externally — handled in main trade loop
        return {"ok":"buy_pending"}

    def market_sell(self, symbol:str, qty:float)->dict:
        if qty <= 0: 
            return {"skipped":"nonpositive"}
        return {"ok":"sell_pending"}
