from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.database import get_db

router = APIRouter(prefix="/api/trends", tags=["trends"])


@router.get("/stocks")
async def get_trending_stocks(
    hours: int = Query(24, description="Lookback window in hours"),
    limit: int = Query(20, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("""
            SELECT
                ticker,
                COUNT(*) as mention_count,
                AVG(sentiment_score) as avg_sentiment
            FROM ticker_mentions
            WHERE mentioned_at >= NOW() - (:hours * INTERVAL '1 hour')
            GROUP BY ticker
            ORDER BY mention_count DESC
            LIMIT :limit
        """),
        {"hours": hours, "limit": limit},
    )
    rows = result.fetchall()
    return [
        {
            "ticker": row.ticker,
            "mention_count": row.mention_count,
            "avg_sentiment": round(float(row.avg_sentiment or 0), 4),
        }
        for row in rows
    ]


@router.get("/sentiment")
async def get_sentiment_timeline(
    ticker: str = Query(...),
    hours: int = Query(24),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("""
            SELECT
                DATE_TRUNC('hour', mentioned_at) as hour,
                AVG(sentiment_score) as avg_sentiment,
                COUNT(*) as mentions
            FROM ticker_mentions
            WHERE ticker = :ticker
              AND mentioned_at >= NOW() - (:hours * INTERVAL '1 hour')
            GROUP BY hour
            ORDER BY hour ASC
        """),
        {"ticker": ticker.upper(), "hours": hours},
    )
    rows = result.fetchall()
    return [
        {
            "hour": row.hour.isoformat(),
            "avg_sentiment": round(float(row.avg_sentiment or 0), 4),
            "mentions": row.mentions,
        }
        for row in rows
    ]


@router.get("/history")
async def get_trend_history(
    ticker: str = Query(...),
    hours: int = Query(24),
    db: AsyncSession = Depends(get_db),
):
    """Trending snapshot history for a ticker — shows how mention velocity changed."""
    result = await db.execute(
        text("""
            SELECT
                snapshot_at,
                mention_count,
                avg_sentiment,
                velocity
            FROM trending_snapshots
            WHERE topic = :ticker
              AND snapshot_at >= NOW() - (:hours * INTERVAL '1 hour')
            ORDER BY snapshot_at ASC
        """),
        {"ticker": ticker.upper(), "hours": hours},
    )
    rows = result.fetchall()
    return [
        {
            "snapshot_at": row.snapshot_at.isoformat(),
            "mention_count": row.mention_count,
            "avg_sentiment": round(float(row.avg_sentiment or 0), 4),
            "velocity": round(float(row.velocity or 0), 2),
        }
        for row in rows
    ]


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Quick system overview: total posts, per-source counts, last collected."""
    result = await db.execute(
        text("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE source = 'stocktwits') as stocktwits,
                COUNT(*) FILTER (WHERE source = 'reddit') as reddit,
                COUNT(*) FILTER (WHERE source = 'nitter') as nitter,
                MAX(collected_at) as last_collected
            FROM posts
        """)
    )
    row = result.fetchone()
    ticker_result = await db.execute(text("SELECT COUNT(DISTINCT ticker) FROM ticker_mentions"))
    ticker_row = ticker_result.fetchone()
    return {
        "total_posts": row.total,
        "by_source": {
            "stocktwits": row.stocktwits,
            "reddit": row.reddit,
            "nitter": row.nitter,
        },
        "tickers_tracked": ticker_row[0],
        "last_collected": row.last_collected.isoformat() if row.last_collected else None,
    }
