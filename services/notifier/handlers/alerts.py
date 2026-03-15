import asyncio
import logging
import psycopg2
import os
from telegram import Bot

logger = logging.getLogger(__name__)


def get_db():
    url = os.getenv("DATABASE_URL", "").replace("+asyncpg", "")
    return psycopg2.connect(url)


async def check_and_send_alerts(bot: Bot, chat_id: str):
    """Check for sentiment spikes and volume spikes, send Telegram alerts."""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            # Detect sentiment spike: avg sentiment last 1h vs prior 1h swing > 0.3
            cur.execute("""
                SELECT ticker,
                    AVG(CASE WHEN mentioned_at >= NOW() - INTERVAL '1 hour' THEN sentiment_score END) as recent,
                    AVG(CASE WHEN mentioned_at BETWEEN NOW() - INTERVAL '2 hours' AND NOW() - INTERVAL '1 hour' THEN sentiment_score END) as prior
                FROM ticker_mentions
                WHERE mentioned_at >= NOW() - INTERVAL '2 hours'
                GROUP BY ticker
                HAVING COUNT(*) > 5
            """)
            rows = cur.fetchall()

        conn.close()
        for ticker, recent, prior in rows:
            if recent is None or prior is None:
                continue
            swing = abs(recent - prior)
            if swing >= 0.3:
                direction = "🟢 surge" if recent > prior else "🔴 crash"
                msg = (
                    f"⚡ *Sentiment {direction}* for ${ticker}\n"
                    f"Last hour: {recent:.2f} | Prior hour: {prior:.2f}\n"
                    f"Swing: {swing:.2f}"
                )
                await bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"Alert check error: {e}")
