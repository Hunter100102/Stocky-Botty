import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator

def compute_indicators(df: pd.DataFrame, sma_fast=20, sma_slow=50, rsi_len=14):
    if df.empty: 
        return df.assign(SMA_FAST=np.nan, SMA_SLOW=np.nan, RSI=np.nan)
    close = df['Close']
    df = df.copy()
    df['SMA_FAST'] = close.rolling(sma_fast).mean()
    df['SMA_SLOW'] = close.rolling(sma_slow).mean()
    df['RSI'] = RSIIndicator(close=close, window=rsi_len).rsi()
    return df

def decide_action(symbol, last_row, cfg, sent_score: float|None):
    r"""
    Rules (simple, editable):
    - BUY if SMA_FAST > SMA_SLOW, price > SMA_SLOW, RSI within buy band, and sentiment >= buy_threshold
    - SELL if price < SMA_SLOW or RSI > sell_max or sentiment <= sell_threshold
    - else HOLD
    """
    price = float(last_row['Close'])
    sma_f = float(last_row['SMA_FAST']) if not pd.isna(last_row['SMA_FAST']) else None
    sma_s = float(last_row['SMA_SLOW']) if not pd.isna(last_row['SMA_SLOW']) else None
    rsi   = float(last_row['RSI']) if not pd.isna(last_row['RSI']) else None

    ind = cfg['indicators']
    sent = cfg.get('sentiment',{})
    reason = []

    # Sentiment gates
    buy_ok = True
    sell_ok = False
    if sent.get('use_vader', True) and sent_score is not None:
        if sent_score < sent.get('buy_threshold', 0.05):
            buy_ok = False
        if sent_score <= sent.get('sell_threshold', -0.05):
            sell_ok = True
        reason.append(f"sent={sent_score:.2f}")

    # BUY conditions
    if sma_f and sma_s and rsi is not None:
        if sma_f > sma_s and price > sma_s and (ind.get('rsi_buy_min', 40) <= rsi <= 70) and buy_ok:
            reason.append("trend_up & rsi_ok")
            return "BUY", "; ".join(reason)

    # SELL conditions
    if sma_s and price < sma_s:
        reason.append("lost_sma_slow")
        return "SELL", "; ".join(reason)
    if rsi is not None and rsi > ind.get('rsi_sell_max', 75):
        reason.append("rsi_hot")
        return "SELL", "; ".join(reason)
    if sell_ok:
        reason.append("neg_sent")
        return "SELL", "; ".join(reason)

    return "HOLD", "; ".join(reason) or "no_signal"
