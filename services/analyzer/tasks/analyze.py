import logging
import json
import psycopg2
import os
import re
from main import app
from sentiment.vader_analyzer import VaderAnalyzer
from extraction.ticker_extractor import TickerExtractor

logger = logging.getLogger(__name__)
vader = VaderAnalyzer()
extractor = TickerExtractor()


def get_db():
    url = os.getenv("DATABASE_URL", "").replace("+asyncpg", "")
    return psycopg2.connect(url)


@app.task(name="tasks.analyze.analyze_post", bind=True, max_retries=3)
def analyze_post(self, external_id: str, content: str):
    try:
        sentiment = vader.analyze(content)
        tickers = extractor.extract(content)
        conn = get_db()
        try:
            with conn.cursor() as cur:
                # Get internal post UUID
                cur.execute("SELECT id, posted_at FROM posts WHERE external_id = %s", (external_id,))
                row = cur.fetchone()
                if not row:
                    return
                post_uuid, posted_at = row

                # Save sentiment
                cur.execute(
                    """
                    INSERT INTO sentiment_scores (post_id, analyzer, score, label)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (str(post_uuid), "vader", sentiment["score"], sentiment["label"]),
                )

                # Save ticker mentions
                for ticker in tickers:
                    cur.execute(
                        """
                        INSERT INTO ticker_mentions (post_id, ticker, mentioned_at, sentiment_score)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                        """,
                        (str(post_uuid), ticker, posted_at, sentiment["score"]),
                    )

            conn.commit()
            logger.debug(f"Analyzed {external_id}: sentiment={sentiment['label']}, tickers={tickers}")
        finally:
            conn.close()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
