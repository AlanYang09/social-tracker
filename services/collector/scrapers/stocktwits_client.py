import requests
import logging
from datetime import datetime
from typing import List
from shared.models import PostIn
from shared.constants import SOURCE_STOCKTWITS
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)
BASE_URL = "https://api.stocktwits.com/api/2"


class StockTwitsScraper(BaseScraper):
    """Fetches posts from StockTwits public API (no auth required for basic endpoints)."""

    def scrape(self, keywords: List[str]) -> List[PostIn]:
        posts = []
        tickers = [k.lstrip("$").upper() for k in keywords if k.startswith("$")]
        for ticker in tickers:
            try:
                posts.extend(self._fetch_ticker_stream(ticker))
            except Exception as e:
                logger.warning(f"StockTwits error for {ticker}: {e}")
        return posts

    def _fetch_ticker_stream(self, ticker: str) -> List[PostIn]:
        url = f"{BASE_URL}/streams/symbol/{ticker}.json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        messages = data.get("messages", [])
        posts = []
        for msg in messages:
            try:
                sentiment = msg.get("entities", {}).get("sentiment", {})
                posts.append(PostIn(
                    external_id=f"st_{msg['id']}",
                    source=SOURCE_STOCKTWITS,
                    author=msg.get("user", {}).get("username"),
                    content=msg.get("body", ""),
                    url=f"https://stocktwits.com/message/{msg['id']}",
                    posted_at=datetime.fromisoformat(msg["created_at"].replace("Z", "+00:00")),
                    raw_data=msg,
                    metadata={
                        "ticker": ticker,
                        "sentiment_label": sentiment.get("basic") if sentiment else None,
                        "likes": msg.get("likes", {}).get("total", 0),
                    },
                ))
            except Exception as e:
                logger.debug(f"Skipping StockTwits message: {e}")
        return posts
