from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PostIn(BaseModel):
    external_id: str
    source: str  # 'stocktwits', 'reddit', 'twitter', 'nitter'
    author: Optional[str] = None
    content: str
    url: Optional[str] = None
    posted_at: datetime
    raw_data: Optional[dict] = None
    metadata: Optional[dict] = None


class SentimentResult(BaseModel):
    post_id: str
    analyzer: str
    score: float  # -1.0 to 1.0
    label: str    # positive, negative, neutral


class TickerMention(BaseModel):
    post_id: str
    ticker: str
    mentioned_at: datetime
    sentiment_score: Optional[float] = None
