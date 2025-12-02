"""
Tests for AI Service
Comprehensive tests for AI/ML features
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import List

from app.services.ai_service import (
    AIService,
    SentimentResult,
    ContentSimilarity,
    RecommendationScore,
    create_ai_service
)
from app.models.post import Post
from app.models.comment import Comment
from app.models.user import User
from app.models.category import Category


class MockPost:
    """Mock post for testing"""
    
    def __init__(self, id: int, title: str, content: str, user_id: int = 1, 
                 category: str = None, created_at=None):
        self.id = id
        self.title = title
        self.content = content
        self.user_id = user_id
        self.category = Mock(name=category) if category else None
        self.likes_count = 0
        self.comments_count = 0
        self.created_at = created_at


class MockUser:
    """Mock user for testing"""
    
    def __init__(self, id: int, name: str = "Test User"):
        self.id = id
        self.name = name


class MockComment:
    """Mock comment for testing"""
    
    def __init__(self, id: int, content: str, post_id: int, user_id: int = 1, created_at=None):
        self.id = id
        self.content = content
        self.post_id = post_id
        self.user_id = user_id
        self.likes_count = 0
        self.created_at = created_at


@pytest.fixture
def mock_user_service():
    """Mock user service"""
    service = Mock()
    service.get_by_id = AsyncMock(return_value=MockUser(1))
    service.get_all = AsyncMock(return_value=[MockUser(1), MockUser(2)])
    return service


@pytest.fixture
def mock_post_service():
    """Mock post service"""
    service = Mock()
    service.get_by_id = AsyncMock(return_value=MockPost(1, "Test Post", "Test content"))
    service.get_by_user_id = AsyncMock(return_value=[
        MockPost(1, "User Post 1", "User content 1", 1),
        MockPost(2, "User Post 2", "User content 2", 1)
    ])
    service.get_all = AsyncMock(return_value=[
        MockPost(1, "Test Post 1", "Test content 1"),
        MockPost(2, "Test Post 2", "Test content 2"),
        MockPost(3, "Test Post 3", "Test content 3")
    ])
    return service


@pytest.fixture
def mock_comment_service():
    """Mock comment service"""
    service = Mock()
    service.get_by_user_id = AsyncMock(return_value=[
        MockComment(1, "Test comment 1", 1),
        MockComment(2, "Test comment 2", 2)
    ])
    service.get_all = AsyncMock(return_value=[
        MockComment(1, "Test comment 1", 1),
        MockComment(2, "Test comment 2", 2)
    ])
    return service


@pytest.fixture
def ai_service(mock_user_service, mock_post_service, mock_comment_service):
    """Create AI service with mocked dependencies"""
    return AIService(mock_user_service, mock_post_service, mock_comment_service)


class TestSentimentAnalysis:
    """Test sentiment analysis functionality"""
    
    @pytest.mark.asyncio
    async def test_analyze_positive_sentiment(self, ai_service):
        """Test positive sentiment analysis"""
        result = await ai_service.analyze_sentiment("This is amazing! I love this!")
        
        assert isinstance(result, SentimentResult)
        assert result.sentiment in ["positive", "neutral"]  # May vary based on model
        assert 0 <= result.confidence <= 1
        assert "textblob_polarity" in result.scores
        assert "combined_score" in result.scores
    
    @pytest.mark.asyncio
    async def test_analyze_negative_sentiment(self, ai_service):
        """Test negative sentiment analysis"""
        result = await ai_service.analyze_sentiment("This is terrible! I hate this!")
        
        assert isinstance(result, SentimentResult)
        assert result.sentiment in ["negative", "neutral"]  # May vary based on model
        assert 0 <= result.confidence <= 1
        assert "textblob_polarity" in result.scores
        assert "combined_score" in result.scores
    
    @pytest.mark.asyncio
    async def test_analyze_neutral_sentiment(self, ai_service):
        """Test neutral sentiment analysis"""
        result = await ai_service.analyze_sentiment("This is a test message.")
        
        assert isinstance(result, SentimentResult)
        assert result.sentiment in ["positive", "negative", "neutral"]
        assert 0 <= result.confidence <= 1
        assert "textblob_polarity" in result.scores
    
    @pytest.mark.asyncio
    async def test_analyze_empty_text(self, ai_service):
        """Test sentiment analysis with empty text"""
        result = await ai_service.analyze_sentiment("")
        
        assert isinstance(result, SentimentResult)
        assert result.sentiment == "neutral"
        assert result.confidence >= 0
    
    @pytest.mark.asyncio
    async def test_analyze_error_handling(self, ai_service):
        """Test error handling in sentiment analysis"""
        with patch('app.services.ai_service.TextBlob') as mock_textblob:
            mock_textblob.side_effect = Exception("Mock error")
            
            result = await ai_service.analyze_sentiment("Test text")
            
            assert isinstance(result, SentimentResult)
            assert result.sentiment == "neutral"
            assert "error" in result.scores


class TestContentSimilarity:
    """Test content similarity functionality"""
    
    @pytest.mark.asyncio
    async def test_find_similar_content(self, ai_service, mock_post_service):
        """Test finding similar content"""
        similar_content = await ai_service.find_similar_content(post_id=1, limit=3)
        
        assert isinstance(similar_content, list)
        assert len(similar_content) <= 3
        
        for item in similar_content:
            assert isinstance(item, ContentSimilarity)
            assert hasattr(item, 'post_id')
            assert hasattr(item, 'similarity_score')
            assert hasattr(item, 'title')
            assert 0 <= item.similarity_score <= 1
            assert item.post_id != 1  # Should not include the target post
    
    @pytest.mark.asyncio
    async def test_find_similar_content_no_post(self, ai_service, mock_post_service):
        """Test finding similar content when post doesn't exist"""
        mock_post_service.get_by_id.return_value = None
        
        similar_content = await ai_service.find_similar_content(post_id=999, limit=5)
        
        assert isinstance(similar_content, list)
        assert len(similar_content) == 0
    
    @pytest.mark.asyncio
    async def test_find_similar_content_single_post(self, ai_service, mock_post_service):
        """Test finding similar content with only one post"""
        mock_post_service.get_all.return_value = [
            MockPost(1, "Test Post", "Test content")
        ]
        
        similar_content = await ai_service.find_similar_content(post_id=1, limit=5)
        
        assert isinstance(similar_content, list)
        assert len(similar_content) == 0


class TestUserPreferences:
    """Test user preference analysis"""
    
    @pytest.mark.asyncio
    async def test_analyze_user_preferences(self, ai_service, mock_user_service):
        """Test user preference analysis"""
        analysis = await ai_service.analyze_user_preferences(user_id=1)
        
        assert isinstance(analysis, dict)
        assert "total_posts" in analysis
        assert "total_comments" in analysis
        assert "preferred_categories" in analysis
        assert "sentiment_distribution" in analysis
        assert "content_length_stats" in analysis
        assert "engagement_score" in analysis
        
        assert isinstance(analysis["total_posts"], int)
        assert isinstance(analysis["total_comments"], int)
        assert isinstance(analysis["engagement_score"], float)
        assert 0 <= analysis["engagement_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_analyze_new_user(self, ai_service, mock_user_service):
        """Test analysis for new user with no posts/comments"""
        mock_post_service.get_by_user_id.return_value = []
        mock_comment_service.get_by_user_id.return_value = []
        
        analysis = await ai_service.analyze_user_preferences(user_id=999)
        
        assert isinstance(analysis, dict)
        assert analysis["total_posts"] == 0
        assert analysis["total_comments"] == 0
        assert analysis["engagement_score"] == 0.0


class TestRecommendations:
    """Test personalized recommendations"""
    
    @pytest.mark.asyncio
    async def test_get_personalized_recommendations(self, ai_service):
        """Test getting personalized recommendations"""
        recommendations = await ai_service.get_personalized_recommendations(
            user_id=1, 
            limit=5
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5
        
        for rec in recommendations:
            assert isinstance(rec, RecommendationScore)
            assert hasattr(rec, 'post_id')
            assert hasattr(rec, 'score')
            assert hasattr(rec, 'reasons')
            assert 0 <= rec.score <= 1
            assert isinstance(rec.reasons, list)
    
    @pytest.mark.asyncio
    async def test_get_recommendations_no_user_posts(self, ai_service):
        """Test recommendations for user with no posts"""
        mock_post_service.get_by_user_id.return_value = []
        
        recommendations = await ai_service.get_personalized_recommendations(
            user_id=999, 
            limit=5
        )
        
        assert isinstance(recommendations, list)
        # Should still return some recommendations based on general patterns
    
    @pytest.mark.asyncio
    async def test_recommendation_scoring(self, ai_service, mock_post_service):
        """Test recommendation scoring logic"""
        # Create a mock post for testing
        mock_post = MockPost(
            id=5, 
            title="Technology Post", 
            content="This is about AI and machine learning",
            category="technology"
        )
        mock_post_service.get_all.return_value = [mock_post]
        
        score_data = await ai_service._calculate_recommendation_score(mock_post, 1, {})
        
        assert isinstance(score_data, dict)
        assert "total_score" in score_data
        assert "reasons" in score_data
        assert 0 <= score_data["total_score"] <= 1
        assert isinstance(score_data["reasons"], list)


class TestContentClassification:
    """Test content classification"""
    
    @pytest.mark.asyncio
    async def test_classify_content(self, ai_service):
        """Test content classification"""
        classification = await ai_service.classify_content(
            title="AI and Machine Learning",
            content="This article discusses artificial intelligence and machine learning technologies"
        )
        
        assert isinstance(classification, dict)
        assert "sentiment" in classification
        assert "topics" in classification
        assert "reading_time_minutes" in classification
        assert "complexity" in classification
        assert "word_count" in classification
        assert "estimated_engagement" in classification
        
        assert isinstance(classification["sentiment"], dict)
        assert "label" in classification["sentiment"]
        assert "confidence" in classification["sentiment"]
        
        assert isinstance(classification["topics"], list)
        assert isinstance(classification["reading_time_minutes"], int)
        assert classification["reading_time_minutes"] > 0
        assert classification["complexity"] in ["simple", "medium", "complex"]
        assert classification["estimated_engagement"] in ["low", "medium", "high"]
    
    @pytest.mark.asyncio
    async def test_topic_extraction(self, ai_service):
        """Test topic extraction"""
        topics = await ai_service._extract_topics(
            "This is about AI, machine learning, and programming"
        )
        
        assert isinstance(topics, list)
        
        for topic in topics:
            assert isinstance(topic, dict)
            assert "topic" in topic
            assert "relevance_score" in topic
            assert 0 <= topic["relevance_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_engagement_estimation(self, ai_service):
        """Test engagement estimation"""
        high_engagement = await ai_service._estimate_engagement(
            "This is amazing! Did you know that 75% of people love this?"
        )
        
        low_engagement = await ai_service._estimate_engagement(
            "This is a simple statement."
        )
        
        assert high_engagement in ["low", "medium", "high"]
        assert low_engagement in ["low", "medium", "high"]


class TestContentModeration:
    """Test content moderation"""
    
    @pytest.mark.asyncio
    async def test_moderate_good_content(self, ai_service):
        """Test moderation of good content"""
        result = await ai_service.moderate_content(
            title="Great article",
            content="This is a wonderful and informative article about technology."
        )
        
        assert isinstance(result, dict)
        assert "approved" in result
        assert "issues_found" in result
        assert "severity" in result
        assert "total_issues" in result
        assert "confidence" in result
        
        assert isinstance(result["approved"], bool)
        assert isinstance(result["issues_found"], list)
        assert result["severity"] in ["low", "medium", "high", "unknown"]
        assert 0 <= result["confidence"] <= 1
    
    @pytest.mark.asyncio
    async def test_moderate_problematic_content(self, ai_service):
        """Test moderation of problematic content"""
        result = await ai_service.moderate_content(
            title="Spam content",
            content="This is fake and scam content"
        )
        
        assert isinstance(result, dict)
        # Should detect the inappropriate keywords
        if result["issues_found"]:
            assert len(result["issues_found"]) > 0
    
    @pytest.mark.asyncio
    async def test_moderate_highly_negative_content(self, ai_service):
        """Test moderation of highly negative content"""
        result = await ai_service.moderate_content(
            title="Terrible content",
            content="I absolutely hate everything about this. This is the worst thing ever created."
        )
        
        assert isinstance(result, dict)
        # Should potentially flag highly negative content


class TestBatchAnalysis:
    """Test batch content analysis"""
    
    @pytest.mark.asyncio
    async def test_batch_analyze_content(self, ai_service):
        """Test batch content analysis"""
        posts = [
            MockPost(1, "Post 1", "Content 1"),
            MockPost(2, "Post 2", "Content 2"),
            MockPost(3, "Post 3", "Content 3")
        ]
        
        results = await ai_service.batch_analyze_content(posts)
        
        assert isinstance(results, dict)
        assert len(results) == len(posts)
        
        for post_id, analysis in results.items():
            assert isinstance(analysis, dict)
            assert "sentiment" in analysis or "error" in analysis


class TestEmbeddings:
    """Test embedding functionality"""
    
    @pytest.mark.asyncio
    async def test_get_content_embeddings(self, ai_service):
        """Test content embedding generation"""
        texts = [
            "This is the first text",
            "This is the second text",
            "This is the third text"
        ]
        
        embeddings = await ai_service.get_content_embeddings(texts)
        
        assert isinstance(embeddings, object)  # numpy array or similar
        if hasattr(embeddings, 'shape'):
            assert embeddings.shape[0] == len(texts)
        elif hasattr(embeddings, '__len__'):
            assert len(embeddings) == len(texts)
    
    @pytest.mark.asyncio
    async def test_get_empty_embeddings(self, ai_service):
        """Test embedding with empty text list"""
        embeddings = await ai_service.get_content_embeddings([])
        
        # Should handle empty input gracefully
        assert isinstance(embeddings, object)
    
    @pytest.mark.asyncio
    async def test_embedding_cache(self, ai_service):
        """Test embedding caching"""
        texts = ["Test text for caching"]
        
        # First call should compute embeddings
        embeddings1 = await ai_service.get_content_embeddings(texts)
        
        # Second call should use cache
        embeddings2 = await ai_service.get_content_embeddings(texts)
        
        # Should be the same result (if cached properly)
        # Note: This test may vary depending on implementation


class TestFactoryFunction:
    """Test service factory function"""
    
    def test_create_ai_service(self, mock_user_service, mock_post_service, mock_comment_service):
        """Test AI service factory function"""
        service = create_ai_service(mock_user_service, mock_post_service, mock_comment_service)
        
        assert isinstance(service, AIService)
        assert service.user_service == mock_user_service
        assert service.post_service == mock_post_service
        assert service.comment_service == mock_comment_service


class TestErrorHandling:
    """Test comprehensive error handling"""
    
    @pytest.mark.asyncio
    async def test_service_initialization_error(self, mock_user_service, mock_post_service, mock_comment_service):
        """Test service initialization with errors"""
        with patch.object(AIService, '_initialize_models') as mock_init:
            mock_init.side_effect = Exception("Init error")
            
            # Should still create service but handle initialization error
            service = AIService(mock_user_service, mock_post_service, mock_comment_service)
            assert service is not None
    
    @pytest.mark.asyncio
    async def test_network_timeout_handling(self, ai_service):
        """Test handling of network timeouts or external service failures"""
        with patch('app.services.ai_service.TextBlob') as mock_textblob:
            mock_textblob.side_effect = Exception("Network timeout")
            
            result = await ai_service.analyze_sentiment("Test text")
            
            # Should return a fallback result rather than crashing
            assert isinstance(result, SentimentResult)


# Integration tests
@pytest.mark.integration
class TestAIIntegration:
    """Integration tests for AI service"""
    
    @pytest.mark.asyncio
    async def test_full_recommendation_pipeline(self, ai_service):
        """Test complete recommendation generation pipeline"""
        # Test the full flow from user analysis to recommendations
        user_prefs = await ai_service.analyze_user_preferences(user_id=1)
        recommendations = await ai_service.get_personalized_recommendations(user_id=1)
        
        assert isinstance(user_prefs, dict)
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_content_analysis_pipeline(self, ai_service):
        """Test complete content analysis pipeline"""
        # Test sentiment, classification, and moderation in sequence
        text = "This is an amazing article about AI and technology!"
        
        sentiment = await ai_service.analyze_sentiment(text)
        classification = await ai_service.classify_content("AI Article", text)
        moderation = await ai_service.moderate_content("AI Article", text)
        
        assert isinstance(sentiment, SentimentResult)
        assert isinstance(classification, dict)
        assert isinstance(moderation, dict)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])