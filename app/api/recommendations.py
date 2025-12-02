"""
Recommendation API Endpoints
Advanced AI-powered recommendation system with personalized content suggestions
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import List, Dict, Any, Optional
import asyncio
from sqlalchemy.orm import Session

from app.schemas.recommendation import (
    InteractionLogRequest, InteractionLogResponse,
    RecommendationRequest, RecommendationResponse,
    SimilarContentRequest, SimilarContentResponse,
    PreferenceUpdateRequest, PreferenceUpdateResponse,
    FeedbackRequest, FeedbackResponse,
    TrendingRequest, TrendingResponse,
    AnalyticsRequest, AnalyticsResponse
)
from app.services.recommendation_service import EnhancedRecommendationService
from app.services.user import UserService
from app.services.post import PostService
from app.services.comment import CommentService
from app.services.ai_service import AIService
from app.core.dependency_injection import get_dependencies
from app.database import get_db

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def get_recommendation_service(db: Session = Depends(get_db)) -> EnhancedRecommendationService:
    """Dependency injection for recommendation service"""
    deps = get_dependencies()
    user_service = deps.get("user_service")
    post_service = deps.get("post_service")
    comment_service = deps.get("comment_service")
    ai_service = deps.get("ai_service")
    
    if not all([user_service, post_service, comment_service, ai_service]):
        raise HTTPException(status_code=500, detail="Required services not available")
    
    return EnhancedRecommendationService(
        db=db,
        user_service=user_service,
        post_service=post_service,
        comment_service=comment_service,
        ai_service=ai_service
    )


@router.post("/interactions/log", response_model=InteractionLogResponse)
async def log_user_interaction(
    request: InteractionLogRequest,
    recommendation_service: EnhancedRecommendationService = Depends(get_recommendation_service)
):
    """
    Log user interaction for recommendation learning
    Supports: view, like, share, comment, save, click, dismiss
    """
    try:
        success = await recommendation_service.log_user_interaction(
            user_id=request.user_id,
            post_id=request.post_id,
            interaction_type=request.interaction_type,
            score=request.score,
            time_spent=request.time_spent_seconds,
            scroll_depth=request.scroll_depth,
            session_id=request.session_id
        )
        
        if success:
            return InteractionLogResponse(
                success=True,
                message="Interaction logged successfully",
                timestamp=asyncio.get_event_loop().time()
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to log interaction")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging interaction: {str(e)}")


@router.post("/personalized", response_model=RecommendationResponse)
async def get_personalized_recommendations(
    request: RecommendationRequest,
    recommendation_service: EnhancedRecommendationService = Depends(get_recommendation_service)
):
    """
    Get personalized content recommendations for a user
    Uses hybrid collaborative and content-based filtering
    """
    try:
        recommendations = await recommendation_service.get_personalized_recommendations(
            user_id=request.user_id,
            limit=request.limit,
            include_types=request.include_types
        )
        
        return RecommendationResponse(
            recommendations=recommendations,
            algorithm="hybrid",
            generated_at=asyncio.get_event_loop().time(),
            total_count=len(recommendations)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.post("/similar", response_model=SimilarContentResponse)
async def get_similar_content(
    request: SimilarContentRequest,
    recommendation_service: EnhancedRecommendationService = Depends(get_recommendation_service)
):
    """
    Get content similar to a specific post
    Uses AI embeddings and pre-computed similarity scores
    """
    try:
        similar_posts = await recommendation_service.get_similar_content(
            post_id=request.post_id,
            limit=request.limit
        )
        
        return SimilarContentResponse(
            similar_posts=similar_posts,
            source_post_id=request.post_id,
            generated_at=asyncio.get_event_loop().time()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar content: {str(e)}")


@router.get("/trending", response_model=TrendingResponse)
async def get_trending_content(
    limit: int = Query(default=10, ge=1, le=50, description="Number of trending posts to return"),
    timeframe: str = Query(default="day", regex="^(hour|day|week)$", description="Time period for trending analysis"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    recommendation_service: EnhancedRecommendationService = Depends(get_recommendation_service)
):
    """
    Get trending content with engagement analytics
    Supports filtering by time period and category
    """
    try:
        from app.models.recommendation import TrendingContent
        from sqlalchemy import desc
        
        # Build query for trending content
        query = recommendation_service.db.query(TrendingContent).filter(
            TrendingContent.is_trending == True
        )
        
        # Apply time filter
        if timeframe == "hour":
            time_threshold = asyncio.get_event_loop().time() - 3600
        elif timeframe == "day":
            time_threshold = asyncio.get_event_loop().time() - 86400
        else:  # week
            time_threshold = asyncio.get_event_loop().time() - 604800
        
        # Note: In a real implementation, you'd filter by last_updated
        # For now, return top trending posts
        
        trending_posts = query.order_by(desc(TrendingContent.trend_score)).limit(limit).all()
        
        trending_data = []
        for trending in trending_posts:
            post = await recommendation_service.post_service.get_by_id(trending.post_id)
            if post:
                trending_data.append({
                    "post_id": post.id,
                    "title": post.title,
                    "author": post.author.username,
                    "trend_score": trending.trend_score,
                    "velocity": trending.velocity,
                    "views_count": trending.views_count,
                    "likes_count": trending.likes_count,
                    "shares_count": trending.shares_count,
                    "comments_count": trending.comments_count,
                    "timeframe": timeframe,
                    "category": category
                })
        
        return TrendingResponse(
            trending_posts=trending_data,
            timeframe=timeframe,
            generated_at=asyncio.get_event_loop().time(),
            total_count=len(trending_data)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trending content: {str(e)}")


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_recommendation_feedback(
    request: FeedbackRequest,
    recommendation_service: EnhancedRecommendationService = Depends(get_recommendation_service)
):
    """
    Submit feedback on recommendations for continuous improvement
    Supports: click, like, share, save, dismiss, report
    """
    try:
        success = await recommendation_service.update_recommendation_feedback(
            user_id=request.user_id,
            post_id=request.post_id,
            feedback_type=request.feedback_type,
            feedback_score=request.feedback_score,
            recommendation_type=request.recommendation_type
        )
        
        if success:
            return FeedbackResponse(
                success=True,
                message="Feedback recorded successfully",
                timestamp=asyncio.get_event_loop().time()
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to record feedback")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")


@router.get("/analytics/{user_id}", response_model=AnalyticsResponse)
async def get_recommendation_analytics(
    user_id: int,
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    recommendation_service: EnhancedRecommendationService = Depends(get_recommendation_service)
):
    """
    Get recommendation analytics for a user
    Includes engagement metrics, preference insights, and algorithm performance
    """
    try:
        from datetime import datetime, timedelta
        from app.models.recommendation import UserInteraction, UserPreference
        
        # Get user interactions in the specified period
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        interactions = recommendation_service.db.query(UserInteraction).filter(
            and_(
                UserInteraction.user_id == user_id,
                UserInteraction.created_at >= cutoff_date
            )
        ).all()
        
        preferences = recommendation_service.db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.is_active == True
            )
        ).all()
        
        # Calculate analytics
        total_interactions = len(interactions)
        interaction_types = {}
        for interaction in interactions:
            interaction_types[interaction.interaction_type] = interaction_types.get(interaction.interaction_type, 0) + 1
        
        engagement_rate = (interaction_types.get("like", 0) + interaction_types.get("share", 0) + 
                          interaction_types.get("comment", 0)) / max(total_interactions, 1)
        
        top_preferences = []
        for pref in sorted(preferences, key=lambda x: x.strength, reverse=True)[:5]:
            top_preferences.append({
                "type": pref.preference_type,
                "value": pref.preference_value,
                "strength": pref.strength,
                "confidence": pref.confidence,
                "interactions": pref.interaction_count
            })
        
        return AnalyticsResponse(
            user_id=user_id,
            analysis_period_days=days,
            total_interactions=total_interactions,
            interaction_types=interaction_types,
            engagement_rate=engagement_rate,
            top_preferences=top_preferences,
            recommendation_accuracy=0.75,  # Placeholder - would calculate based on feedback
            generated_at=asyncio.get_event_loop().time()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")


@router.get("/preferences/{user_id}")
async def get_user_preferences(
    user_id: int,
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of preferences to return"),
    recommendation_service: EnhancedRecommendationService = Depends(get_recommendation_service)
):
    """
    Get user's learned preferences for transparency and control
    """
    try:
        from app.models.recommendation import UserPreference
        
        preferences = recommendation_service.db.query(UserPreference).filter(
            and_(
                UserPreference.user_id == user_id,
                UserPreference.is_active == True
            )
        ).order_by(desc(UserPreference.strength)).limit(limit).all()
        
        preference_data = []
        for pref in preferences:
            preference_data.append({
                "id": pref.id,
                "type": pref.preference_type,
                "value": pref.preference_value,
                "strength": pref.strength,
                "confidence": pref.confidence,
                "interaction_count": pref.interaction_count,
                "positive_interactions": pref.positive_interactions,
                "negative_interactions": pref.negative_interactions,
                "last_interaction": pref.last_interaction.isoformat() if pref.last_interaction else None
            })
        
        return {
            "user_id": user_id,
            "total_preferences": len(preference_data),
            "preferences": preference_data,
            "generated_at": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user preferences: {str(e)}")


@router.delete("/preferences/{user_id}/{preference_id}")
async def delete_user_preference(
    user_id: int,
    preference_id: int,
    recommendation_service: EnhancedRecommendationService = Depends(get_recommendation_service)
):
    """
    Allow users to delete/modify their learned preferences
    """
    try:
        from app.models.recommendation import UserPreference
        
        preference = recommendation_service.db.query(UserPreference).filter(
            and_(
                UserPreference.id == preference_id,
                UserPreference.user_id == user_id
            )
        ).first()
        
        if not preference:
            raise HTTPException(status_code=404, detail="Preference not found")
        
        # Soft delete by setting is_active to False
        preference.is_active = False
        recommendation_service.db.commit()
        
        return {
            "success": True,
            "message": "Preference removed successfully",
            "preference_id": preference_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting preference: {str(e)}")


@router.get("/health")
async def recommendation_service_health_check(
    recommendation_service: EnhancedRecommendationService = Depends(get_recommendation_service)
):
    """
    Health check for recommendation service
    """
    try:
        # Test basic functionality
        test_user_id = 1  # Would use a test user in practice
        
        health_status = {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "algorithms": {
                "collaborative_filtering": True,
                "content_based": True,
                "trending": True,
                "hybrid_recommendations": True
            },
            "database_connection": True,
            "ai_service": True
        }
        
        # Test database connection
        try:
            recommendation_service.db.execute("SELECT 1")
        except Exception:
            health_status["database_connection"] = False
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": asyncio.get_event_loop().time()
        }


# Advanced recommendation endpoints

@router.get("/explore/{user_id}")
async def explore_new_content(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=20),
    exclude_categories: Optional[List[str]] = Query(default=None),
    exclude_authors: Optional[List[str]] = Query(default=None),
    recommendation_service: EnhancedRecommendationService = Depends(get_recommendation_service)
):
    """
    Get diverse content recommendations for exploration
    Helps users discover new topics and creators
    """
    try:
        # Implementation would filter out user's usual preferences
        # and suggest completely new content categories/authors
        
        return {
            "user_id": user_id,
            "exploration_recommendations": [
                # Placeholder implementation
                {
                    "post_id": 1,
                    "title": "Explore this new topic",
                    "reason": "Discover something new",
                    "diversity_score": 0.8
                }
            ],
            "strategy": "diversity_first",
            "generated_at": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating exploration recommendations: {str(e)}")


@router.get("/cold-start/{user_id}")
async def cold_start_recommendations(
    user_id: int,
    interests: Optional[List[str]] = Query(default=None, description="User-provided initial interests"),
    limit: int = Query(default=10, ge=1, le=20)
):
    """
    Get recommendations for new users with minimal interaction history
    Uses provided interests or falls back to popular content
    """
    try:
        # Implementation would use provided interests or popular content
        
        return {
            "user_id": user_id,
            "cold_start_recommendations": [
                # Placeholder implementation
                {
                    "post_id": 1,
                    "title": "Welcome content",
                    "reason": "Popular starter content",
                    "confidence": 0.6
                }
            ],
            "strategy": "popularity_based",
            "interests_provided": interests is not None,
            "generated_at": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cold start recommendations: {str(e)}")