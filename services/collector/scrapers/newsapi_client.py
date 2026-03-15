import requests
import logging
import os
from datetime import datetime, timezone
from typing import List
from shared.models import PostIn
from shared.constants import SOURCE_NEWS
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)
BASE_URL = "https://newsapi.org/v2/everything"


class NewsAPIScraper(BaseScraper):
    """Fetches news headlines from NewsAPI (free tier: 100 req/day)."""

    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY", "")

    def scrape(self, keywords: List[str]) -> List[PostIn]:
        if not self.api_key:
            logger.info("NEWS_API_KEY not set — skipping news scrape")
            return []

        posts = []
        # Use top-level keywords only (skip $-prefixed tickers to save quota)
        queries = [k for k in keywords if not k.startswith("$")][:5]
        for query in queries:
            try:
                posts.extend(self._fetch(query))
            except Exception as e:
                logger.warning(f"NewsAPI error for '{query}': {e}")
        return posts

    def _fetch(self, query: str) -> List[PostIn]:
        resp = requests.get(
            BASE_URL,
            params={
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
                "apiKey": self.api_key,
            },
            timeout=10,
        )
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        posts = []
        for art in articles:
            try:
                title = art.get("title") or ""
                desc = art.get("description") or ""
                content = f"{title}. {desc}".strip(". ")
                if not content:
                    continue
                published = art.get("publishedAt", "")
                posted_at = (
                    datetime.fromisoformat(published.replace("Z", "+00:00"))
                    if published
                    else datetime.now(tz=timezone.utc)
                )
                posts.append(PostIn(
                    external_id=f"news_{art.get('url', '')}",
                    source=SOURCE_NEWS,
                    author=art.get("source", {}).get("name", "unknown"),
                    content=content[:1000],
                    url=art.get("url", ""),
                    posted_at=posted_at,
                    metadata={"query": query, "source_name": art.get("source", {}).get("name")},
                ))
            except Exception as e:
                logger.debug(f"Skipping NewsAPI article: {e}")
        return posts
