# AI/ML Features Documentation

## Overview

The FastAPI application now includes comprehensive AI/ML capabilities that provide intelligent content analysis, personalization, and moderation features. These features enhance user experience by offering personalized recommendations, sentiment analysis, content classification, and automated moderation.

## Features Implemented

### 1. Sentiment Analysis

- **Purpose**: Analyzes the sentiment (positive, negative, neutral) of text content
- **Models Used**: TextBlob + VADER sentiment analysis
- **Applications**:
  - Comment moderation
  - Content quality assessment
  - User engagement analysis

### 2. Content Recommendations

- **Purpose**: Provides personalized content recommendations to users
- **Algorithm**: Multi-factor recommendation system considering:
  - User content preferences
  - Content similarity
  - Category preferences
  - Engagement metrics
  - Recency scoring

### 3. Content Similarity

- **Purpose**: Finds similar content based on semantic similarity
- **Models Used**: Sentence transformers + TF-IDF vectorization
- **Applications**:
  - Related posts suggestions
  - Content discovery
  - Duplicate detection

### 4. Content Classification

- **Purpose**: Automatically categorizes and analyzes content
- **Features**:
  - Topic extraction
  - Sentiment analysis
  - Reading time estimation
  - Complexity analysis
  - Engagement prediction

### 5. Content Moderation

- **Purpose**: Automatically moderates content for appropriateness
- **Capabilities**:
  - Keyword filtering
  - Sentiment-based moderation
  - Severity assessment
  - Action recommendations

### 6. User Analytics

- **Purpose**: Analyzes user behavior and preferences
- **Metrics**:
  - Content preferences
  - Engagement patterns
  - Activity analysis
  - Behavioral insights

### 7. Background Processing

- **Purpose**: Handles ML model training and updates
- **Tasks**:
  - Content analysis scheduling
  - Model retraining
  - Analytics updates
  - User engagement analysis

## API Endpoints

### Sentiment Analysis

```
POST /api/v1/ai/sentiment/analyze
```

**Request:**

```json
{
    "text": "This is amazing content!"
}
```

**Response:**

```json
{
    "sentiment": "positive",
    "confidence": 0.85,
    "scores": {
        "textblob_polarity": 0.8,
        "vader_compound": 0.9,
        "combined_score": 0.85
    }
}
```

### Similar Content

```
POST /api/v1/ai/content/similar
```

**Request:**

```json
{
    "post_id": 1,
    "limit": 5
}
```

**Response:**

```json
{
    "similar_posts": [
        {
            "post_id": 2,
            "similarity_score": 0.85,
            "title": "Similar Post Title"
        }
    ]
}
```

### Personalized Recommendations

```
POST /api/v1/ai/recommendations/personalized
```

**Request:**

```json
{
    "user_id": 1,
    "limit": 10
}
```

**Response:**

```json
{
    "recommendations": [
        {
            "post_id": 5,
            "score": 0.9,
            "reasons": ["Matches your interest in technology", "Popular content"]
        }
    ]
}
```

### Content Classification

```
POST /api/v1/ai/content/classify
```

**Request:**

```json
{
    "title": "Introduction to AI",
    "content": "This article discusses artificial intelligence and machine learning..."
}
```

**Response:**

```json
{
    "sentiment": {
        "label": "positive",
        "confidence": 0.85
    },
    "topics": [
        {"topic": "technology", "relevance_score": 0.9},
        {"topic": "AI", "relevance_score": 0.8}
    ],
    "reading_time_minutes": 3,
    "complexity": "medium",
    "word_count": 450,
    "estimated_engagement": "high"
}
```

### User Analysis

```
POST /api/v1/ai/user/analyze
```

**Request:**

```json
{
    "user_id": 1
}
```

**Response:**

```json
{
    "total_posts": 15,
    "total_comments": 42,
    "preferred_categories": {"technology": 8, "science": 4},
    "sentiment_distribution": {"positive": 12, "neutral": 3, "negative": 0},
    "engagement_score": 0.75
}
```

### Content Moderation

```
POST /api/v1/ai/content/moderate
```

**Request:**

```json
{
    "title": "Article Title",
    "content": "Article content to moderate..."
}
```

**Response:**

```json
{
    "approved": true,
    "issues_found": [],
    "severity": "low",
    "total_issues": 0,
    "confidence": 0.95,
    "action_required": "none"
}
```

### Batch Analysis

```
POST /api/v1/ai/content/batch-analyze
```

**Request:**

```json
{
    "post_ids": [1, 2, 3],
    "include_similarity": true,
    "include_recommendations": false
}
```

**Response:**

```json
{
    "task_id": "batch_3_hash123",
    "status": "started",
    "message": "Batch analysis started. Check back later for results."
}
```

### Trending Topics

```
GET /api/v1/ai/insights/trending-topics
```

**Response:**

```json
{
    "trending_topics": [
        {"topic": "AI", "score": 0.95, "growth": "+12%"},
        {"topic": "Remote Work", "score": 0.87, "growth": "+8%"}
    ],
    "analysis_period": "last_7_days",
    "confidence": 0.85
}
```

### Content Quality Analysis

```
POST /api/v1/ai/insights/content-quality
```

**Request:**

```json
{
    "post_id": 1
}
```

**Response:**

```json
{
    "readability_score": 0.78,
    "seo_optimization": 0.65,
    "engagement_potential": 0.82,
    "overall_quality": 0.77,
    "suggestions": [
        "Consider adding more subheadings for better readability",
        "Include more data points to support your arguments"
    ]
}
```

### Auto Tagging

```
POST /api/v1/ai/insights/auto-tag
```

**Request:** Query parameters

- `title`: Content title
- `content`: Content body

**Response:**

```json
{
    "suggested_tags": ["technology", "AI", "positive"],
    "confidence": 0.75,
    "alternatives": ["trending", "featured"]
}
```

### Health Check

```
GET /api/v1/ai/health
```

**Response:**

```json
{
    "status": "healthy",
    "models_loaded": true,
    "test_sentiment": "positive",
    "timestamp": 1640995200.123
}
```

## Usage Examples

### Python Client Example

```python
import httpx

async def analyze_content():
    async with httpx.AsyncClient() as client:
        # Sentiment analysis
        response = await client.post(
            "http://localhost:8000/api/v1/ai/sentiment/analyze",
            json={"text": "This is great content!"}
        )
        sentiment_result = response.json()
        
        # Get recommendations
        recommendations = await client.post(
            "http://localhost:8000/api/v1/ai/recommendations/personalized",
            json={"user_id": 1, "limit": 5}
        )
        recs = recommendations.json()
```

### JavaScript Client Example

```javascript
// Sentiment analysis
const sentimentResponse = await fetch('/api/v1/ai/sentiment/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: 'This is amazing!' })
});
const sentiment = await sentimentResponse.json();

// Get recommendations
const recommendationsResponse = await fetch('/api/v1/ai/recommendations/personalized', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: 1, limit: 10 })
});
const recommendations = await recommendationsResponse.json();
```

## Configuration

### Environment Variables

```bash
# AI Service Configuration
AI_MODEL_CACHE_SIZE=1000
AI_BATCH_SIZE=10
AI_MAX_TEXT_LENGTH=5000
AI_SIMILARITY_THRESHOLD=0.1
AI_CONFIDENCE_THRESHOLD=0.5

# Model Paths (optional)
TRANSFORMERS_CACHE=/app/models/transformers
NLTK_DATA=/app/models/nltk
```

### Dependencies

```txt
# AI/ML Dependencies (added to requirements.txt)
transformers==4.36.0
torch==2.1.0
scikit-learn==1.3.2
numpy==1.24.3
pandas==2.1.3
sentence-transformers==2.2.2
textblob==0.17.1
nltk==3.8.1
faiss-cpu==1.7.4
joblib==1.3.2
accelerate==0.25.0
bitsandbytes==0.41.2
scipy==1.11.4
matplotlib==3.8.2
seaborn==0.13.0
```

## Background Tasks

The AI service includes several background tasks that run automatically:

1. **Content Analysis Task** (Every 5 minutes)
   - Analyzes new content for sentiment, topics, and quality
   - Updates recommendation scores
   - Processes content moderation

2. **Model Training Task** (Every hour)
   - Retrains similarity models
   - Updates content clusters
   - Refreshes recommendation algorithms

3. **Analytics Update Task** (Every 30 minutes)
   - Updates sentiment analytics
   - Calculates recommendation metrics
   - Processes moderation statistics

4. **User Engagement Analysis** (Every hour)
   - Analyzes user behavior patterns
   - Updates engagement scores
   - Refreshes user preferences

## Testing

Run the AI service tests:

```bash
# Test AI service functionality
pytest app/tests/test_ai_service.py -v

# Test AI API endpoints
pytest app/tests/test_ai_api.py -v

# Run integration tests
pytest app/tests/test_ai_service.py -m integration -v
```

## Performance Considerations

### Caching

- Embeddings are cached to avoid recomputation
- Similarity matrices are cached for faster lookups
- Model states are periodically saved to disk

### Batch Processing

- Content analysis is performed in batches to optimize performance
- Background tasks process multiple items simultaneously
- Rate limiting prevents API overload

### Model Optimization

- Lightweight transformer models are used for faster inference
- TF-IDF fallback for when transformer models fail
- Progressive model loading reduces startup time

## Error Handling

The AI service includes comprehensive error handling:

- **Fallback Models**: If transformer models fail, fallback to simpler models
- **Graceful Degradation**: Service continues to function with reduced capabilities
- **Error Logging**: All errors are logged with detailed context
- **Health Monitoring**: Regular health checks ensure service availability

## Security Considerations

### Content Moderation

- Automated keyword filtering
- Sentiment-based content flagging
- Severity assessment for manual review

### Data Privacy

- No sensitive data is stored in AI model caches
- User analytics are anonymized
- Content analysis is performed on-demand

### Rate Limiting

- API endpoints include rate limiting
- Batch operations are throttled
- Background tasks respect system resources

## Future Enhancements

Potential improvements to the AI service:

1. **Advanced Models**
   - GPT integration for content generation
   - Custom fine-tuned models for domain-specific analysis
   - Multi-language support

2. **Enhanced Analytics**
   - Real-time sentiment tracking
   - Viral content prediction
   - User behavior prediction

3. **Improved Recommendations**
   - Collaborative filtering algorithms
   - Deep learning recommendation models
   - Cross-platform recommendation

4. **Content Generation**
   - AI-powered content suggestions
   - Automated content summaries
   - Dynamic content optimization

## Troubleshooting

### Common Issues

1. **Model Loading Failures**
   - Check available memory
   - Verify model files are present
   - Review error logs for specific model issues

2. **Slow Performance**
   - Enable caching
   - Reduce batch sizes
   - Check background task status

3. **Inaccurate Recommendations**
   - Retrain models with recent data
   - Adjust similarity thresholds
   - Review user preference data

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger('app.services.ai_service').setLevel(logging.DEBUG)
```

Monitor background tasks:

```python
# Check task status via API
response = requests.get('/api/v1/ai/analytics/overview')
```

## Integration Guide

To integrate AI features into your application:

1. **Import the AI service**:

```python
from app.services.ai_service import AIService, create_ai_service
from app.api.ai import router as ai_router
```

2. **Include the AI router**:

```python
app.include_router(ai_router, prefix="/api/v1", tags=["AI Features"])
```

3. **Initialize background tasks**:

```python
from app.core.ai_background_tasks import create_ai_background_task_manager

# Initialize and start background tasks
ai_task_manager = await create_ai_background_task_manager(...)
await ai_task_manager.start_tasks()
```

4. **Use the service**:

```python
# Create service instance
ai_service = create_ai_service(user_service, post_service, comment_service)

# Analyze content
sentiment = await ai_service.analyze_sentiment("Great content!")
recommendations = await ai_service.get_personalized_recommendations(user_id=1)
```

## Support

For issues or questions about the AI features:

1. Check the test files for usage examples
2. Review the API documentation
3. Enable debug logging for troubleshooting
4. Monitor background task status
5. Check system resources and model loading

The AI service is designed to be robust and fault-tolerant, but proper monitoring and maintenance are recommended for production use.
