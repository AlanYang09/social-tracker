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
