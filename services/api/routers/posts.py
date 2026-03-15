from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import Optional
from datetime import datetime
from db.database import get_db
from models.post import Post

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("")
async def get_posts(
    q: Optional[str] = Query(None, description="Search query"),
    source: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Post).order_by(Post.posted_at.desc()).limit(limit).offset(offset)
    if q:
        stmt = stmt.where(Post.content.ilike(f"%{q}%"))
    if source:
        stmt = stmt.where(Post.source == source)
    result = await db.execute(stmt)
    posts = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "external_id": p.external_id,
            "source": p.source,
            "author": p.author,
            "content": p.content,
            "url": p.url,
            "posted_at": p.posted_at.isoformat() if p.posted_at else None,
        }
        for p in posts
    ]
