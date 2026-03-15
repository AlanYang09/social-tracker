# Celery queue names
QUEUE_DEFAULT = "celery"
QUEUE_ANALYSIS = "analysis"

# Redis channels
CHANNEL_LIVE_FEED = "channel:live_feed"
CHANNEL_ALERTS = "channel:alerts"

# Sentiment labels
SENTIMENT_POSITIVE = "positive"
SENTIMENT_NEGATIVE = "negative"
SENTIMENT_NEUTRAL = "neutral"

# Data sources
SOURCE_STOCKTWITS = "stocktwits"
SOURCE_REDDIT = "reddit"
SOURCE_TWITTER = "twitter"
SOURCE_NITTER = "nitter"
SOURCE_NEWS = "news"

# Default keywords to track
DEFAULT_KEYWORDS = [
    "$TSLA", "$AAPL", "$NVDA", "$GME", "$AMC",
    "bitcoin", "ethereum", "crypto",
    "meme stock", "short squeeze",
]

# Subreddits to monitor
DEFAULT_SUBREDDITS = [
    "wallstreetbets",
    "stocks",
    "investing",
    "CryptoCurrency",
    "StockMarket",
]

# Alert thresholds
SENTIMENT_SPIKE_THRESHOLD = 0.3   # swing within 1 hour
VOLUME_SPIKE_MULTIPLIER = 2.0     # 2x 7-day rolling average
