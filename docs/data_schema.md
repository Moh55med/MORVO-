# Data Schema Documentation

This document defines the required data structure for integrating with three platforms: SE Ranking, Brand24, and Ayrshare. The schema will guide database table creation and edge function development.

## Table of Contents
- [SE Ranking Data Schema](#se-ranking-data-schema)
- [Brand24 Data Schema](#brand24-data-schema)
- [Ayrshare Data Schema](#ayrshare-data-schema)
- [Common Fields](#common-fields)
- [Database Considerations](#database-considerations)

---

## SE Ranking Data Schema

### Required Fields

| Field Name | Data Type | Description | Required | Example |
|------------|-----------|-------------|----------|---------|
| `keyword` | string | The search keyword being tracked | Yes | "digital marketing" |
| `position` | integer | Current ranking position in search results | Yes | 5 |
| `url` | string | The URL of the ranking page | Yes | "https://example.com/digital-marketing-guide" |
| `volume` | integer | Monthly search volume for the keyword | Yes | 12000 |
| `cpc` | decimal | Cost per click (in USD) | Yes | 2.45 |
| `competition` | decimal | Competition level (0-1) | Yes | 0.75 |
| `previous_position` | integer | Previous ranking position | No | 8 |
| `position_change` | integer | Change in position from previous check | No | 3 |
| `search_engine` | string | Search engine (google, bing, yahoo) | Yes | "google" |
| `location` | string | Geographic location for search | Yes | "United States" |
| `device` | string | Device type (desktop, mobile, tablet) | Yes | "desktop" |
| `tracked_date` | datetime | Date when position was recorded | Yes | "2024-01-15T10:30:00Z" |
| `project_id` | string | SE Ranking project identifier | Yes | "proj_12345" |

### Mock JSON Structure

```json
{
  "keyword": "digital marketing",
  "position": 5,
  "url": "https://example.com/digital-marketing-guide",
  "volume": 12000,
  "cpc": 2.45,
  "competition": 0.75,
  "previous_position": 8,
  "position_change": 3,
  "search_engine": "google",
  "location": "United States",
  "device": "desktop",
  "tracked_date": "2024-01-15T10:30:00Z",
  "project_id": "proj_12345"
}
```

---

## Brand24 Data Schema

### Required Fields

| Field Name | Data Type | Description | Required | Example |
|------------|-----------|-------------|----------|---------|
| `mention_id` | string | Unique identifier for the mention | Yes | "mention_67890" |
| `mention_text` | text | Full text content of the mention | Yes | "Great article about digital marketing trends!" |
| `sentiment` | string | Sentiment analysis (positive, negative, neutral) | Yes | "positive" |
| `sentiment_score` | decimal | Sentiment score (-1 to 1) | Yes | 0.8 |
| `platform` | string | Social media platform or website | Yes | "twitter" |
| `author` | string | Author/username of the mention | Yes | "@marketing_expert" |
| `author_followers` | integer | Number of followers of the author | No | 15000 |
| `author_verified` | boolean | Whether the author is verified | No | true |
| `url` | string | Direct URL to the mention | Yes | "https://twitter.com/marketing_expert/status/123456789" |
| `published_date` | datetime | When the mention was published | Yes | "2024-01-15T14:22:00Z" |
| `collected_date` | datetime | When the mention was collected | Yes | "2024-01-15T15:00:00Z" |
| `reach` | integer | Estimated reach of the mention | No | 25000 |
| `engagement` | integer | Total engagement (likes, shares, comments) | No | 150 |
| `language` | string | Language of the mention | Yes | "en" |
| `country` | string | Country where mention originated | No | "United States" |
| `project_id` | string | Brand24 project identifier | Yes | "brand24_proj_456" |

### Mock JSON Structure

```json
{
  "mention_id": "mention_67890",
  "mention_text": "Great article about digital marketing trends! Really helpful insights for our strategy.",
  "sentiment": "positive",
  "sentiment_score": 0.8,
  "platform": "twitter",
  "author": "@marketing_expert",
  "author_followers": 15000,
  "author_verified": true,
  "url": "https://twitter.com/marketing_expert/status/123456789",
  "published_date": "2024-01-15T14:22:00Z",
  "collected_date": "2024-01-15T15:00:00Z",
  "reach": 25000,
  "engagement": 150,
  "language": "en",
  "country": "United States",
  "project_id": "brand24_proj_456"
}
```

---

## Ayrshare Data Schema

### Required Fields

| Field Name | Data Type | Description | Required | Example |
|------------|-----------|-------------|----------|---------|
| `post_id` | string | Unique identifier for the social media post | Yes | "ayr_post_789" |
| `post_content` | text | Content of the social media post | Yes | "Check out our latest digital marketing guide!" |
| `platform` | string | Social media platform | Yes | "linkedin" |
| `status` | string | Post status (published, scheduled, draft, failed) | Yes | "published" |
| `timestamp` | datetime | When the post was published/scheduled | Yes | "2024-01-15T16:00:00Z" |
| `scheduled_time` | datetime | Scheduled publish time (if applicable) | No | "2024-01-16T09:00:00Z" |
| `media_urls` | array | Array of media file URLs attached to post | No | ["https://example.com/image1.jpg"] |
| `hashtags` | array | Array of hashtags used in the post | No | ["#digitalmarketing", "#strategy"] |
| `mentions` | array | Array of mentioned users/handles | No | ["@partner_company"] |
| `engagement_metrics` | object | Engagement data (likes, shares, comments) | No | {"likes": 45, "shares": 12, "comments": 8} |
| `reach` | integer | Number of people who saw the post | No | 5000 |
| `impressions` | integer | Number of times the post was displayed | No | 7500 |
| `click_through_rate` | decimal | CTR percentage | No | 0.025 |
| `api_response` | object | Raw API response from Ayrshare | No | {"status": "success", "id": "12345"} |
| `error_message` | string | Error message if post failed | No | "Rate limit exceeded" |
| `project_id` | string | Ayrshare project identifier | Yes | "ayr_proj_789" |

### Mock JSON Structure

```json
{
  "post_id": "ayr_post_789",
  "post_content": "Check out our latest digital marketing guide! 🚀 Learn the top strategies for 2024 and boost your online presence. #digitalmarketing #strategy #growth",
  "platform": "linkedin",
  "status": "published",
  "timestamp": "2024-01-15T16:00:00Z",
  "scheduled_time": null,
  "media_urls": [
    "https://example.com/digital-marketing-guide-2024.jpg"
  ],
  "hashtags": [
    "#digitalmarketing",
    "#strategy",
    "#growth"
  ],
  "mentions": [
    "@marketing_partner"
  ],
  "engagement_metrics": {
    "likes": 45,
    "shares": 12,
    "comments": 8,
    "saves": 5
  },
  "reach": 5000,
  "impressions": 7500,
  "click_through_rate": 0.025,
  "api_response": {
    "status": "success",
    "id": "12345",
    "url": "https://linkedin.com/posts/12345"
  },
  "error_message": null,
  "project_id": "ayr_proj_789"
}
```

---

## Common Fields

All data entries should include these common fields for tracking and management:

| Field Name | Data Type | Description | Required | Example |
|------------|-----------|-------------|----------|---------|
| `id` | string | Unique identifier for the record | Yes | "uuid-12345-67890" |
| `source_platform` | string | Platform name (se_ranking, brand24, ayrshare) | Yes | "se_ranking" |
| `created_at` | datetime | When the record was created in our system | Yes | "2024-01-15T10:30:00Z" |
| `updated_at` | datetime | When the record was last updated | Yes | "2024-01-15T10:30:00Z" |
| `is_active` | boolean | Whether the record is currently active | Yes | true |
| `metadata` | object | Additional platform-specific metadata | No | {"api_version": "v2", "rate_limit_remaining": 950} |

---

## Database Considerations

### Table Structure Recommendations

1. **Main Tables**: Create separate tables for each platform to maintain data integrity
2. **Indexing**: Index frequently queried fields (dates, keywords, sentiment, status)
3. **Partitioning**: Consider partitioning by date for large datasets
4. **Data Types**: Use appropriate data types (JSONB for complex objects, TIMESTAMP for dates)

### Data Retention Policy

- **SE Ranking**: Keep historical data for trend analysis (recommended: 2 years)
- **Brand24**: Store mentions for sentiment analysis (recommended: 1 year)
- **Ayrshare**: Maintain post history for performance tracking (recommended: 1 year)

### API Rate Limits

- **SE Ranking**: 1000 requests/day
- **Brand24**: 5000 mentions/month
- **Ayrshare**: 100 posts/day

### Error Handling

All API responses should include error handling for:
- Rate limiting
- Authentication failures
- Network timeouts
- Invalid data formats
- Platform-specific errors

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-01-15 | Initial schema definition |

---

*This schema will be used to guide the development of database tables and edge functions for data integration.*
