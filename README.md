# Social Tracker

Real-time social media sentiment dashboard tracking stocks, memes, and trending topics across Twitter/X, Reddit, and StockTwits.

## Features

- **Multi-source scraping**: StockTwits, Reddit (r/wallstreetbets etc.), Nitter RSS (Twitter)
- **Sentiment analysis**: VADER for all posts, FinBERT (Phase 2) for financial content
- **Trending stocks**: Real-time ticker mention counts + sentiment scores
- **Live dashboard**: WebSocket-powered live feed, searchable post history, sentiment charts
- **Telegram bot**: `/top`, `/sentiment TSLA`, spike alerts

## Quick Start

1. Copy `.env.example` to `.env` and fill in your credentials:
   - Reddit API keys from https://www.reddit.com/prefs/apps
   - Telegram bot token from @BotFather

2. Start everything:
   ```bash
   docker compose up --build
   ```

3. Open http://localhost:3000

## Services

| Service | Port | Description |
|---|---|---|
| frontend | 3000 | Next.js dashboard |
| api | 8000 | FastAPI REST + WebSocket |
| collector | — | Celery scraper workers |
| analyzer | — | Celery NLP workers |
| notifier | — | Telegram bot |
| postgres | 5432 | Data store |
| redis | 6379 | Task queue + pub/sub |

## API Endpoints

- `GET /api/posts?q=&source=&limit=` — search posts
- `GET /api/trends/stocks?hours=24` — trending tickers
- `GET /api/trends/sentiment?ticker=TSLA` — sentiment timeline
- `WS /ws/live-feed` — real-time post stream

## Roadmap

- [ ] Phase 1: MVP (current)
- [ ] Phase 2: Real-time WebSocket live feed + Telegram spike alerts
- [ ] Phase 3: Meme detection, BERTopic clustering, FinBERT
- [ ] Phase 4: CI/CD auto-deploy, data retention policies
