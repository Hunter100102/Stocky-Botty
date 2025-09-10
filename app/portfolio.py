from dataclasses import dataclass
from typing import Dict, List, Tuple
import math

@dataclass
class Position:
    symbol: str
    qty: float
    avg_price: float

def target_allocation(cash: float, prices: dict[str,float], max_positions:int, max_per_position_pct: float):
    # Equal-weight among selected up to caps
    picks = list(prices.keys())[:max_positions]
    alloc = {}
    if not picks:
        return alloc
    budget = cash
    per_cap = cash * max_per_position_pct
    per = min(budget/len(picks), per_cap)
    for s in picks:
        alloc[s] = per
    return alloc

def shares_for_dollars(dollars: float, price: float) -> float:
    if price <= 0: 
        return 0.0
    return max(0.0, dollars / price)
