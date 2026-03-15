import praw
import logging
import os
from datetime import datetime, timezone
from typing import List
from shared.models import PostIn
from shared.constants import SOURCE_REDDIT
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class RedditScraper(BaseScraper):
    """Fetches hot/new posts from target subreddits using PRAW."""

    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID", ""),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
            user_agent=os.getenv("REDDIT_USER_AGENT", "social-tracker/1.0"),
        )

    def scrape(self, keywords: List[str], subreddits: List[str] = None) -> List[PostIn]:
        from config import SUBREDDITS
        subreddits = subreddits or SUBREDDITS
        posts = []
        for sub in subreddits:
            try:
                posts.extend(self._fetch_subreddit(sub))
            except Exception as e:
                logger.warning(f"Reddit error for r/{sub}: {e}")
        return posts

    def _fetch_subreddit(self, subreddit_name: str, limit: int = 50) -> List[PostIn]:
        sub = self.reddit.subreddit(subreddit_name)
        posts = []
        for submission in sub.hot(limit=limit):
            try:
                content = f"{submission.title}\n{submission.selftext or ''}".strip()
                posts.append(PostIn(
                    external_id=f"reddit_{submission.id}",
                    source=SOURCE_REDDIT,
                    author=str(submission.author),
                    content=content[:2000],  # cap at 2000 chars
                    url=f"https://reddit.com{submission.permalink}",
                    posted_at=datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
                    metadata={
                        "subreddit": subreddit_name,
                        "score": submission.score,
                        "num_comments": submission.num_comments,
                        "upvote_ratio": submission.upvote_ratio,
                    },
                ))
            except Exception as e:
                logger.debug(f"Skipping Reddit post: {e}")
        return posts
