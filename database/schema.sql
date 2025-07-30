-- MORVO Database Schema for Supabase (PostgreSQL)
-- Based on data schema for SE Ranking, Brand24, and Ayrshare integration

-- Enable UUID extension for generating unique IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- SEO SIGNALS TABLE (SE Ranking Data)
-- =====================================================

CREATE TABLE seo_signals (
    -- Common Fields
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_platform VARCHAR(50) NOT NULL DEFAULT 'se_ranking',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    
    -- SE Ranking Specific Fields
    keyword VARCHAR(500) NOT NULL,
    position INTEGER NOT NULL,
    url TEXT NOT NULL,
    volume INTEGER NOT NULL,
    cpc DECIMAL(10,2) NOT NULL,
    competition DECIMAL(3,2) NOT NULL CHECK (competition >= 0 AND competition <= 1),
    previous_position INTEGER,
    position_change INTEGER,
    search_engine VARCHAR(50) NOT NULL,
    location VARCHAR(100) NOT NULL,
    device VARCHAR(50) NOT NULL,
    tracked_date TIMESTAMP WITH TIME ZONE NOT NULL,
    project_id VARCHAR(100) NOT NULL,
    
    -- Constraints
    CONSTRAINT seo_signals_position_check CHECK (position > 0),
    CONSTRAINT seo_signals_volume_check CHECK (volume >= 0),
    CONSTRAINT seo_signals_cpc_check CHECK (cpc >= 0),
    CONSTRAINT seo_signals_search_engine_check CHECK (search_engine IN ('google', 'bing', 'yahoo')),
    CONSTRAINT seo_signals_device_check CHECK (device IN ('desktop', 'mobile', 'tablet'))
);

-- Indexes for SEO Signals
CREATE INDEX idx_seo_signals_keyword ON seo_signals(keyword);
CREATE INDEX idx_seo_signals_position ON seo_signals(position);
CREATE INDEX idx_seo_signals_tracked_date ON seo_signals(tracked_date);
CREATE INDEX idx_seo_signals_project_id ON seo_signals(project_id);
CREATE INDEX idx_seo_signals_search_engine ON seo_signals(search_engine);
CREATE INDEX idx_seo_signals_location ON seo_signals(location);
CREATE INDEX idx_seo_signals_device ON seo_signals(device);
CREATE INDEX idx_seo_signals_created_at ON seo_signals(created_at);
CREATE INDEX idx_seo_signals_is_active ON seo_signals(is_active);

-- Composite indexes for common queries
CREATE INDEX idx_seo_signals_keyword_project ON seo_signals(keyword, project_id);
CREATE INDEX idx_seo_signals_date_project ON seo_signals(tracked_date, project_id);
CREATE INDEX idx_seo_signals_engine_location ON seo_signals(search_engine, location);

-- =====================================================
-- MENTIONS TABLE (Brand24 Data)
-- =====================================================

CREATE TABLE mentions (
    -- Common Fields
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_platform VARCHAR(50) NOT NULL DEFAULT 'brand24',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    
    -- Brand24 Specific Fields
    mention_id VARCHAR(100) UNIQUE NOT NULL,
    mention_text TEXT NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    sentiment_score DECIMAL(3,2) NOT NULL CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    platform VARCHAR(50) NOT NULL,
    author VARCHAR(200) NOT NULL,
    author_followers INTEGER CHECK (author_followers >= 0),
    author_verified BOOLEAN DEFAULT FALSE,
    url TEXT NOT NULL,
    published_date TIMESTAMP WITH TIME ZONE NOT NULL,
    collected_date TIMESTAMP WITH TIME ZONE NOT NULL,
    reach INTEGER CHECK (reach >= 0),
    engagement INTEGER CHECK (engagement >= 0),
    language VARCHAR(10) NOT NULL,
    country VARCHAR(100),
    project_id VARCHAR(100) NOT NULL,
    
    -- Constraints
    CONSTRAINT mentions_sentiment_check CHECK (sentiment IN ('positive', 'negative', 'neutral')),
    CONSTRAINT mentions_published_collected_check CHECK (published_date <= collected_date)
);

-- Indexes for Mentions
CREATE INDEX idx_mentions_mention_id ON mentions(mention_id);
CREATE INDEX idx_mentions_sentiment ON mentions(sentiment);
CREATE INDEX idx_mentions_sentiment_score ON mentions(sentiment_score);
CREATE INDEX idx_mentions_platform ON mentions(platform);
CREATE INDEX idx_mentions_author ON mentions(author);
CREATE INDEX idx_mentions_published_date ON mentions(published_date);
CREATE INDEX idx_mentions_collected_date ON mentions(collected_date);
CREATE INDEX idx_mentions_project_id ON mentions(project_id);
CREATE INDEX idx_mentions_language ON mentions(language);
CREATE INDEX idx_mentions_country ON mentions(country);
CREATE INDEX idx_mentions_created_at ON mentions(created_at);
CREATE INDEX idx_mentions_is_active ON mentions(is_active);

-- Full-text search index for mention_text
CREATE INDEX idx_mentions_text_search ON mentions USING GIN(to_tsvector('english', mention_text));

-- Composite indexes for common queries
CREATE INDEX idx_mentions_sentiment_project ON mentions(sentiment, project_id);
CREATE INDEX idx_mentions_platform_date ON mentions(platform, published_date);
CREATE INDEX idx_mentions_author_verified ON mentions(author, author_verified);

-- =====================================================
-- POSTS TABLE (Ayrshare Data)
-- =====================================================

CREATE TABLE posts (
    -- Common Fields
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_platform VARCHAR(50) NOT NULL DEFAULT 'ayrshare',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    
    -- Ayrshare Specific Fields
    post_id VARCHAR(100) UNIQUE NOT NULL,
    post_content TEXT NOT NULL,
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    scheduled_time TIMESTAMP WITH TIME ZONE,
    media_urls TEXT[], -- Array of media URLs
    hashtags TEXT[], -- Array of hashtags
    mentions TEXT[], -- Array of mentioned users
    engagement_metrics JSONB, -- Object with likes, shares, comments, etc.
    reach INTEGER CHECK (reach >= 0),
    impressions INTEGER CHECK (impressions >= 0),
    click_through_rate DECIMAL(5,4) CHECK (click_through_rate >= 0 AND click_through_rate <= 1),
    api_response JSONB, -- Raw API response
    error_message TEXT,
    project_id VARCHAR(100) NOT NULL,
    
    -- Constraints
    CONSTRAINT posts_status_check CHECK (status IN ('published', 'scheduled', 'draft', 'failed')),
    CONSTRAINT posts_timestamp_scheduled_check CHECK (scheduled_time IS NULL OR timestamp <= scheduled_time)
);

-- Indexes for Posts
CREATE INDEX idx_posts_post_id ON posts(post_id);
CREATE INDEX idx_posts_platform ON posts(platform);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_timestamp ON posts(timestamp);
CREATE INDEX idx_posts_scheduled_time ON posts(scheduled_time);
CREATE INDEX idx_posts_project_id ON posts(project_id);
CREATE INDEX idx_posts_created_at ON posts(created_at);
CREATE INDEX idx_posts_is_active ON posts(is_active);

-- GIN indexes for array fields
CREATE INDEX idx_posts_hashtags ON posts USING GIN(hashtags);
CREATE INDEX idx_posts_mentions ON posts USING GIN(mentions);
CREATE INDEX idx_posts_media_urls ON posts USING GIN(media_urls);

-- Full-text search index for post_content
CREATE INDEX idx_posts_content_search ON posts USING GIN(to_tsvector('english', post_content));

-- Composite indexes for common queries
CREATE INDEX idx_posts_platform_status ON posts(platform, status);
CREATE INDEX idx_posts_project_status ON posts(project_id, status);
CREATE INDEX idx_posts_timestamp_project ON posts(timestamp, project_id);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =====================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables
CREATE TRIGGER update_seo_signals_updated_at 
    BEFORE UPDATE ON seo_signals 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mentions_updated_at 
    BEFORE UPDATE ON mentions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_posts_updated_at 
    BEFORE UPDATE ON posts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE seo_signals IS 'Stores SEO ranking data from SE Ranking platform';
COMMENT ON TABLE mentions IS 'Stores brand mentions and sentiment data from Brand24 platform';
COMMENT ON TABLE posts IS 'Stores social media posts and engagement data from Ayrshare platform';

COMMENT ON COLUMN seo_signals.keyword IS 'The search keyword being tracked';
COMMENT ON COLUMN seo_signals.position IS 'Current ranking position in search results';
COMMENT ON COLUMN seo_signals.competition IS 'Competition level (0-1 scale)';
COMMENT ON COLUMN seo_signals.position_change IS 'Change in position from previous check';

COMMENT ON COLUMN mentions.sentiment IS 'Sentiment analysis: positive, negative, or neutral';
COMMENT ON COLUMN mentions.sentiment_score IS 'Sentiment score ranging from -1 to 1';
COMMENT ON COLUMN mentions.engagement IS 'Total engagement (likes, shares, comments)';

COMMENT ON COLUMN posts.status IS 'Post status: published, scheduled, draft, or failed';
COMMENT ON COLUMN posts.engagement_metrics IS 'JSON object containing likes, shares, comments, saves';
COMMENT ON COLUMN posts.click_through_rate IS 'CTR as decimal (e.g., 0.025 for 2.5%)';
