import logging
import json
import psycopg2
import os
import redis as redis_lib
from datetime import datetime, timezone
from main import app
from config import KEYWORDS, SUBREDDITS
from scrapers.stocktwits_client import StockTwitsScraper
from scrapers.reddit_client import RedditScraper
from scrapers.nitter_rss import NitterRSSScraper
from scrapers.newsapi_client import NewsAPIScraper
from shared.constants import CHANNEL_LIVE_FEED

logger = logging.getLogger(__name__)


def get_db():
    url = os.getenv("DATABASE_URL", "").replace("+asyncpg", "")
    return psycopg2.connect(url)


def get_redis():
    return redis_lib.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))


def save_posts(posts):
    if not posts:
        return 0
    conn = get_db()
    r = get_redis()
    saved = 0
    try:
        with conn.cursor() as cur:
            for post in posts:
                try:
                    cur.execute(
                        """
                        INSERT INTO posts (external_id, source, author, content, url, posted_at, raw_data, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (external_id) DO NOTHING
                        """,
                        (
                            post.external_id,
                            post.source,
                            post.author,
                            post.content,
                            post.url,
                            post.posted_at,
                            json.dumps(post.raw_data) if post.raw_data else None,
                            json.dumps(post.metadata) if post.metadata else None,
                        ),
                    )
                    if cur.rowcount > 0:
                        saved += 1
                        # Publish to Redis live feed
                        r.publish(CHANNEL_LIVE_FEED, json.dumps({
                            "external_id": post.external_id,
                            "source": post.source,
                            "author": post.author,
                            "content": post.content[:280],
                            "posted_at": post.posted_at.isoformat(),
                        }))
                        # Queue for analysis
                        app.send_task(
                            "tasks.analyze.analyze_post",
                            args=[post.external_id, post.content],
                            queue="analysis",
                        )
                except Exception as e:
                    logger.debug(f"Insert error: {e}")
        conn.commit()
    finally:
        conn.close()
    return saved


@app.task(name="tasks.scrape_keywords.scrape_stocktwits", bind=True, max_retries=3)
def scrape_stocktwits(self):
    try:
        scraper = StockTwitsScraper()
        posts = scraper.scrape(KEYWORDS)
        saved = save_posts(posts)
        logger.info(f"StockTwits: fetched {len(posts)}, saved {saved} new posts")
        return {"fetched": len(posts), "saved": saved}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@app.task(name="tasks.scrape_keywords.scrape_reddit", bind=True, max_retries=3)
def scrape_reddit(self):
    try:
        scraper = RedditScraper()
        posts = scraper.scrape(KEYWORDS, SUBREDDITS)
        saved = save_posts(posts)
        logger.info(f"Reddit: fetched {len(posts)}, saved {saved} new posts")
        return {"fetched": len(posts), "saved": saved}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@app.task(name="tasks.scrape_keywords.scrape_nitter", bind=True, max_retries=3)
def scrape_nitter(self):
    try:
        scraper = NitterRSSScraper()
        posts = scraper.scrape(KEYWORDS)
        saved = save_posts(posts)
        logger.info(f"Nitter: fetched {len(posts)}, saved {saved} new posts")
        return {"fetched": len(posts), "saved": saved}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=120)


@app.task(name="tasks.scrape_keywords.scrape_news", bind=True, max_retries=3)
def scrape_news(self):
    try:
        scraper = NewsAPIScraper()
        posts = scraper.scrape(KEYWORDS)
        saved = save_posts(posts)
        logger.info(f"NewsAPI: fetched {len(posts)}, saved {saved} new posts")
        return {"fetched": len(posts), "saved": saved}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)
