from abc import ABC, abstractmethod

class Broker(ABC):
    @abstractmethod
    def get_positions(self)->list[dict]:
        ...

    @abstractmethod
    def get_cash(self)->float:
        ...

    @abstractmethod
    def market_buy(self, symbol:str, qty:float)->dict:
        ...

    @abstractmethod
    def market_sell(self, symbol:str, qty:float)->dict:
        ...
