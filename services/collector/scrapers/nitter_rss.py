import feedparser
import logging
from datetime import datetime, timezone
from typing import List
from email.utils import parsedate_to_datetime
from shared.models import PostIn
from shared.constants import SOURCE_NITTER
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

# Public Nitter instances (rotate if one is down)
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
]


class NitterRSSScraper(BaseScraper):
    """Fetches tweets via Nitter RSS feeds — no API key required."""

    def scrape(self, keywords: List[str]) -> List[PostIn]:
        posts = []
        for keyword in keywords:
            try:
                posts.extend(self._fetch_search(keyword))
            except Exception as e:
                logger.warning(f"Nitter RSS error for '{keyword}': {e}")
        return posts

    def _fetch_search(self, query: str) -> List[PostIn]:
        for instance in NITTER_INSTANCES:
            try:
                url = f"{instance}/search/rss?q={query}&f=tweets"
                feed = feedparser.parse(url)
                if feed.entries:
                    return self._parse_feed(feed, query)
            except Exception:
                continue
        return []

    def _parse_feed(self, feed, query: str) -> List[PostIn]:
        posts = []
        for entry in feed.entries[:20]:
            try:
                try:
                    posted_at = parsedate_to_datetime(entry.published)
                except Exception:
                    posted_at = datetime.now(tz=timezone.utc)

                posts.append(PostIn(
                    external_id=f"nitter_{entry.id}",
                    source=SOURCE_NITTER,
                    author=entry.get("author", "unknown"),
                    content=entry.get("summary", ""),
                    url=entry.get("link", ""),
                    posted_at=posted_at,
                    metadata={"query": query},
                ))
            except Exception as e:
                logger.debug(f"Skipping Nitter entry: {e}")
        return posts
