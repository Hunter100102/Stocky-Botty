import feedparser, re
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

_vader = None

def _ensure_vader():
    global _vader
    if _vader is None:
        try:
            _vader = SentimentIntensityAnalyzer()
        except:
            nltk.download('vader_lexicon')
            _vader = SentimentIntensityAnalyzer()
    return _vader

def fetch_headlines(rss_urls:list[str], limit:int=200)->list[dict]:
    items = []
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:limit]:
                items.append({
                    "title": e.title if hasattr(e, 'title') else "",
                    "summary": e.summary if hasattr(e, 'summary') else "",
                    "link": e.link if hasattr(e, 'link') else "",
                })
        except Exception as e:
            continue
    return items

def score_for_symbol(symbol:str, rss_urls:list[str]):
    vader = _ensure_vader()
    news = fetch_headlines(rss_urls, limit=50)
    sym = symbol.split("-")[0].upper()
    texts = []
    for n in news:
        t = (n["title"] or "") + " " + (n["summary"] or "")
        if re.search(rf"\b{re.escape(sym)}\b", t, flags=re.IGNORECASE):
            texts.append(t)
    if len(texts) < 1:
        return None, 0
    scores = [vader.polarity_scores(t)["compound"] for t in texts]
    return sum(scores)/len(scores), len(texts)
