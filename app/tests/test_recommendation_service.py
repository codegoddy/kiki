"""
Tests for Enhanced Recommendation Service
Comprehensive tests for AI-powered recommendation algorithms
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import numpy as np

from app.services.recommendation_service import EnhancedRecommendationService
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.recommendation import (
    UserInteraction, UserPreference, ContentEmbedding, 
    RecommendationFeedback, SimilarityScore, TrendingContent
)
from app.services.ai_service import AIService


class TestEnhancedRecommendationService:
    """Test suite for Enhanced Recommendation Service"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock()
    
    @pytest.fixture
    def mock_user_service(self):
        """Mock user service"""
        return Mock()
    
    @pytest.fixture
    def mock_post_service(self):
        """Mock post service"""
        return Mock()
    
    @pytest.fixture
    def mock_comment_service(self):
        """Mock comment service"""
        return Mock()
    
    @pytest.fixture
    def mock_ai_service(self):
        """Mock AI service"""
        return Mock()
    
    @pytest.fixture
    def recommendation_service(self, mock_db, mock_user_service, mock_post_service, 
                              mock_comment_service, mock_ai_service):
        """Create recommendation service with mocked dependencies"""
        return EnhancedRecommendationService(
            db=mock_db,
            user_service=mock_user_service,
            post_service=mock_post_service,
            comment_service=mock_comment_service,
            ai_service=mock_ai_service
        )
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user"""
        user = Mock()
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        return user
    
    @pytest.fixture
    def sample_post(self, sample_user):
        """Create sample post"""
        post = Mock()
        post.id = 1
        post.title = "Test Post"
        post.content = "This is a test post content"
        post.author = sample_user
        post.author_id = sample_user.id
        post.categories = []
        post.created_at = datetime.utcnow()
        return post
    
    @pytest.fixture
    def sample_interactions(self, sample_user, sample_post):
        """Create sample user interactions"""
        interactions = []
        for i in range(5):
            interaction = Mock()
            interaction.user_id = sample_user.id
            interaction.post_id = sample_post.id + i
            interaction.interaction_type = "view" if i % 2 == 0 else "like"
            interaction.interaction_score = 1.0
            interaction.created_at = datetime.utcnow() - timedelta(days=i)
            interactions.append(interaction)
        return interactions
    
    @pytest.mark.asyncio
    async def test_log_user_interaction(self, recommendation_service, sample_user, sample_post):
        """Test logging user interaction"""
        # Mock the database operations
        recommendation_service.db.add = Mock()
        recommendation_service.db.commit = AsyncMock()
        recommendation_service._update_user_preferences = AsyncMock()
        recommendation_service._update_post_trending_score = AsyncMock()
        
        # Test logging an interaction
        success = await recommendation_service.log_user_interaction(
            user_id=sample_user.id,
            post_id=sample_post.id,
            interaction_type="like",
            score=1.0,
            time_spent=30,
            scroll_depth=0.8
        )
        
        assert success is True
        recommendation_service.db.add.assert_called_once()
        recommendation_service._update_user_preferences.assert_called_once()
        recommendation_service._update_post_trending_score.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_personalized_recommendations_new_user(self, recommendation_service):
        """Test getting recommendations for a new user (cold start)"""
        # Mock empty user interactions
        recommendation_service.db.query.return_value.filter.return_value.all.return_value = []
        
        # Mock cold start recommendations
        recommendation_service._get_cold_start_recommendations = AsyncMock(return_value=[
            {"post_id": 1, "score": 0.5, "reason": "Popular content", "algorithm": "cold_start", "confidence": 0.5}
        ])
        
        recommendations = await recommendation_service.get_personalized_recommendations(
            user_id=999, limit=5
        )
        
        assert len(recommendations) == 1
        assert recommendations[0]["algorithm"] == "cold_start"
        recommendation_service._get_cold_start_recommendations.assert_called_once_with(5)
    
    @pytest.mark.asyncio
    async def test_get_personalized_recommendations_existing_user(self, recommendation_service, sample_user, sample_post):
        """Test getting recommendations for an existing user"""
        # Mock user interactions
        mock_interactions = [Mock()]
        mock_interactions[0].post_id = sample_post.id
        recommendation_service.db.query.return_value.filter.return_value.all.return_value = mock_interactions
        
        # Mock similar users finding
        recommendation_service._find_similar_users = AsyncMock(return_value=[(2, 0.8)])
        
        # Mock collaborative recommendations
        recommendation_service._get_collaborative_recommendations = AsyncMock(return_value=[
            {"post_id": 2, "score": 0.7, "reason": "Similar users liked this", "algorithm": "collaborative", "confidence": 0.8}
        ])
        
        # Mock content-based recommendations
        recommendation_service._get_content_based_recommendations = AsyncMock(return_value=[])
        
        # Mock trending recommendations
        recommendation_service._get_trending_recommendations = AsyncMock(return_value=[])
        
        # Mock merge and diversity functions
        recommendation_service._merge_and_deduplicate_recommendations = Mock(return_value=[
            {"post_id": 2, "score": 0.7, "reason": "Similar users liked this", "algorithm": "collaborative", "confidence": 0.8}
        ])
        recommendation_service._apply_diversity = AsyncMock(return_value=[
            {"post_id": 2, "score": 0.7, "reason": "Similar users liked this", "algorithm": "collaborative", "confidence": 0.8}
        ])
        
        recommendations = await recommendation_service.get_personalized_recommendations(
            user_id=sample_user.id, limit=5
        )
        
        assert len(recommendations) == 1
        assert recommendations[0]["algorithm"] == "collaborative"
    
    @pytest.mark.asyncio
    async def test_find_similar_users(self, recommendation_service, sample_user, sample_interactions):
        """Test finding similar users"""
        # Mock database queries
        recommendation_service.db.query.return_value.filter.return_value.all.return_value = sample_interactions
        
        similar_users = await recommendation_service._find_similar_users(
            user_id=sample_user.id, 
            user_interactions=sample_interactions
        )
        
        # Should return users with similar preferences
        assert isinstance(similar_users, list)
    
    @pytest.mark.asyncio
    async def test_calculate_content_similarity(self, recommendation_service, sample_user, sample_post):
        """Test calculating content similarity"""
        # Mock user preferences
        mock_preferences = [
            Mock(preference_type="category", preference_value="tech", strength=0.8),
            Mock(preference_type="author", preference_value="testuser", strength=0.6)
        ]
        recommendation_service.db.query.return_value.filter.return_value.all.return_value = mock_preferences
        
        # Mock post service
        recommendation_service.post_service.get_by_id = AsyncMock(return_value=sample_post)
        recommendation_service.ai_service.find_similar_content = AsyncMock(return_value=[])
        
        similarity_score = await recommendation_service._calculate_content_similarity(
            user_id=sample_user.id, post=sample_post
        )
        
        assert 0.0 <= similarity_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_get_similar_content_with_precomputed(self, recommendation_service, sample_post):
        """Test getting similar content with pre-computed similarities"""
        # Mock pre-computed similarities
        mock_similarities = [
            Mock(
                source_post_id=sample_post.id,
                target_post_id=2,
                similarity_score=0.8,
                algorithm="ai_embeddings",
                confidence=0.9
            )
        ]
        recommendation_service.db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_similarities
        
        similar_content = await recommendation_service.get_similar_content(
            post_id=sample_post.id, limit=5
        )
        
        assert len(similar_content) == 1
        assert similar_content[0]["similarity_score"] == 0.8
        assert similar_content[0]["algorithm"] == "ai_embeddings"
    
    @pytest.mark.asyncio
    async def test_get_similar_content_compute_on_fly(self, recommendation_service, sample_post):
        """Test computing similarities on-the-fly when pre-computed scores don't exist"""
        # Mock empty pre-computed similarities
        recommendation_service.db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        # Mock AI service similarity calculation
        mock_ai_similarities = [
            Mock(post_id=2, similarity_score=0.7),
            Mock(post_id=3, similarity_score=0.6)
        ]
        recommendation_service.ai_service.find_similar_content = AsyncMock(return_value=mock_ai_similarities)
        
        # Mock database commit
        recommendation_service.db.add = Mock()
        recommendation_service.db.commit = AsyncMock()
        
        similar_content = await recommendation_service.get_similar_content(
            post_id=sample_post.id, limit=5
        )
        
        assert len(similar_content) == 2
        assert similar_content[0]["algorithm"] == "ai_embeddings"
        
        # Verify that new similarity records were created
        assert recommendation_service.db.add.call_count == 2
    
    @pytest.mark.asyncio
    async def test_update_recommendation_feedback(self, recommendation_service, sample_user, sample_post):
        """Test updating recommendation feedback"""
        # Mock database operations
        recommendation_service.db.add = Mock()
        recommendation_service.db.commit = AsyncMock()
        
        success = await recommendation_service.update_recommendation_feedback(
            user_id=sample_user.id,
            post_id=sample_post.id,
            feedback_type="click",
            feedback_score=1.0,
            recommendation_type="personalized"
        )
        
        assert success is True
        recommendation_service.db.add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_preference_update(self, recommendation_service, sample_user, sample_post):
        """Test user preference update"""
        # Mock post with categories
        sample_post.categories = [Mock(name="technology"), Mock(name="AI")]
        
        # Mock preference query (no existing preferences)
        recommendation_service.db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock database operations
        recommendation_service.db.add = Mock()
        recommendation_service.ai_service.classify_content = AsyncMock(return_value={
            "topics": [{"topic": "machine learning", "relevance_score": 0.8}],
            "sentiment": {"label": "positive"}
        })
        
        await recommendation_service._update_user_preferences(
            user_id=sample_user.id,
            post_id=sample_post.id,
            interaction_type="like",
            score=1.0
        )
        
        # Should create multiple preference records
        assert recommendation_service.db.add.call_count >= 3  # categories + author + topics
    
    @pytest.mark.asyncio
    async def test_trending_score_update(self, recommendation_service, sample_post):
        """Test trending score calculation"""
        # Mock recent interactions
        mock_interactions = []
        for i in range(10):
            interaction = Mock()
            interaction.post_id = sample_post.id
            interaction.interaction_type = "view" if i % 3 == 0 else "like" if i % 3 == 1 else "share"
            interaction.created_at = datetime.utcnow() - timedelta(minutes=i * 10)
            mock_interactions.append(interaction)
        
        recommendation_service.db.query.return_value.filter.return_value.all.return_value = mock_interactions
        
        # Mock trending content (doesn't exist)
        recommendation_service.db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock database operations
        recommendation_service.db.add = Mock()
        
        await recommendation_service._update_post_trending_score(sample_post.id)
        
        # Should add new trending record
        recommendation_service.db.add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_merge_and_deduplicate_recommendations(self, recommendation_service):
        """Test merging recommendations from different algorithms"""
        recommendations = [
            {"post_id": 1, "score": 0.5, "algorithm": "collaborative", "reason": "Similar users", "confidence": 0.8},
            {"post_id": 1, "score": 0.3, "algorithm": "content_based", "reason": "Matches interests", "confidence": 0.7},
            {"post_id": 2, "score": 0.6, "algorithm": "trending", "reason": "Popular now", "confidence": 0.9}
        ]
        
        merged = recommendation_service._merge_and_deduplicate_recommendations(recommendations)
        
        # Should deduplicate post 1 and combine scores
        assert len(merged) == 2
        
        # Post 1 should have combined score
        post_1_rec = next(r for r in merged if r["post_id"] == 1)
        assert post_1_rec["score"] == 0.8  # 0.5 + 0.3
        
        # Post 2 should remain unchanged
        post_2_rec = next(r for r in merged if r["post_id"] == 2)
        assert post_2_rec["score"] == 0.6
    
    @pytest.mark.asyncio
    async def test_apply_diversity(self, recommendation_service):
        """Test applying diversity to recommendations"""
        recommendations = [
            {"post_id": 1, "score": 0.9},
            {"post_id": 2, "score": 0.8},
            {"post_id": 3, "score": 0.7},
            {"post_id": 4, "score": 0.6},
            {"post_id": 5, "score": 0.5}
        ]
        
        # Mock post service to return posts with different authors
        async def mock_get_by_id(post_id):
            post = Mock()
            post.author_id = post_id  # Different author for each post
            return post
        
        recommendation_service.post_service.get_by_id = mock_get_by_id
        
        diverse_recommendations = await recommendation_service._apply_diversity(recommendations, 3)
        
        # Should limit to 3 recommendations
        assert len(diverse_recommendations) == 3
        
        # Should be top 3 by score
        assert diverse_recommendations[0]["score"] == 0.9
        assert diverse_recommendations[1]["score"] == 0.8
        assert diverse_recommendations[2]["score"] == 0.7
    
    @pytest.mark.asyncio
    async def test_cold_start_recommendations(self, recommendation_service):
        """Test cold start recommendations for new users"""
        # Mock popular posts query
        mock_posts = []
        for i in range(5):
            post = Mock()
            post.id = i + 1
            post.title = f"Popular Post {i}"
            post.created_at = datetime.utcnow() - timedelta(days=i)
            mock_posts.append(post)
        
        recommendation_service.db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_posts
        
        cold_start_recs = await recommendation_service._get_cold_start_recommendations(3)
        
        assert len(cold_start_recs) == 3
        for rec in cold_start_recs:
            assert rec["algorithm"] == "cold_start"
            assert rec["score"] == 0.5
    
    def test_algorithm_weights_configuration(self, recommendation_service):
        """Test algorithm weights configuration"""
        weights = recommendation_service.weights
        
        assert "collaborative" in weights
        assert "content_based" in weights
        assert "trending" in weights
        assert "diversity" in weights
        
        # Weights should sum to 1.0
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 0.01


class TestRecommendationModels:
    """Test suite for recommendation data models"""
    
    def test_user_interaction_creation(self):
        """Test UserInteraction model creation"""
        interaction = UserInteraction(
            user_id=1,
            post_id=1,
            interaction_type="like",
            interaction_score=1.0,
            time_spent_seconds=30,
            scroll_depth=0.8
        )
        
        assert interaction.user_id == 1
        assert interaction.post_id == 1
        assert interaction.interaction_type == "like"
        assert interaction.interaction_score == 1.0
        assert interaction.time_spent_seconds == 30
        assert interaction.scroll_depth == 0.8
    
    def test_user_preference_creation(self):
        """Test UserPreference model creation"""
        preference = UserPreference(
            user_id=1,
            preference_type="category",
            preference_value="technology",
            strength=0.8,
            confidence=0.9,
            interaction_count=5,
            positive_interactions=4,
            negative_interactions=1
        )
        
        assert preference.user_id == 1
        assert preference.preference_type == "category"
        assert preference.preference_value == "technology"
        assert preference.strength == 0.8
        assert preference.confidence == 0.9
        assert preference.interaction_count == 5
    
    def test_content_embedding_creation(self):
        """Test ContentEmbedding model creation"""
        embedding = ContentEmbedding(
            post_id=1,
            embedding_type="text",
            embedding_vector=[0.1, 0.2, 0.3],
            model_name="all-MiniLM-L6-v2",
            vector_dimension=3,
            quality_score=0.8
        )
        
        assert embedding.post_id == 1
        assert embedding.embedding_type == "text"
        assert embedding.model_name == "all-MiniLM-L6-v2"
        assert embedding.vector_dimension == 3
        assert embedding.quality_score == 0.8
    
    def test_similarity_score_creation(self):
        """Test SimilarityScore model creation"""
        similarity = SimilarityScore(
            source_post_id=1,
            target_post_id=2,
            similarity_score=0.8,
            algorithm="cosine",
            confidence=0.9
        )
        
        assert similarity.source_post_id == 1
        assert similarity.target_post_id == 2
        assert similarity.similarity_score == 0.8
        assert similarity.algorithm == "cosine"
        assert similarity.confidence == 0.9
    
    def test_trending_content_creation(self):
        """Test TrendingContent model creation"""
        trending = TrendingContent(
            post_id=1,
            trend_score=0.9,
            velocity=0.5,
            views_count=100,
            likes_count=20,
            shares_count=5,
            comments_count=10
        )
        
        assert trending.post_id == 1
        assert trending.trend_score == 0.9
        assert trending.velocity == 0.5
        assert trending.views_count == 100
        assert trending.likes_count == 20
        assert trending.is_trending is True
    
    def test_recommendation_feedback_creation(self):
        """Test RecommendationFeedback model creation"""
        feedback = RecommendationFeedback(
            user_id=1,
            post_id=1,
            recommendation_type="personalized",
            feedback_type="click",
            feedback_score=1.0,
            position_in_list=1
        )
        
        assert feedback.user_id == 1
        assert feedback.post_id == 1
        assert feedback.recommendation_type == "personalized"
        assert feedback.feedback_type == "click"
        assert feedback.feedback_score == 1.0
        assert feedback.position_in_list == 1


class TestRecommendationEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def recommendation_service(self):
        """Create service with minimal mocking"""
        return EnhancedRecommendationService(
            db=Mock(),
            user_service=Mock(),
            post_service=Mock(),
            comment_service=Mock(),
            ai_service=Mock()
        )
    
    @pytest.mark.asyncio
    async def test_empty_recommendations(self, recommendation_service):
        """Test handling when no recommendations can be generated"""
        # Mock empty results from all algorithms
        recommendation_service._get_collaborative_recommendations = AsyncMock(return_value=[])
        recommendation_service._get_content_based_recommendations = AsyncMock(return_value=[])
        recommendation_service._get_trending_recommendations = AsyncMock(return_value=[])
        recommendation_service._merge_and_deduplicate_recommendations = Mock(return_value=[])
        recommendation_service._apply_diversity = AsyncMock(return_value=[])
        
        recommendations = await recommendation_service.get_personalized_recommendations(999, limit=10)
        
        assert recommendations == []
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, recommendation_service, sample_user):
        """Test handling of database errors"""
        # Mock database error
        recommendation_service.db.commit.side_effect = Exception("Database error")
        
        success = await recommendation_service.log_user_interaction(
            user_id=sample_user.id,
            post_id=1,
            interaction_type="view"
        )
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_ai_service_failure(self, recommendation_service):
        """Test handling when AI service fails"""
        # Mock AI service failure
        recommendation_service.ai_service.find_similar_content = AsyncMock(side_effect=Exception("AI service error"))
        
        # Should still work with fallback methods
        recommendations = await recommendation_service.get_personalized_recommendations(1, limit=5)
        
        # Should return empty rather than crash
        assert isinstance(recommendations, list)