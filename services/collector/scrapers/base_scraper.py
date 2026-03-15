from abc import ABC, abstractmethod
from typing import List
from shared.models import PostIn


class BaseScraper(ABC):
    """All scrapers must implement this interface."""

    @abstractmethod
    def scrape(self, keywords: List[str]) -> List[PostIn]:
        """Fetch posts matching the given keywords."""
        ...

    def deduplicate(self, posts: List[PostIn], seen_ids: set) -> List[PostIn]:
        """Filter out posts whose external_id is already in seen_ids."""
        unique = []
        for post in posts:
            if post.external_id not in seen_ids:
                seen_ids.add(post.external_id)
                unique.append(post)
        return unique
