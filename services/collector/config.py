import os
from shared.constants import DEFAULT_KEYWORDS, DEFAULT_SUBREDDITS

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://tracker:tracker@postgres:5432/tracker")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "social-tracker/1.0")

KEYWORDS = DEFAULT_KEYWORDS
SUBREDDITS = DEFAULT_SUBREDDITS

# How often to scrape (seconds)
SCRAPE_INTERVAL = 300  # 5 minutes
