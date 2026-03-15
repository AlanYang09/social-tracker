"""
Calculates trending scores for tickers.
Run this as a periodic task to populate trending_snapshots.
"""
import psycopg2
import os
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


def calculate_trends(hours: int = 1):
    url = os.getenv("DATABASE_URL", "").replace("+asyncpg", "")
    conn = psycopg2.connect(url)
    now = datetime.now(tz=timezone.utc)
    window_start = now - timedelta(hours=hours)

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    tm.ticker,
                    COUNT(*) as mention_count,
                    AVG(tm.sentiment_score) as avg_sentiment
                FROM ticker_mentions tm
                WHERE tm.mentioned_at >= %s
                GROUP BY tm.ticker
                ORDER BY mention_count DESC
                LIMIT 50
                """,
                (window_start,),
            )
            rows = cur.fetchall()

            for row in rows:
                ticker, mention_count, avg_sentiment = row
                cur.execute(
                    """
                    INSERT INTO trending_snapshots (topic, topic_type, mention_count, avg_sentiment, velocity)
                    VALUES (%s, 'stock', %s, %s, %s)
                    """,
                    (ticker, mention_count, avg_sentiment, float(mention_count) / hours),
                )

        conn.commit()
        logger.info(f"Trending snapshot saved: {len(rows)} tickers")
    finally:
        conn.close()
