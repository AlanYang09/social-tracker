from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from db.database import get_db

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("")
async def get_posts(
    q: Optional[str] = Query(None, description="Search query"),
    source: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    filters = ["1=1"]
    params: dict = {"limit": limit, "offset": offset}
    if q:
        filters.append("p.content ILIKE :q")
        params["q"] = f"%{q}%"
    if source:
        filters.append("p.source = :source")
        params["source"] = source

    where = " AND ".join(filters)
    result = await db.execute(
        text(f"""
            SELECT
                p.id::text,
                p.external_id,
                p.source,
                p.author,
                p.content,
                p.url,
                p.posted_at,
                s.score  AS sentiment_score,
                s.label  AS sentiment_label
            FROM posts p
            LEFT JOIN sentiment_scores s ON s.post_id = p.id AND s.analyzer = 'vader'
            WHERE {where}
            ORDER BY p.posted_at DESC
            LIMIT :limit OFFSET :offset
        """),
        params,
    )
    rows = result.fetchall()
    return [
        {
            "id": row.id,
            "external_id": row.external_id,
            "source": row.source,
            "author": row.author,
            "content": row.content,
            "url": row.url,
            "posted_at": row.posted_at.isoformat() if row.posted_at else None,
            "sentiment_score": float(row.sentiment_score) if row.sentiment_score is not None else None,
            "sentiment_label": row.sentiment_label,
        }
        for row in rows
    ]
