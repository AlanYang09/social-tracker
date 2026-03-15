from sqlalchemy import Column, String, Text, DateTime, JSON, UUID
from sqlalchemy.sql import func
import uuid
from db.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(255), unique=True, nullable=False)
    source = Column(String(50), nullable=False)
    author = Column(String(255))
    content = Column(Text, nullable=False)
    url = Column(Text)
    posted_at = Column(DateTime(timezone=True), nullable=False)
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    raw_data = Column(JSON)
    metadata_ = Column("metadata", JSON, default={})
