CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS posts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id     VARCHAR(255) UNIQUE NOT NULL,
    source          VARCHAR(50) NOT NULL,
    author          VARCHAR(255),
    content         TEXT NOT NULL,
    url             TEXT,
    posted_at       TIMESTAMPTZ NOT NULL,
    collected_at    TIMESTAMPTZ DEFAULT NOW(),
    raw_data        JSONB,
    metadata        JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS sentiment_scores (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id     UUID REFERENCES posts(id) ON DELETE CASCADE,
    analyzer    VARCHAR(50) NOT NULL,
    score       DECIMAL(5,4),
    label       VARCHAR(20),
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(post_id, analyzer)
);

CREATE TABLE IF NOT EXISTS ticker_mentions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id         UUID REFERENCES posts(id) ON DELETE CASCADE,
    ticker          VARCHAR(10) NOT NULL,
    mentioned_at    TIMESTAMPTZ NOT NULL,
    sentiment_score DECIMAL(5,4)
);

CREATE TABLE IF NOT EXISTS trending_snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic           VARCHAR(255) NOT NULL,
    topic_type      VARCHAR(50),
    mention_count   INTEGER,
    avg_sentiment   DECIMAL(5,4),
    velocity        DECIMAL(10,4),
    snapshot_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_posts_posted_at ON posts(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_source ON posts(source);
CREATE INDEX IF NOT EXISTS idx_ticker_mentions_ticker ON ticker_mentions(ticker, mentioned_at DESC);
CREATE INDEX IF NOT EXISTS idx_trending_snapshots_at ON trending_snapshots(snapshot_at DESC);
