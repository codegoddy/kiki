# AI Configuration Example

This document provides practical examples for configuring and using the AI/ML features in your FastAPI application.

## Environment Configuration

### .env File Example

```bash
# AI/ML Service Configuration
AI_SERVICE_ENABLED=true
AI_MODEL_CACHE_SIZE=1000
AI_BATCH_SIZE=10
AI_MAX_TEXT_LENGTH=5000
AI_SIMILARITY_THRESHOLD=0.1
AI_CONFIDENCE_THRESHOLD=0.5
AI_SENTIMENT_MODEL=textblob+vader
AI_EMBEDDING_MODEL=all-MiniLM-L6-v2

# Background Tasks Configuration
AI_BACKGROUND_TASKS_ENABLED=true
AI_CONTENT_ANALYSIS_INTERVAL=300
AI_MODEL_TRAINING_INTERVAL=3600
AI_ANALYTICS_UPDATE_INTERVAL=1800
AI_USER_ENGAGEMENT_INTERVAL=3600

# Performance Configuration
AI_WORKER_PROCESSES=4
AI_MEMORY_LIMIT=2GB
AI_CACHE_TTL=3600
AI_RATE_LIMIT_REQUESTS=100
AI_RATE_LIMIT_WINDOW=60

# Model Storage Paths
AI_MODELS_PATH=/app/models
AI_CACHE_PATH=/app/cache
AI_TRANSFORMERS_CACHE=/app/models/transformers
AI_NLTK_DATA=/app/models/nltk

# Development/Production Flags
AI_DEBUG_MODE=false
AI_VERBOSE_LOGGING=false
AI_TEST_MODE=false
```

### Docker Environment Example

```yaml
# docker-compose.yml environment section
environment:
  - AI_SERVICE_ENABLED=true
  - AI_MODEL_CACHE_SIZE=2000
  - AI_BATCH_SIZE=20
  - AI_MAX_TEXT_LENGTH=10000
  - AI_SIMILARITY_THRESHOLD=0.05
  - AI_CONFIDENCE_THRESHOLD=0.3
  - AI_BACKGROUND_TASKS_ENABLED=true
  - AI_WORKER_PROCESSES=8
  - AI_MODELS_PATH=/data/models
  - AI_CACHE_PATH=/data/cache
```

## Application Integration

### main.py Integration Example

```python
"""
Enhanced main.py with AI service integration
"""

from fastapi import FastAPI
from app.api import auth, users, posts, comments, admin, categories, social, ai
from app.core.ai_background_tasks import create_ai_background_task_manager
from app.services.ai_service import AIService, create_ai_service

# ... existing imports and setup ...

# Include AI router
app.include_router(
    ai.router, 
    prefix=f"{settings.api.API_V1_STR}", 
    tags=["AI Features"]
)

# Startup event with AI service initialization
@app.on_event("startup")
async def startup_event():
    """Enhanced startup with AI service"""
    
    # Initialize AI services if enabled
    if settings.ai.ENABLED:
        try:
            # Create services
            ai_service = create_ai_service(
                user_service=user_service,
                post_service=post_service,
                comment_service=comment_service
            )
            
            # Initialize background tasks
            ai_task_manager = await create_ai_background_task_manager(
                ai_service=ai_service,
                user_service=user_service,
                post_service=post_service,
                comment_service=comment_service
            )
            
            # Start background tasks
            await ai_task_manager.start_tasks()
            
            logger.info("AI services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI services: {e}")
```

### Service Factory Example

```python
"""
Enhanced service factory with AI service integration
"""

from app.services.user import UserService
from app.services.post import PostService
from app.services.comment import CommentService
from app.services.ai_service import AIService, create_ai_service

class ServiceFactory:
    """Enhanced service factory with AI integration"""
    
    def __init__(self):
        self.user_service = UserService()
        self.post_service = PostService()
        self.comment_service = CommentService()
        self.ai_service = None
    
    async def initialize_ai_service(self):
        """Initialize AI service with dependencies"""
        self.ai_service = create_ai_service(
            user_service=self.user_service,
            post_service=self.post_service,
            comment_service=self.comment_service
        )
        return self.ai_service
    
    def get_all_services(self):
        """Get all services including AI"""
        services = {
            "user_service": self.user_service,
            "post_service": self.post_service,
            "comment_service": self.comment_service,
            "ai_service": self.ai_service
        }
        return services

# Usage
service_factory = ServiceFactory()
ai_service = await service_factory.initialize_ai_service()
```

## Configuration Files

### AI Configuration Schema

```python
"""
Enhanced configuration with AI settings
"""

from pydantic import BaseSettings, Field
from typing import List, Optional

class AIConfig(BaseSettings):
    """AI service configuration"""
    
    # Service Enable/Disable
    enabled: bool = Field(default=True, description="Enable AI service")
    
    # Model Configuration
    model_cache_size: int = Field(default=1000, ge=100, le=10000)
    batch_size: int = Field(default=10, ge=1, le=100)
    max_text_length: int = Field(default=5000, ge=100, le=50000)
    
    # Thresholds
    similarity_threshold: float = Field(default=0.1, ge=0.0, le=1.0)
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Models
    sentiment_model: str = Field(default="textblob+vader")
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    
    # Background Tasks
    background_tasks_enabled: bool = Field(default=True)
    content_analysis_interval: int = Field(default=300, ge=60)  # seconds
    model_training_interval: int = Field(default=3600, ge=300)  # seconds
    analytics_update_interval: int = Field(default=1800, ge=300)  # seconds
    user_engagement_interval: int = Field(default=3600, ge=300)  # seconds
    
    # Performance
    worker_processes: int = Field(default=4, ge=1, le=16)
    memory_limit: str = Field(default="2GB")
    cache_ttl: int = Field(default=3600, ge=300)  # seconds
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, ge=10, le=1000)
    rate_limit_window: int = Field(default=60, ge=30, le=3600)  # seconds
    
    # File Paths
    models_path: str = Field(default="/app/models")
    cache_path: str = Field(default="/app/cache")
    transformers_cache: Optional[str] = Field(default=None)
    nltk_data: Optional[str] = Field(default=None)
    
    # Development Settings
    debug_mode: bool = Field(default=False)
    verbose_logging: bool = Field(default=False)
    test_mode: bool = Field(default=False)
    
    class Config:
        env_prefix = "AI_"
        case_sensitive = False

# Usage in main config
class Settings(BaseSettings):
    ai: AIConfig = AIConfig()
    # ... other settings
```

### Environment-Specific Configurations

#### Development Configuration

```python
# config/development.py
from .base import BaseConfig

class DevelopmentConfig(BaseConfig):
    """Development environment AI configuration"""
    
    AI_ENABLED = True
    AI_DEBUG_MODE = True
    AI_VERBOSE_LOGGING = True
    AI_TEST_MODE = True
    
    AI_MODEL_CACHE_SIZE = 100
    AI_BATCH_SIZE = 5
    AI_WORKER_PROCESSES = 2
    
    AI_CONTENT_ANALYSIS_INTERVAL = 60  # Run more frequently in dev
    AI_MODEL_TRAINING_INTERVAL = 300   # Train more frequently
    
    AI_CONFIDENCE_THRESHOLD = 0.3  # Lower threshold for development
    AI_SIMILARITY_THRESHOLD = 0.05  # More permissive in dev
```

#### Production Configuration

```python
# config/production.py
from .base import BaseConfig

class ProductionConfig(BaseConfig):
    """Production environment AI configuration"""
    
    AI_ENABLED = True
    AI_DEBUG_MODE = False
    AI_VERBOSE_LOGGING = False
    AI_TEST_MODE = False
    
    AI_MODEL_CACHE_SIZE = 5000
    AI_BATCH_SIZE = 50
    AI_WORKER_PROCESSES = 8
    
    AI_CONTENT_ANALYSIS_INTERVAL = 300  # Less frequent in production
    AI_MODEL_TRAINING_INTERVAL = 7200   # Train less frequently
    
    AI_CONFIDENCE_THRESHOLD = 0.7  # Higher threshold for production
    AI_SIMILARITY_THRESHOLD = 0.2  # More restrictive in production
    
    AI_RATE_LIMIT_REQUESTS = 500
    AI_RATE_LIMIT_WINDOW = 60
```

## Testing Configuration

### Test Configuration

```python
# tests/conftest.py - AI service testing setup
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from app.services.ai_service import AIService
from app.core.ai_background_tasks import AIBackgroundTaskManager

@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing"""
    service = Mock(spec=AIService)
    service.analyze_sentiment = AsyncMock()
    service.find_similar_content = AsyncMock()
    service.get_personalized_recommendations = AsyncMock()
    service.classify_content = AsyncMock()
    service.moderate_content = AsyncMock()
    return service

@pytest.fixture
async def ai_service_with_mocks(mock_user_service, mock_post_service, mock_comment_service):
    """Create AI service with mocked dependencies"""
    service = AIService(mock_user_service, mock_post_service, mock_comment_service)
    
    # Mock the model initialization
    service._initialize_models = Mock()
    service.tfidf_vectorizer = Mock()
    service.tokenizer = Mock()
    service.model = Mock()
    
    return service

@pytest.fixture
def test_config():
    """Test configuration"""
    return {
        "AI_ENABLED": True,
        "AI_TEST_MODE": True,
        "AI_DEBUG_MODE": True,
        "AI_MODEL_CACHE_SIZE": 10,
        "AI_BATCH_SIZE": 2,
        "AI_WORKER_PROCESSES": 1
    }
```

### Integration Test Configuration

```python
# tests/test_ai_integration.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client_with_ai():
    """Test client with AI features enabled"""
    # Configure app for testing
    app.dependency_overrides = {}
    
    # Mock AI service dependencies for integration tests
    from app.api.ai import get_ai_service
    from unittest.mock import AsyncMock
    
    def mock_ai_service():
        service = Mock()
        service.analyze_sentiment = AsyncMock(return_value=type('Result', (), {
            'sentiment': 'positive',
            'confidence': 0.8,
            'scores': {}
        })())
        return service
    
    app.dependency_overrides[get_ai_service] = mock_ai_service
    
    return TestClient(app)
```

## Docker Configuration

### Dockerfile AI Configuration

```dockerfile
# Dockerfile - AI service setup
FROM python:3.11-slim

# Install AI/ML dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data and models
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

# Set up model cache directory
RUN mkdir -p /app/models /app/cache
ENV AI_MODELS_PATH=/app/models
ENV AI_CACHE_PATH=/app/cache

# Set environment variables
ENV AI_SERVICE_ENABLED=true
ENV AI_WORKER_PROCESSES=4
ENV AI_MODEL_CACHE_SIZE=2000

# Expose port
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose AI Configuration

```yaml
# docker-compose.yml - AI service configuration
version: '3.8'

services:
  app:
    build: .
    environment:
      - AI_SERVICE_ENABLED=true
      - AI_MODEL_CACHE_SIZE=2000
      - AI_BATCH_SIZE=20
      - AI_WORKER_PROCESSES=4
      - AI_MODELS_PATH=/data/models
      - AI_CACHE_PATH=/data/cache
    volumes:
      - ./models:/data/models
      - ./cache:/data/cache
    depends_on:
      - redis
      - postgres
  
  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=appdb
      - POSTGRES_USER=appuser
      - POSTGRES_PASSWORD=apppass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  redis_data:
  postgres_data:
  models:
  cache:
```

## Monitoring and Logging

### AI Service Monitoring

```python
"""
AI service monitoring configuration
"""

import logging
from prometheus_client import Counter, Histogram, Gauge

# AI Service Metrics
ai_requests_total = Counter('ai_requests_total', 'Total AI requests', ['endpoint', 'status'])
ai_request_duration = Histogram('ai_request_duration_seconds', 'AI request duration')
ai_active_models = Gauge('ai_active_models', 'Number of active AI models')
ai_cache_hits = Counter('ai_cache_hits_total', 'Cache hits')
ai_cache_misses = Counter('ai_cache_misses_total', 'Cache misses')

# Logging configuration for AI service
ai_logger = logging.getLogger('app.services.ai_service')
ai_logger.setLevel(logging.INFO)

# File handler for AI logs
ai_handler = logging.FileHandler('/var/log/ai_service.log')
ai_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
ai_handler.setFormatter(ai_formatter)
ai_logger.addHandler(ai_handler)

# Health check endpoint
@app.get("/ai/health/detailed")
async def detailed_ai_health():
    """Detailed AI service health check"""
    import psutil
    import time
    
    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        },
        "ai_service": {
            "models_loaded": ai_active_models._value._value if hasattr(ai_active_models, '_value') else 0,
            "cache_size": len(ai_service.embeddings_cache) if hasattr(ai_service, 'embeddings_cache') else 0,
            "background_tasks_running": True  # Would check actual status
        }
    }
    
    return health_data
```

## Usage Examples

### Basic AI Service Usage

```python
"""
Basic usage example for AI features
"""

from app.services.ai_service import create_ai_service
from app.services.user import UserService
from app.services.post import PostService
from app.services.comment import CommentService

async def basic_ai_example():
    """Basic AI service usage example"""
    
    # Initialize services
    user_service = UserService()
    post_service = PostService()
    comment_service = CommentService()
    
    # Create AI service
    ai_service = create_ai_service(user_service, post_service, comment_service)
    
    # Analyze sentiment
    sentiment = await ai_service.analyze_sentiment("This is amazing content!")
    print(f"Sentiment: {sentiment.sentiment}, Confidence: {sentiment.confidence}")
    
    # Get recommendations
    recommendations = await ai_service.get_personalized_recommendations(user_id=1, limit=5)
    for rec in recommendations:
        print(f"Recommended post {rec.post_id} with score {rec.score}")
    
    # Classify content
    classification = await ai_service.classify_content(
        title="AI Article",
        content="This article discusses artificial intelligence and machine learning."
    )
    print(f"Topics: {classification['topics']}")
    
    # Moderate content
    moderation = await ai_service.moderate_content(
        title="Test Article",
        content="This is test content."
    )
    print(f"Approved: {moderation['approved']}")

# Run the example
import asyncio
asyncio.run(basic_ai_example())
```

### Batch Processing Example

```python
"""
Batch processing example
"""

async def batch_processing_example():
    """Example of batch processing content"""
    
    # Create AI service
    ai_service = create_ai_service(user_service, post_service, comment_service)
    
    # Get all posts for batch processing
    all_posts = await post_service.get_all()
    
    # Batch analyze content
    results = await ai_service.batch_analyze_content(all_posts)
    
    # Process results
    for post_id, analysis in results.items():
        if "error" not in analysis:
            print(f"Post {post_id}: {analysis['sentiment']['label']}")
        else:
            print(f"Post {post_id}: Analysis failed - {analysis['error']}")

# Run batch processing
asyncio.run(batch_processing_example())
```

This configuration guide provides comprehensive examples for setting up and using the AI/ML features in your FastAPI application. Adjust the configurations based on your specific requirements and deployment environment.
