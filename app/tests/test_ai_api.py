"""
Tests for AI API Endpoints
Tests for AI-powered REST API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import json

from app.main import app
from app.api.ai import router as ai_router
from app.services.ai_service import AIService, SentimentResult, ContentSimilarity, RecommendationScore


class TestAIAPI:
    """Test AI API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_ai_service(self):
        """Mock AI service"""
        service = Mock(spec=AIService)
        service.analyze_sentiment = AsyncMock()
        service.find_similar_content = AsyncMock()
        service.get_personalized_recommendations = AsyncMock()
        service.classify_content = AsyncMock()
        service.analyze_user_preferences = AsyncMock()
        service.moderate_content = AsyncMock()
        service.batch_analyze_content = AsyncMock()
        return service
    
    def test_sentiment_analysis_endpoint(self, client, mock_ai_service):
        """Test sentiment analysis endpoint"""
        # Mock the sentiment analysis result
        mock_result = SentimentResult(
            sentiment="positive",
            confidence=0.8,
            scores={"textblob_polarity": 0.7, "vader_compound": 0.9}
        )
        mock_ai_service.analyze_sentiment.return_value = mock_result
        
        with patch('app.api.ai.get_ai_service', return_value=mock_ai_service):
            response = client.post("/api/v1/ai/sentiment/analyze", json={
                "text": "This is a great article!"
            })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "sentiment" in data
        assert "confidence" in data
        assert "scores" in data
        assert data["sentiment"] == "positive"
        assert 0 <= data["confidence"] <= 1
    
    def test_sentiment_analysis_invalid_input(self, client):
        """Test sentiment analysis with invalid input"""
        response = client.post("/api/v1/ai/sentiment/analyze", json={
            "invalid_field": "value"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_similar_content_endpoint(self, client, mock_ai_service):
        """Test similar content endpoint"""
        # Mock similar content results
        mock_similar = [
            ContentSimilarity(post_id=2, similarity_score=0.85, title="Similar Post"),
            ContentSimilarity(post_id=3, similarity_score=0.72, title="Another Similar Post")
        ]
        mock_ai_service.find_similar_content.return_value = mock_similar
        
        with patch('app.api.ai.get_ai_service', return_value=mock_ai_service):
            response = client.post("/api/v1/ai/content/similar", json={
                "post_id": 1,
                "limit": 5
            })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "similar_posts" in data
        assert len(data["similar_posts"]) == 2
        
        for post in data["similar_posts"]:
            assert "post_id" in post
            assert "similarity_score" in post
            assert "title" in post
            assert 0 <= post["similarity_score"] <= 1
    
    def test_personalized_recommendations_endpoint(self, client, mock_ai_service):
        """Test personalized recommendations endpoint"""
        # Mock recommendation results
        mock_recommendations = [
            RecommendationScore(
                post_id=5, 
                score=0.9, 
                reasons=["Matches your interest in technology", "Popular content"]
            ),
            RecommendationScore(
                post_id=7, 
                score=0.75, 
                reasons=["Similar to your previous content"]
            )
        ]
        mock_ai_service.get_personalized_recommendations.return_value = mock_recommendations
        
        with patch('app.api.ai.get_ai_service', return_value=mock_ai_service):
            response = client.post("/api/v1/ai/recommendations/personalized", json={
                "user_id": 1,
                "limit": 10
            })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "recommendations" in data
        assert len(data["recommendations"]) == 2
        
        for rec in data["recommendations"]:
            assert "post_id" in rec
            assert "score" in rec
            assert "reasons" in rec
            assert 0 <= rec["score"] <= 1
            assert isinstance(rec["reasons"], list)
    
    def test_content_classification_endpoint(self, client, mock_ai_service):
        """Test content classification endpoint"""
        # Mock classification result
        mock_classification = {
            "sentiment": {
                "label": "positive",
                "confidence": 0.85,
                "scores": {"textblob_polarity": 0.8}
            },
            "topics": [
                {"topic": "technology", "relevance_score": 0.9},
                {"topic": "AI", "relevance_score": 0.8}
            ],
            "reading_time_minutes": 3,
            "complexity": "medium",
            "word_count": 450,
            "character_count": 2400,
            "estimated_engagement": "high"
        }
        mock_ai_service.classify_content.return_value = mock_classification
        
        with patch('app.api.ai.get_ai_service', return_value=mock_ai_service):
            response = client.post("/api/v1/ai/content/classify", json={
                "title": "Introduction to AI",
                "content": "This article discusses artificial intelligence and machine learning..."
            })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "sentiment" in data
        assert "topics" in data
        assert "reading_time_minutes" in data
        assert "complexity" in data
        assert "word_count" in data
        assert "estimated_engagement" in data
        
        assert isinstance(data["topics"], list)
        assert data["reading_time_minutes"] > 0
        assert data["complexity"] in ["simple", "medium", "complex"]
    
    def test_user_analysis_endpoint(self, client, mock_ai_service):
        """Test user analysis endpoint"""
        # Mock user analysis result
        mock_analysis = {
            "total_posts": 15,
            "total_comments": 42,
            "preferred_categories": {"technology": 8, "science": 4, "business": 3},
            "sentiment_distribution": {"positive": 12, "neutral": 3, "negative": 0},
            "content_length_stats": {"avg": 850.5, "min": 200, "max": 2000},
            "engagement_score": 0.75
        }
        mock_ai_service.analyze_user_preferences.return_value = mock_analysis
        
        with patch('app.api.ai.get_ai_service', return_value=mock_ai_service):
            response = client.post("/api/v1/ai/user/analyze", json={
                "user_id": 1
            })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_posts" in data
        assert "total_comments" in data
        assert "preferred_categories" in data
        assert "sentiment_distribution" in data
        assert "engagement_score" in data
        
        assert isinstance(data["preferred_categories"], dict)
        assert 0 <= data["engagement_score"] <= 1
    
    def test_content_moderation_endpoint(self, client, mock_ai_service):
        """Test content moderation endpoint"""
        # Mock moderation result
        mock_moderation = {
            "approved": True,
            "issues_found": [],
            "severity": "low",
            "total_issues": 0,
            "confidence": 0.95,
            "action_required": "none"
        }
        mock_ai_service.moderate_content.return_value = mock_moderation
        
        with patch('app.api.ai.get_ai_service', return_value=mock_ai_service):
            response = client.post("/api/v1/ai/content/moderate", json={
                "title": "Great Article",
                "content": "This is a wonderful and informative article."
            })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "approved" in data
        assert "issues_found" in data
        assert "severity" in data
        assert "action_required" in data
        
        assert isinstance(data["approved"], bool)
        assert isinstance(data["issues_found"], list)
    
    def test_batch_analysis_endpoint(self, client, mock_ai_service):
        """Test batch analysis endpoint"""
        with patch('app.api.ai.get_ai_service', return_value=mock_ai_service):
            response = client.post("/api/v1/ai/content/batch-analyze", json={
                "post_ids": [1, 2, 3],
                "include_similarity": True,
                "include_recommendations": False
            })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "task_id" in data
        assert "status" in data
        assert "message" in data
        assert data["status"] == "started"
        assert isinstance(data["task_id"], str)
    
    def test_analytics_overview_endpoint(self, client, mock_ai_service):
        """Test analytics overview endpoint"""
        with patch('app.api.ai.get_ai_service', return_value=mock_ai_service):
            response = client.get("/api/v1/ai/analytics/overview")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_content_analyzed" in data
        assert "sentiment_distribution" in data
        assert "moderation_stats" in data
        assert "recommendation_stats" in data
        
        assert isinstance(data["sentiment_distribution"], dict)
        assert isinstance(data["moderation_stats"], dict)
    
    def test_ai_health_check_endpoint(self, client, mock_ai_service):
        """Test AI service health check endpoint"""
        # Mock health check result
        mock_result = SentimentResult(
            sentiment="positive",
            confidence=0.5,
            scores={}
        )
        mock_ai_service.analyze_sentiment.return_value = mock_result
        
        with patch('app.api.ai.get_ai_service', return_value=mock_ai_service):
            response = client.get("/api/v1/ai/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "models_loaded" in data
        assert "timestamp" in data
        
        assert data["status"] in ["healthy", "unhealthy"]
        assert isinstance(data["models_loaded"], bool)
    
    def test_trending_topics_endpoint(self, client, mock_ai_service):
        """Test trending topics endpoint"""
        with patch('app.api.ai.get_ai_service', return_value=mock_ai_service):
            response = client.get("/api/v1/ai/insights/trending-topics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "trending_topics" in data
        assert "analysis_period" in data
        assert "confidence" in data
        
        topics = data["trending_topics"]
        assert isinstance(topics, list)
        
        for topic in topics:
            assert "topic" in topic
            assert "score" in topic
            assert "growth" in topic
            assert 0 <= topic["score"] <= 1
    
    def test_content_quality_endpoint(self, client, mock_ai_service):
        """Test content quality analysis endpoint"""
        with patch('app.api.ai.get_ai_service', return_value=mock_ai_service):
            response = client.post("/api/v1/ai/insights/content-quality", json={
                "post_id": 1
            })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "readability_score" in data
        assert "seo_optimization" in data
        assert "engagement_potential" in data
        assert "overall_quality" in data
        assert "suggestions" in data
        
        assert isinstance(data["suggestions"], list)
        assert 0 <= data["overall_quality"] <= 1
    
    def test_audience_sentiment_endpoint(self, client, mock_ai_service):
        """Test audience sentiment analysis endpoint"""
        with patch('app.api.ai.get_ai_service', return_value=mock_ai_service):
            response = client.get("/api/v1/ai/insights/audience-sentiment", params={
                "post_id": 1
            })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "overall_sentiment" in data
        assert "confidence" in data
        assert "sentiment_breakdown" in data
        assert "emotional_indicators" in data
        assert "engagement_metrics" in data
        
        assert data["overall_sentiment"] in ["positive", "negative", "neutral"]
        assert 0 <= data["confidence"] <= 1
    
    def test_auto_tag_endpoint(self, client, mock_ai_service):
        """Test auto-tagging endpoint"""
        # Mock classification for auto-tagging
        mock_classification = {
            "topics": [
                {"topic": "technology", "relevance_score": 0.9},
                {"topic": "AI", "relevance_score": 0.8}
            ],
            "sentiment": {"label": "positive"},
            "reading_time_minutes": 3
        }
        mock_ai_service.classify_content.return_value = mock_classification
        
        with patch('app.api.ai.get_ai_service', return_value=mock_ai_service):
            response = client.post("/api/v1/ai/insights/auto-tag", params={
                "title": "Introduction to AI",
                "content": "This article discusses artificial intelligence..."
            })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "suggested_tags" in data
        assert "confidence" in data
        assert "alternatives" in data
        
        assert isinstance(data["suggested_tags"], list)
        assert isinstance(data["alternatives"], list)
        assert 0 <= data["confidence"] <= 1


class TestAPIErrorHandling:
    """Test API error handling"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_ai_service_not_available(self, client):
        """Test handling when AI service is not available"""
        with patch('app.api.ai.get_ai_service') as mock_get_service:
            mock_get_service.side_effect = Exception("Service not available")
            
            response = client.post("/api/v1/ai/sentiment/analyze", json={
                "text": "Test text"
            })
            
            assert response.status_code == 500
    
    def test_invalid_request_format(self, client):
        """Test handling of invalid request formats"""
        response = client.post("/api/v1/ai/sentiment/analyze", json={
            # Missing required 'text' field
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_large_request_limit(self, client):
        """Test handling of requests exceeding limits"""
        with TestClient(app) as client:
            # Test with excessive limit
            response = client.post("/api/v1/ai/recommendations/personalized", json={
                "user_id": 1,
                "limit": 1000  # Exceeds max limit
            })
            
            # Should either validate the limit or handle gracefully
            assert response.status_code in [422, 500]
    
    def test_missing_parameters(self, client):
        """Test handling of missing required parameters"""
        response = client.post("/api/v1/ai/similar-content", json={
            # Missing post_id
        })
        
        assert response.status_code == 422  # Validation error


class TestAPIIntegration:
    """Integration tests for AI API"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_workflow_integration(self, client):
        """Test complete AI workflow through API"""
        # This would test a realistic workflow:
        # 1. Create content
        # 2. Analyze sentiment
        # 3. Classify content
        # 4. Get recommendations
        # 5. Moderate content
        
        with patch('app.api.ai.get_ai_service') as mock_get_service:
            # Mock all service methods
            mock_service = Mock()
            mock_service.analyze_sentiment.return_value = SentimentResult("positive", 0.8, {})
            mock_service.classify_content.return_value = {"topics": []}
            mock_service.get_personalized_recommendations.return_value = []
            mock_service.moderate_content.return_value = {"approved": True}
            mock_get_service.return_value = mock_service
            
            # Test sentiment analysis
            sentiment_response = client.post("/api/v1/ai/sentiment/analyze", json={
                "text": "This is great content!"
            })
            assert sentiment_response.status_code == 200
            
            # Test content classification
            classification_response = client.post("/api/v1/ai/content/classify", json={
                "title": "Great Content",
                "content": "This is amazing content about technology."
            })
            assert classification_response.status_code == 200
            
            # Test moderation
            moderation_response = client.post("/api/v1/ai/content/moderate", json={
                "title": "Great Content",
                "content": "This is amazing content about technology."
            })
            assert moderation_response.status_code == 200
    
    def test_batch_processing_integration(self, client):
        """Test batch processing workflow"""
        with patch('app.api.ai.get_ai_service') as mock_get_service:
            mock_service = Mock()
            mock_service.batch_analyze_content.return_value = {
                1: {"sentiment": "positive"},
                2: {"sentiment": "neutral"},
                3: {"sentiment": "negative"}
            }
            mock_get_service.return_value = mock_service
            
            response = client.post("/api/v1/ai/content/batch-analyze", json={
                "post_ids": [1, 2, 3],
                "include_similarity": True,
                "include_recommendations": False
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert data["status"] == "started"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])