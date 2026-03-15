from telegram import Update
from telegram.ext import ContextTypes
import psycopg2
import os


def get_db():
    url = os.getenv("DATABASE_URL", "").replace("+asyncpg", "")
    return psycopg2.connect(url)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Social Tracker Bot\n\n"
        "Commands:\n"
        "/top — Top trending stocks right now\n"
        "/sentiment TSLA — Sentiment for a ticker\n"
        "/status — System status\n"
    )


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ticker, COUNT(*) as cnt, AVG(sentiment_score) as avg_s
                FROM ticker_mentions
                WHERE mentioned_at >= NOW() - INTERVAL '24 hours'
                GROUP BY ticker ORDER BY cnt DESC LIMIT 10
            """)
            rows = cur.fetchall()
        conn.close()

        if not rows:
            await update.message.reply_text("No data yet.")
            return

        lines = ["📈 *Top Tickers (24h)*\n"]
        for ticker, cnt, avg_s in rows:
            avg_s = avg_s or 0
            emoji = "🟢" if avg_s > 0.05 else "🔴" if avg_s < -0.05 else "⚪"
            lines.append(f"{emoji} ${ticker} — {cnt} mentions, sentiment: {avg_s:.2f}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def sentiment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /sentiment TSLA")
        return
    ticker = context.args[0].upper().lstrip("$")
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT AVG(sentiment_score), COUNT(*)
                FROM ticker_mentions
                WHERE ticker = %s AND mentioned_at >= NOW() - INTERVAL '24 hours'
            """, (ticker,))
            row = cur.fetchone()
        conn.close()

        if not row or row[1] == 0:
            await update.message.reply_text(f"No data for ${ticker} in the last 24h.")
            return

        avg_s, cnt = row
        emoji = "🟢" if avg_s > 0.05 else "🔴" if avg_s < -0.05 else "⚪"
        await update.message.reply_text(
            f"{emoji} *${ticker}*\nMentions: {cnt}\nAvg sentiment: {avg_s:.3f}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*), MAX(collected_at) FROM posts")
            total, last = cur.fetchone()
        conn.close()
        await update.message.reply_text(
            f"✅ *System Status*\nTotal posts: {total}\nLast collected: {last}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"DB error: {e}")
