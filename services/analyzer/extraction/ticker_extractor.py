import re
from typing import List

# Common false positives to exclude
EXCLUDE_TICKERS = {"A", "I", "IT", "AT", "BE", "BY", "TO", "IN", "IS", "OR", "ON", "AN", "AS", "NO"}

TICKER_PATTERN = re.compile(r'\$([A-Z]{1,5})\b')


class TickerExtractor:
    def extract(self, text: str) -> List[str]:
        """Extract stock tickers from text. Handles $AAPL style mentions."""
        matches = TICKER_PATTERN.findall(text.upper())
        return list({t for t in matches if t not in EXCLUDE_TICKERS})
