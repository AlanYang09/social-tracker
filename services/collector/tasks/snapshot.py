"""
Periodic task: snapshot trending tickers into trending_snapshots table.
Runs every 15 minutes via the collector beat schedule.
"""
import logging
import psycopg2
import os
from datetime import datetime, timedelta, timezone
from main import app

logger = logging.getLogger(__name__)


def get_db():
    url = os.getenv("DATABASE_URL", "").replace("+asyncpg", "")
    return psycopg2.connect(url)


@app.task(name="tasks.snapshot.snapshot_trends", bind=True, max_retries=2)
def snapshot_trends(self):
    """Compute trending tickers over last 1h and write to trending_snapshots."""
    try:
        conn = get_db()
        now = datetime.now(tz=timezone.utc)
        window_start = now - timedelta(hours=1)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        ticker,
                        COUNT(*) AS mention_count,
                        AVG(sentiment_score) AS avg_sentiment
                    FROM ticker_mentions
                    WHERE mentioned_at >= %s
                    GROUP BY ticker
                    ORDER BY mention_count DESC
                    LIMIT 50
                    """,
                    (window_start,),
                )
                rows = cur.fetchall()

                for ticker, mention_count, avg_sentiment in rows:
                    cur.execute(
                        """
                        INSERT INTO trending_snapshots
                            (topic, topic_type, mention_count, avg_sentiment, velocity, snapshot_at)
                        VALUES (%s, 'stock', %s, %s, %s, NOW())
                        """,
                        (ticker, mention_count, float(avg_sentiment or 0), float(mention_count)),
                    )

            conn.commit()
            logger.info(f"Trend snapshot: {len(rows)} tickers written")
            return {"tickers": len(rows)}
        finally:
            conn.close()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
