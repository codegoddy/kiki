# AI-Powered Content Recommendations

This document describes the enhanced AI-powered recommendation system added to the FastAPI application. The system provides personalized content recommendations using advanced machine learning algorithms and real-time user behavior analysis.

## Overview

The recommendation system combines multiple algorithms to provide highly personalized content suggestions:

- **Collaborative Filtering**: Finds users with similar preferences and recommends content they enjoyed
- **Content-Based Filtering**: Recommends content similar to what the user has previously engaged with
- **Trending Analysis**: Identifies and recommends popular content in real-time
- **Hybrid Approach**: Combines multiple algorithms with learned weights for optimal recommendations

## Architecture

### Models

The system uses several new database models to track user behavior and preferences:

- `UserInteraction`: Logs all user interactions (views, likes, shares, comments, etc.)
- `UserPreference`: Stores learned user preferences for categories, topics, and authors
- `ContentEmbedding`: Stores AI-generated content embeddings for similarity calculations
- `RecommendationFeedback`: Tracks user feedback on recommendations for continuous improvement
- `SimilarityScore`: Pre-computed similarity scores between content pieces
- `TrendingContent`: Real-time trending content with engagement metrics

### Services

- **EnhancedRecommendationService**: Core recommendation engine with multiple algorithms
- **Background Task Manager**: Handles batch processing and periodic updates
- **AI Service Integration**: Uses existing AI service for content analysis and embeddings

### API Endpoints

All recommendation endpoints are available under `/api/v1/recommendations/`

## API Documentation

### Core Recommendation Endpoints

#### 1. Log User Interaction

```http
POST /api/v1/recommendations/interactions/log
```

Logs user interactions for recommendation learning. Supports multiple interaction types.

**Request Body:**

```json
{
  "user_id": 1,
  "post_id": 123,
  "interaction_type": "like",  // view, like, share, comment, save, click, dismiss, report
  "score": 1.0,
  "time_spent_seconds": 45,
  "scroll_depth": 0.8,
  "session_id": "sess_12345"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Interaction logged successfully",
  "timestamp": 1703123456.789
}
```

#### 2. Get Personalized Recommendations

```http
POST /api/v1/recommendations/personalized
```

Returns personalized content recommendations using hybrid algorithm approach.

**Request Body:**

```json
{
  "user_id": 1,
  "limit": 10,
  "include_types": ["personalized", "similar", "trending"]
}
```

**Response:**

```json
{
  "recommendations": [
    {
      "post_id": 124,
      "score": 0.85,
      "reason": "Based on your reading history",
      "algorithm": "collaborative",
      "confidence": 0.9
    },
    {
      "post_id": 125,
      "score": 0.78,
      "reason": "Trending in your favorite categories",
      "algorithm": "trending",
      "confidence": 0.8
    }
  ],
  "algorithm": "hybrid",
  "generated_at": 1703123456.789,
  "total_count": 2
}
```

#### 3. Find Similar Content

```http
POST /api/v1/recommendations/similar
```

Finds content similar to a specific post using AI embeddings.

**Request Body:**

```json
{
  "post_id": 123,
  "limit": 5
}
```

**Response:**

```json
{
  "similar_posts": [
    {
      "post_id": 124,
      "similarity_score": 0.92,
      "algorithm": "ai_embeddings",
      "confidence": 0.9
    }
  ],
  "source_post_id": 123,
  "generated_at": 1703123456.789
}
```

### Analytics and Insights

#### 4. Get Trending Content

```http
GET /api/v1/recommendations/trending?limit=10&timeframe=day&category=technology
```

Returns trending content with engagement analytics.

**Query Parameters:**

- `limit` (int): Number of posts to return (1-50)
- `timeframe` (str): Analysis period - "hour", "day", or "week"
- `category` (str, optional): Filter by category

**Response:**

```json
{
  "trending_posts": [
    {
      "post_id": 126,
      "title": "AI Breakthrough in 2024",
      "author": "tech_writer",
      "trend_score": 0.95,
      "velocity": 0.8,
      "views_count": 1500,
      "likes_count": 120,
      "shares_count": 45,
      "comments_count": 30,
      "timeframe": "day",
      "category": "technology"
    }
  ],
  "timeframe": "day",
  "generated_at": 1703123456.789,
  "total_count": 1
}
```

#### 5. Get User Analytics

```http
GET /api/v1/recommendations/analytics/1?days=30
```

Provides comprehensive analytics about user engagement and recommendation performance.

**Query Parameters:**

- `days` (int): Analysis period in days (1-365)

**Response:**

```json
{
  "user_id": 1,
  "analysis_period_days": 30,
  "total_interactions": 156,
  "interaction_types": {
    "view": 89,
    "like": 34,
    "share": 12,
    "comment": 21
  },
  "engagement_rate": 0.43,
  "top_preferences": [
    {
      "type": "category",
      "value": "technology",
      "strength": 0.85,
      "confidence": 0.9,
      "interactions": 45
    }
  ],
  "recommendation_accuracy": 0.78,
  "generated_at": 1703123456.789
}
```

### User Preferences

#### 6. View User Preferences

```http
GET /api/v1/recommendations/preferences/1?limit=20
```

Shows learned user preferences for transparency and control.

**Query Parameters:**

- `limit` (int): Maximum number of preferences to return (1-100)

**Response:**

```json
{
  "user_id": 1,
  "total_preferences": 15,
  "preferences": [
    {
      "id": 1,
      "type": "category",
      "value": "technology",
      "strength": 0.85,
      "confidence": 0.9,
      "interaction_count": 45,
      "positive_interactions": 42,
      "negative_interactions": 3,
      "last_interaction": "2024-01-15T10:30:00"
    }
  ],
  "generated_at": 1703123456.789
}
```

#### 7. Delete User Preference

```http
DELETE /api/v1/recommendations/preferences/1/5
```

Allows users to remove learned preferences they disagree with.

**Response:**

```json
{
  "success": true,
  "message": "Preference removed successfully",
  "preference_id": 5
}
```

### Advanced Features

#### 8. Explore New Content

```http
GET /api/v1/recommendations/explore/1?limit=10&exclude_categories=technology
```

Helps users discover new topics and creators outside their usual preferences.

**Query Parameters:**

- `limit` (int): Number of exploration items (1-20)
- `exclude_categories` (list): Categories to avoid
- `exclude_authors` (list): Authors to avoid

**Response:**

```json
{
  "user_id": 1,
  "exploration_recommendations": [
    {
      "post_id": 200,
      "title": "Ancient History Discovery",
      "reason": "Discover something completely new",
      "diversity_score": 0.9
    }
  ],
  "strategy": "diversity_first",
  "generated_at": 1703123456.789
}
```

#### 9. Cold Start Recommendations

```http
GET /api/v1/recommendations/cold-start/1?interests=technology,ai&limit=5
```

Provides recommendations for new users with minimal interaction history.

**Query Parameters:**

- `interests` (list): User-provided initial interests (optional)
- `limit` (int): Number of recommendations (1-20)

**Response:**

```json
{
  "user_id": 1,
  "cold_start_recommendations": [
    {
      "post_id": 201,
      "title": "Getting Started with AI",
      "reason": "Popular starter content for your interests",
      "confidence": 0.7
    }
  ],
  "strategy": "popularity_based",
  "interests_provided": true,
  "generated_at": 1703123456.789
}
```

#### 10. Submit Feedback

```http
POST /api/v1/recommendations/feedback
```

Allows users to provide direct feedback on recommendations for improvement.

**Request Body:**

```json
{
  "user_id": 1,
  "post_id": 124,
  "feedback_type": "click",  // click, like, share, save, dismiss, report
  "feedback_score": 1.0,
  "recommendation_type": "personalized"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Feedback recorded successfully",
  "timestamp": 1703123456.789
}
```

#### 11. Health Check

```http
GET /api/v1/recommendations/health
```

Monitors the health status of the recommendation system.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "algorithms": {
    "collaborative_filtering": true,
    "content_based": true,
    "trending": true,
    "hybrid_recommendations": true
  },
  "database_connection": true,
  "ai_service": true
}
```

## Algorithm Details

### Collaborative Filtering

The system identifies users with similar preferences by:

1. Finding users who have interacted with similar content
2. Calculating cosine similarity between user preference vectors
3. Recommending content that similar users have positively engaged with
4. Weighting recommendations by similarity score and user engagement history

### Content-Based Filtering

Recommendations are based on content similarity:

1. Extract features from user interactions (categories, authors, topics, sentiment)
2. Generate content embeddings using AI models
3. Calculate similarity between user preferences and candidate content
4. Rank content by similarity scores and user preference strength

### Trending Algorithm

Real-time trending detection:

1. Track engagement metrics (views, likes, shares, comments) over time
2. Calculate velocity (rate of change) for engagement
3. Apply decay factors to give more weight to recent activity
4. Combine multiple time windows (hour, day, week) for comprehensive trending scores

### Hybrid Approach

The system combines multiple algorithms with learned weights:

- **Collaborative Filtering** (40%): Leverages collective user behavior
- **Content-Based** (30%): Uses content similarity and user preferences
- **Trending** (20%): Incorporates real-time popularity
- **Diversity** (10%): Ensures diverse recommendations to avoid filter bubbles

## Background Tasks

The system runs several background tasks for continuous optimization:

### Content Analysis

- **Frequency**: Every 5 minutes
- **Purpose**: Analyze new content and generate embeddings
- **Process**: Generate AI embeddings, calculate similarities, update trending scores

### Preference Updates

- **Frequency**: Every 30 minutes
- **Purpose**: Update user preferences based on recent interactions
- **Process**: Analyze interaction patterns, update preference strengths and confidence

### Similarity Calculations

- **Frequency**: Every hour
- **Purpose**: Pre-compute content similarities for faster recommendations
- **Process**: Generate similarity scores between content pairs

### Trending Updates

- **Frequency**: Every 10 minutes
- **Purpose**: Keep trending scores current
- **Process**: Update engagement metrics and trending rankings

### Model Training

- **Frequency**: Daily
- **Purpose**: Train and update recommendation models
- **Process**: Adjust algorithm weights based on feedback performance

### Data Cleanup

- **Frequency**: Weekly
- **Purpose**: Maintain system performance by cleaning old data
- **Process**: Remove old interactions, inactive preferences, low-confidence similarities

## Configuration

### Environment Variables

```bash
# Recommendation System Configuration
RECOMMENDATION_ENABLED=true
RECOMMENDATION_CACHE_SIZE=1000
RECOMMENDATION_BATCH_SIZE=50
RECOMMENDATION_MAX_RECOMMENDATIONS=20
RECOMMENDATION_SIMILARITY_THRESHOLD=0.1
RECOMMENDATION_CONFIDENCE_THRESHOLD=0.5

# Algorithm Weights (optional - will be learned automatically)
RECOMMENDATION_COLLABORATIVE_WEIGHT=0.4
RECOMMENDATION_CONTENT_WEIGHT=0.3
RECOMMENDATION_TRENDING_WEIGHT=0.2
RECOMMENDATION_DIVERSITY_WEIGHT=0.1

# Background Task Intervals (seconds)
RECOMMENDATION_CONTENT_ANALYSIS_INTERVAL=300
RECOMMENDATION_PREFERENCE_UPDATE_INTERVAL=1800
RECOMMENDATION_SIMILARITY_INTERVAL=3600
RECOMMENDATION_TRENDING_INTERVAL=600
RECOMMENDATION_TRAINING_INTERVAL=86400
RECOMMENDATION_CLEANUP_INTERVAL=604800
```

### Database Schema

The recommendation system adds several new tables:

```sql
-- User interactions
CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    post_id INTEGER NOT NULL REFERENCES posts(id),
    interaction_type VARCHAR(50) NOT NULL,
    interaction_score FLOAT DEFAULT 1.0,
    session_id VARCHAR(255),
    user_agent TEXT,
    referrer TEXT,
    time_spent_seconds INTEGER DEFAULT 0,
    scroll_depth FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User preferences
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    preference_type VARCHAR(50) NOT NULL,
    preference_value VARCHAR(255) NOT NULL,
    strength FLOAT DEFAULT 0.0,
    confidence FLOAT DEFAULT 0.0,
    interaction_count INTEGER DEFAULT 0,
    positive_interactions INTEGER DEFAULT 0,
    negative_interactions INTEGER DEFAULT 0,
    first_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Content embeddings
CREATE TABLE content_embeddings (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id),
    embedding_type VARCHAR(50) DEFAULT 'text',
    embedding_vector TEXT NOT NULL,  -- JSON-encoded vector
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    vector_dimension INTEGER NOT NULL,
    quality_score FLOAT DEFAULT 0.0,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Additional tables for feedback, similarities, and trending...
```

## Performance Considerations

### Caching

- Content embeddings are cached for faster similarity calculations
- User preference vectors are cached to reduce database queries
- Pre-computed similarity scores reduce real-time computation
- Recommendation results can be cached for popular users

### Indexing

Key database indexes for performance:

```sql
-- User interactions
CREATE INDEX idx_user_interaction_user_type ON user_interactions(user_id, interaction_type);
CREATE INDEX idx_user_interaction_post_type ON user_interactions(post_id, interaction_type);
CREATE INDEX idx_user_interaction_created ON user_interactions(created_at);

-- User preferences
CREATE INDEX idx_user_preference_unique ON user_preferences(user_id, preference_type, preference_value);
CREATE INDEX idx_user_preference_strength ON user_preferences(strength);

-- Content embeddings
CREATE INDEX idx_content_embedding_post_type ON content_embeddings(post_id, embedding_type);
```

### Scaling Considerations

- **Horizontal Scaling**: Multiple recommendation service instances can run in parallel
- **Database Optimization**: Regular cleanup of old data maintains query performance
- **Background Processing**: CPU-intensive tasks run asynchronously to avoid blocking API responses
- **Monitoring**: Built-in health checks and performance metrics

## Testing

Comprehensive test suites are provided:

### Unit Tests

- `app/tests/test_recommendation_service.py`: Tests for recommendation algorithms
- `app/tests/test_recommendation_api.py`: Tests for API endpoints

### Test Coverage

- All recommendation algorithms
- User interaction logging
- Preference learning and updates
- Similarity calculations
- Trending content analysis
- Background task execution
- Error handling and edge cases

### Running Tests

```bash
# Run all recommendation tests
pytest app/tests/test_recommendation_service.py -v
pytest app/tests/test_recommendation_api.py -v

# Run with coverage
pytest --cov=app.services.recommendation_service --cov=app.api.recommendations
```

## Monitoring and Analytics

### Key Metrics

- **Recommendation Accuracy**: Percentage of recommendations that receive positive feedback
- **Click-Through Rate**: Percentage of recommendations that users click on
- **User Engagement**: Overall user engagement with recommended content
- **Algorithm Performance**: Individual performance of each recommendation algorithm
- **Diversity Score**: Measure of content diversity in recommendations

### Health Monitoring

- Service status endpoint provides real-time health information
- Background task monitoring with execution time tracking
- Database connection and performance monitoring
- AI service availability checks

## Future Enhancements

Planned improvements for the recommendation system:

1. **Deep Learning Models**: Neural collaborative filtering and content-based models
2. **Real-time Personalization**: Instant recommendation updates based on current session
3. **Multi-modal Recommendations**: Incorporate images and videos in recommendations
4. **Advanced Diversity**: More sophisticated diversity algorithms to prevent filter bubbles
5. **A/B Testing Framework**: Built-in framework for testing recommendation algorithm changes
6. **Explainable AI**: Provide explanations for why specific content was recommended
7. **Privacy-preserving Recommendations**: Implement federated learning for privacy

## Troubleshooting

### Common Issues

1. **No Recommendations Returned**
   - Check if user has any interaction history
   - Verify database connections and query performance
   - Ensure content analysis background tasks are running

2. **Poor Recommendation Quality**
   - Review algorithm weights and feedback scores
   - Check if preference learning is working correctly
   - Monitor background task execution and performance

3. **High Response Times**
   - Enable caching for frequently requested recommendations
   - Optimize database queries with proper indexes
   - Consider scaling recommendation service instances

4. **Memory Usage Growth**
   - Ensure cleanup tasks are running regularly
   - Monitor cache sizes and implement cache eviction policies
   - Review background task intervals to prevent excessive data accumulation

### Debug Endpoints

- `/api/v1/recommendations/health`: System health status
- `/api/v1/recommendations/analytics/{user_id}`: User-specific analytics
- Logs: Detailed logging of recommendation algorithms and performance

## Conclusion

The AI-powered recommendation system provides a comprehensive solution for personalized content discovery. With its hybrid approach, real-time learning, and extensive analytics, it significantly enhances user engagement while maintaining system performance and scalability.
