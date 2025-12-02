"""
Tests for Recommendation API Endpoints
Comprehensive API tests for recommendation features
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.recommendations import router as recommendation_router
from app.services.recommendation_service import EnhancedRecommendationService
from app.schemas.recommendation import (
    InteractionLogRequest, RecommendationRequest, SimilarContentRequest,
    FeedbackRequest, TrendingRequest, AnalyticsRequest
)


class TestRecommendationAPI:
    """Test suite for recommendation API endpoints"""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app with recommendation router"""
        app = FastAPI()
        app.include_router(recommendation_router)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_recommendation_service(self):
        """Mock recommendation service"""
        return Mock(spec=EnhancedRecommendationService)
    
    def test_health_check_endpoint(self, client, mock_recommendation_service):
        """Test health check endpoint"""
        with patch('app.api.recommendations.get_recommendation_service', return_value=mock_recommendation_service):
            response = client.get("/recommendations/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "timestamp" in data
            assert "algorithms" in data
    
    def test_log_interaction_endpoint(self, client, mock_recommendation_service):
        """Test logging user interaction endpoint"""
        mock_recommendation_service.log_user_interaction = AsyncMock(return_value=True)
        
        interaction_data = {
            "user_id": 1,
            "post_id": 1,
            "interaction_type": "like",
            "score": 1.0,
            "time_spent_seconds": 30,
            "scroll_depth": 0.8
        }
        
        with patch('app.api.recommendations.get_recommendation_service', return_value=mock_recommendation_service):
            response = client.post("/recommendations/interactions/log", json=interaction_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "message" in data
            assert "timestamp" in data
            
            # Verify service was called with correct parameters
            mock_recommendation_service.log_user_interaction.assert_called_once()
            call_args = mock_recommendation_service.log_user_interaction.call_args
            assert call_args[1]["user_id"] == 1
            assert call_args[1]["post_id"] == 1
            assert call_args[1]["interaction_type"] == "like"
    
    def test_get_personalized_recommendations_endpoint(self, client, mock_recommendation_service):
        """Test personalized recommendations endpoint"""
        mock_recommendation_service.get_personalized_recommendations = AsyncMock(return_value=[
            {
                "post_id": 1,
                "score": 0.8,
                "reason": "Matches your interests",
                "algorithm": "collaborative",
                "confidence": 0.9
            },
            {
                "post_id": 2,
                "score": 0.7,
                "reason": "Trending now",
                "algorithm": "trending",
                "confidence": 0.8
            }
        ])
        
        request_data = {
            "user_id": 1,
            "limit": 10,
            "include_types": ["personalized", "trending"]
        }
        
        with patch('app.api.recommendations.get_recommendation_service', return_value=mock_recommendation_service):
            response = client.post("/recommendations/personalized", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "recommendations" in data
            assert "algorithm" in data
            assert "generated_at" in data
            assert "total_count" in data
            
            assert len(data["recommendations"]) == 2
            assert data["algorithm"] == "hybrid"
            assert data["total_count"] == 2
            
            # Verify service was called
            mock_recommendation_service.get_personalized_recommendations.assert_called_once()
    
    def test_get_similar_content_endpoint(self, client, mock_recommendation_service):
        """Test similar content endpoint"""
        mock_recommendation_service.get_similar_content = AsyncMock(return_value=[
            {
                "post_id": 2,
                "similarity_score": 0.8,
                "algorithm": "ai_embeddings",
                "confidence": 0.9
            },
            {
                "post_id": 3,
                "similarity_score": 0.7,
                "algorithm": "ai_embeddings",
                "confidence": 0.8
            }
        ])
        
        request_data = {
            "post_id": 1,
            "limit": 5
        }
        
        with patch('app.api.recommendations.get_recommendation_service', return_value=mock_recommendation_service):
            response = client.post("/recommendations/similar", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "similar_posts" in data
            assert "source_post_id" in data
            assert "generated_at" in data
            
            assert data["source_post_id"] == 1
            assert len(data["similar_posts"]) == 2
            assert data["similar_posts"][0]["similarity_score"] == 0.8
            
            # Verify service was called
            mock_recommendation_service.get_similar_content.assert_called_once_with(post_id=1, limit=5)
    
    def test_get_trending_content_endpoint(self, client, mock_recommendation_service):
        """Test trending content endpoint"""
        with patch('app.api.recommendations.get_recommendation_service') as mock_get_service:
            mock_service = Mock()
            mock_service.db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
                Mock(
                    post_id=1,
                    trend_score=0.9,
                    velocity=0.5,
                    views_count=100,
                    likes_count=20,
                    shares_count=5,
                    comments_count=10,
                    is_trending=True
                )
            ]
            
            mock_post_service = Mock()
            mock_post = Mock()
            mock_post.id = 1
            mock_post.title = "Trending Post"
            mock_post.author.username = "testuser"
            mock_post_service.get_by_id = AsyncMock(return_value=mock_post)
            
            mock_service.post_service = mock_post_service
            mock_get_service.return_value = mock_service
            
            response = client.get("/recommendations/trending?limit=10&timeframe=day")
            
            assert response.status_code == 200
            data = response.json()
            assert "trending_posts" in data
            assert "timeframe" in data
            assert "generated_at" in data
            assert "total_count" in data
            
            assert data["timeframe"] == "day"
            assert len(data["trending_posts"]) == 1
            assert data["trending_posts"][0]["trend_score"] == 0.9
    
    def test_submit_feedback_endpoint(self, client, mock_recommendation_service):
        """Test recommendation feedback endpoint"""
        mock_recommendation_service.update_recommendation_feedback = AsyncMock(return_value=True)
        
        feedback_data = {
            "user_id": 1,
            "post_id": 1,
            "feedback_type": "click",
            "feedback_score": 1.0,
            "recommendation_type": "personalized"
        }
        
        with patch('app.api.recommendations.get_recommendation_service', return_value=mock_recommendation_service):
            response = client.post("/recommendations/feedback", json=feedback_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "message" in data
            assert "timestamp" in data
            
            # Verify service was called
            mock_recommendation_service.update_recommendation_feedback.assert_called_once()
    
    def test_get_user_analytics_endpoint(self, client, mock_recommendation_service):
        """Test user analytics endpoint"""
        with patch('app.api.recommendations.get_recommendation_service') as mock_get_service:
            mock_service = Mock()
            
            # Mock user interactions
            mock_interactions = [
                Mock(interaction_type="view"),
                Mock(interaction_type="like"),
                Mock(interaction_type="share"),
                Mock(interaction_type="view"),
                Mock(interaction_type="like")
            ]
            mock_service.db.query.return_value.filter.return_value.all.return_value = mock_interactions
            
            # Mock user preferences
            mock_preferences = [
                Mock(
                    preference_type="category",
                    preference_value="technology",
                    strength=0.8,
                    confidence=0.9,
                    interaction_count=5,
                    positive_interactions=4,
                    negative_interactions=1,
                    last_interaction=Mock(isoformat=lambda: "2023-01-01T00:00:00")
                )
            ]
            mock_service.db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_preferences
            
            mock_get_service.return_value = mock_service
            
            response = client.get("/recommendations/analytics/1?days=30")
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == 1
            assert "analysis_period_days" in data
            assert "total_interactions" in data
            assert "interaction_types" in data
            assert "engagement_rate" in data
            assert "top_preferences" in data
            assert "recommendation_accuracy" in data
            
            assert data["total_interactions"] == 5
            assert data["engagement_rate"] == 0.4  # 2 likes + 1 share / 5 total
            assert len(data["top_preferences"]) == 1
    
    def test_get_user_preferences_endpoint(self, client, mock_recommendation_service):
        """Test user preferences endpoint"""
        with patch('app.api.recommendations.get_recommendation_service') as mock_get_service:
            mock_service = Mock()
            
            # Mock user preferences
            mock_preferences = [
                Mock(
                    id=1,
                    preference_type="category",
                    preference_value="technology",
                    strength=0.8,
                    confidence=0.9,
                    interaction_count=5,
                    positive_interactions=4,
                    negative_interactions=1,
                    last_interaction=Mock(isoformat=lambda: "2023-01-01T00:00:00")
                ),
                Mock(
                    id=2,
                    preference_type="author",
                    preference_value="testuser",
                    strength=0.6,
                    confidence=0.7,
                    interaction_count=3,
                    positive_interactions=3,
                    negative_interactions=0,
                    last_interaction=Mock(isoformat=lambda: "2023-01-01T00:00:00")
                )
            ]
            
            mock_service.db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_preferences
            mock_get_service.return_value = mock_service
            
            response = client.get("/recommendations/preferences/1?limit=20")
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == 1
            assert "total_preferences" in data
            assert "preferences" in data
            assert "generated_at" in data
            
            assert data["total_preferences"] == 2
            assert len(data["preferences"]) == 2
            assert data["preferences"][0]["type"] == "category"
            assert data["preferences"][1]["value"] == "testuser"
    
    def test_delete_user_preference_endpoint(self, client, mock_recommendation_service):
        """Test delete user preference endpoint"""
        with patch('app.api.recommendations.get_recommendation_service') as mock_get_service:
            mock_service = Mock()
            
            # Mock existing preference
            mock_preference = Mock()
            mock_service.db.query.return_value.filter.return_value.first.return_value = mock_preference
            
            mock_get_service.return_value = mock_service
            
            response = client.delete("/recommendations/preferences/1/1")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Preference removed successfully"
            assert data["preference_id"] == 1
            
            # Verify preference was deactivated
            assert mock_preference.is_active is False
            mock_service.db.commit.assert_called_once()
    
    def test_delete_nonexistent_preference(self, client, mock_recommendation_service):
        """Test deleting a non-existent preference"""
        with patch('app.api.recommendations.get_recommendation_service') as mock_get_service:
            mock_service = Mock()
            
            # Mock non-existent preference
            mock_service.db.query.return_value.filter.return_value.first.return_value = None
            mock_get_service.return_value = mock_service
            
            response = client.delete("/recommendations/preferences/1/999")
            
            assert response.status_code == 404
            assert "Preference not found" in response.json()["detail"]
    
    def test_explore_content_endpoint(self, client, mock_recommendation_service):
        """Test explore new content endpoint"""
        with patch('app.api.recommendations.get_recommendation_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            response = client.get("/recommendations/explore/1?limit=10")
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == 1
            assert "exploration_recommendations" in data
            assert "strategy" in data
            assert "generated_at" in data
    
    def test_cold_start_recommendations_endpoint(self, client, mock_recommendation_service):
        """Test cold start recommendations endpoint"""
        with patch('app.api.recommendations.get_recommendation_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            response = client.get("/recommendations/cold-start/1?limit=5")
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == 1
            assert "cold_start_recommendations" in data
            assert "strategy" in data
            assert "interests_provided" in data
            assert "generated_at" in data


class TestRecommendationAPIEdgeCases:
    """Test edge cases and error handling in API"""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app"""
        app = FastAPI()
        app.include_router(recommendation_router)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)
    
    def test_invalid_interaction_type(self, client):
        """Test invalid interaction type validation"""
        invalid_data = {
            "user_id": 1,
            "post_id": 1,
            "interaction_type": "invalid_type",  # Invalid enum value
            "score": 1.0
        }
        
        response = client.post("/recommendations/interactions/log", json=invalid_data)
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_invalid_feedback_type(self, client):
        """Test invalid feedback type validation"""
        invalid_data = {
            "user_id": 1,
            "post_id": 1,
            "feedback_type": "invalid_type",  # Invalid enum value
            "feedback_score": 1.0
        }
        
        response = client.post("/recommendations/feedback", json=invalid_data)
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_service_unavailable_error(self, client):
        """Test handling when recommendation service is unavailable"""
        with patch('app.api.recommendations.get_recommendation_service', side_effect=Exception("Service unavailable")):
            response = client.post("/recommendations/personalized", json={
                "user_id": 1,
                "limit": 10
            })
            
            # Should return 500 error
            assert response.status_code == 500
    
    def test_missing_required_fields(self, client):
        """Test missing required fields in request"""
        # Missing required fields
        incomplete_data = {
            "user_id": 1
            # Missing other required fields
        }
        
        response = client.post("/recommendations/interactions/log", json=incomplete_data)
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_invalid_limit_parameters(self, client):
        """Test invalid limit parameters"""
        with patch('app.api.recommendations.get_recommendation_service'):
            # Test limit too high
            response = client.post("/recommendations/personalized", json={
                "user_id": 1,
                "limit": 100  # Above maximum
            })
            
            assert response.status_code == 422
            
            # Test limit too low
            response = client.post("/recommendations/personalized", json={
                "user_id": 1,
                "limit": 0  # Below minimum
            })
            
            assert response.status_code == 422
    
    def test_invalid_timeframe_parameter(self, client):
        """Test invalid timeframe parameter for trending content"""
        with patch('app.api.recommendations.get_recommendation_service'):
            response = client.get("/recommendations/trending?timeframe=invalid")
            
            # Should return validation error for query parameter
            assert response.status_code == 422
    
    def test_database_connection_error(self, client, mock_recommendation_service):
        """Test database connection errors"""
        mock_recommendation_service.db.execute.side_effect = Exception("Database connection error")
        
        with patch('app.api.recommendations.get_recommendation_service', return_value=mock_recommendation_service):
            response = client.get("/recommendations/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["database_connection"] is False


class TestRecommendationAPIIntegration:
    """Integration tests for recommendation API"""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app"""
        app = FastAPI()
        app.include_router(recommendation_router)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)
    
    def test_complete_recommendation_workflow(self, client, mock_recommendation_service):
        """Test complete recommendation workflow"""
        with patch('app.api.recommendations.get_recommendation_service', return_value=mock_recommendation_service):
            # Step 1: Log user interaction
            mock_recommendation_service.log_user_interaction = AsyncMock(return_value=True)
            
            interaction_response = client.post("/recommendations/interactions/log", json={
                "user_id": 1,
                "post_id": 1,
                "interaction_type": "view",
                "score": 1.0,
                "time_spent_seconds": 45
            })
            
            assert interaction_response.status_code == 200
            
            # Step 2: Get personalized recommendations
            mock_recommendation_service.get_personalized_recommendations = AsyncMock(return_value=[
                {
                    "post_id": 2,
                    "score": 0.8,
                    "reason": "Based on your viewing history",
                    "algorithm": "collaborative",
                    "confidence": 0.9
                }
            ])
            
            recommendations_response = client.post("/recommendations/personalized", json={
                "user_id": 1,
                "limit": 5
            })
            
            assert recommendations_response.status_code == 200
            recommendations_data = recommendations_response.json()
            assert len(recommendations_data["recommendations"]) == 1
            
            # Step 3: Submit feedback on recommendation
            mock_recommendation_service.update_recommendation_feedback = AsyncMock(return_value=True)
            
            feedback_response = client.post("/recommendations/feedback", json={
                "user_id": 1,
                "post_id": 2,
                "feedback_type": "click",
                "feedback_score": 1.0,
                "recommendation_type": "personalized"
            })
            
            assert feedback_response.status_code == 200
            
            # Step 4: Get analytics
            with patch('app.api.recommendations.get_recommendation_service') as mock_get_service:
                mock_service = Mock()
                mock_service.db.query.return_value.filter.return_value.all.return_value = []
                mock_service.db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
                mock_get_service.return_value = mock_service
                
                analytics_response = client.get("/recommendations/analytics/1")
                assert analytics_response.status_code == 200
    
    def test_concurrent_requests(self, client, mock_recommendation_service):
        """Test handling of concurrent requests"""
        with patch('app.api.recommendations.get_recommendation_service', return_value=mock_recommendation_service):
            mock_recommendation_service.log_user_interaction = AsyncMock(return_value=True)
            
            import concurrent.futures
            import threading
            
            def make_request(request_id):
                return client.post("/recommendations/interactions/log", json={
                    "user_id": request_id,
                    "post_id": 1,
                    "interaction_type": "view"
                })
            
            # Test concurrent interaction logging
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, i) for i in range(10)]
                results = [future.result() for future in futures]
                
                # All requests should succeed
                for result in results:
                    assert result.status_code == 200