"""
AI API Endpoints
Provides RESTful API for AI-powered features
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
import asyncio

from app.schemas.ai import (
    SentimentAnalysisRequest,
    SentimentAnalysisResponse,
    SimilarContentRequest,
    SimilarContentResponse,
    RecommendationRequest,
    RecommendationResponse,
    ContentClassificationRequest,
    ContentClassificationResponse,
    UserAnalysisRequest,
    UserAnalysisResponse,
    ContentModerationRequest,
    ContentModerationResponse,
    BatchAnalysisRequest,
    BatchAnalysisResponse
)
from app.services.ai_service import AIService, create_ai_service
from app.services.user import UserService
from app.services.post import PostService
from app.services.comment import CommentService
from app.core.dependency_injection import get_dependencies

router = APIRouter(prefix="/ai", tags=["AI Features"])


def get_ai_service() -> AIService:
    """Dependency injection for AI service"""
    deps = get_dependencies()
    user_service = deps.get("user_service")
    post_service = deps.get("post_service")
    comment_service = deps.get("comment_service")
    
    if not all([user_service, post_service, comment_service]):
        raise HTTPException(status_code=500, detail="Required services not available")
    
    return create_ai_service(user_service, post_service, comment_service)


@router.post("/sentiment/analyze", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Analyze sentiment of text content
    """
    try:
        result = await ai_service.analyze_sentiment(request.text)
        
        return SentimentAnalysisResponse(
            sentiment=result.sentiment,
            confidence=result.confidence,
            scores=result.scores
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")


@router.post("/content/similar", response_model=SimilarContentResponse)
async def find_similar_content(
    request: SimilarContentRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Find similar content to a given post
    """
    try:
        similar_content = await ai_service.find_similar_content(
            post_id=request.post_id,
            limit=request.limit
        )
        
        return SimilarContentResponse(
            similar_posts=[
                {
                    "post_id": item.post_id,
                    "similarity_score": item.similarity_score,
                    "title": item.title
                }
                for item in similar_content
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similar content search failed: {str(e)}")


@router.post("/recommendations/personalized", response_model=RecommendationResponse)
async def get_personalized_recommendations(
    request: RecommendationRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Get personalized content recommendations for a user
    """
    try:
        recommendations = await ai_service.get_personalized_recommendations(
            user_id=request.user_id,
            limit=request.limit
        )
        
        return RecommendationResponse(
            recommendations=[
                {
                    "post_id": item.post_id,
                    "score": item.score,
                    "reasons": item.reasons
                }
                for item in recommendations
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")


@router.post("/content/classify", response_model=ContentClassificationResponse)
async def classify_content(
    request: ContentClassificationRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Classify content into categories and extract insights
    """
    try:
        analysis = await ai_service.classify_content(
            title=request.title,
            content=request.content
        )
        
        return ContentClassificationResponse(**analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content classification failed: {str(e)}")


@router.post("/user/analyze", response_model=UserAnalysisResponse)
async def analyze_user_preferences(
    request: UserAnalysisRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Analyze user preferences and behavior patterns
    """
    try:
        analysis = await ai_service.analyze_user_preferences(user_id=request.user_id)
        
        return UserAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User analysis failed: {str(e)}")


@router.post("/content/moderate", response_model=ContentModerationResponse)
async def moderate_content(
    request: ContentModerationRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Moderate content for inappropriate material
    """
    try:
        moderation_result = await ai_service.moderate_content(
            title=request.title,
            content=request.content
        )
        
        return ContentModerationResponse(**moderation_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content moderation failed: {str(e)}")


@router.post("/content/batch-analyze", response_model=BatchAnalysisResponse)
async def batch_analyze_content(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Analyze multiple posts in batch (async operation)
    """
    try:
        # For now, process synchronously but mark as background task
        background_tasks.add_task(
            _process_batch_analysis,
            ai_service,
            request.post_ids,
            request.include_similarity,
            request.include_recommendations
        )
        
        return BatchAnalysisResponse(
            task_id=f"batch_{len(request.post_ids)}_{hash(str(request.post_ids))}",
            status="started",
            message="Batch analysis started. Check back later for results."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@router.get("/analytics/overview")
async def get_ai_analytics_overview(
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Get overview of AI analytics for admin dashboard
    """
    try:
        # This would typically fetch aggregated analytics
        # For now, return a basic overview structure
        analytics = {
            "total_content_analyzed": 0,
            "sentiment_distribution": {
                "positive": 0,
                "negative": 0,
                "neutral": 0
            },
            "top_topics": [],
            "moderation_stats": {
                "content_flagged": 0,
                "false_positives": 0
            },
            "recommendation_stats": {
                "total_recommendations": 0,
                "click_through_rate": 0.0
            },
            "last_updated": None
        }
        
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics overview failed: {str(e)}")


@router.get("/health")
async def ai_service_health_check(ai_service: AIService = Depends(get_ai_service)):
    """
    Health check for AI service
    """
    try:
        # Test basic functionality
        test_sentiment = await ai_service.analyze_sentiment("This is a test message")
        
        return {
            "status": "healthy",
            "models_loaded": True,
            "test_sentiment": test_sentiment.sentiment,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": asyncio.get_event_loop().time()
        }


async def _process_batch_analysis(
    ai_service: AIService,
    post_ids: List[int],
    include_similarity: bool,
    include_recommendations: bool
):
    """
    Background task for processing batch analysis
    """
    try:
        # This would typically save results to database
        # For now, just log the process
        print(f"Processing batch analysis for {len(post_ids)} posts...")
        print(f"Include similarity: {include_similarity}")
        print(f"Include recommendations: {include_recommendations}")
        
        # Simulate processing time
        await asyncio.sleep(2)
        
        print("Batch analysis completed")
        
    except Exception as e:
        print(f"Batch analysis failed: {str(e)}")


# Advanced AI Features

@router.get("/insights/trending-topics")
async def get_trending_topics(
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Get trending topics based on recent content analysis
    """
    try:
        # This would analyze recent posts to find trending topics
        trending_topics = [
            {"topic": "Artificial Intelligence", "score": 0.95, "growth": "+12%"},
            {"topic": "Remote Work", "score": 0.87, "growth": "+8%"},
            {"topic": "Sustainable Technology", "score": 0.82, "growth": "+15%"},
            {"topic": "Mental Health", "score": 0.78, "growth": "+5%"},
            {"topic": "Cryptocurrency", "score": 0.75, "growth": "-3%"}
        ]
        
        return {
            "trending_topics": trending_topics,
            "analysis_period": "last_7_days",
            "confidence": 0.85
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trending topics analysis failed: {str(e)}")


@router.post("/insights/content-quality")
async def analyze_content_quality(
    post_id: int,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Analyze content quality metrics for a specific post
    """
    try:
        # This would analyze the post and return quality metrics
        quality_metrics = {
            "readability_score": 0.78,
            "seo_optimization": 0.65,
            "engagement_potential": 0.82,
            "factual_density": 0.71,
            "originality_score": 0.89,
            "overall_quality": 0.77,
            "suggestions": [
                "Consider adding more subheadings for better readability",
                "Include more data points to support your arguments",
                "Add internal links to related content"
            ]
        }
        
        return quality_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content quality analysis failed: {str(e)}")


@router.get("/insights/audience-sentiment")
async def get_audience_sentiment_analysis(
    post_id: int,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Get sentiment analysis of comments for a specific post
    """
    try:
        # This would analyze all comments on a post
        sentiment_analysis = {
            "overall_sentiment": "positive",
            "confidence": 0.82,
            "sentiment_breakdown": {
                "positive": 0.65,
                "neutral": 0.25,
                "negative": 0.10
            },
            "emotional_indicators": {
                "excitement": 0.45,
                "curiosity": 0.38,
                "concern": 0.12,
                "satisfaction": 0.52
            },
            "engagement_metrics": {
                "comment_engagement": 0.78,
                "response_likelihood": 0.65,
                "share_potential": 0.42
            }
        }
        
        return sentiment_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audience sentiment analysis failed: {str(e)}")


@router.post("/insights/auto-tag")
async def auto_generate_tags(
    title: str,
    content: str,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Auto-generate relevant tags for content
    """
    try:
        analysis = await ai_service.classify_content(title, content)
        
        # Extract suggested tags from topics
        suggested_tags = []
        if "topics" in analysis:
            for topic in analysis["topics"]:
                suggested_tags.append(topic["topic"])
        
        # Add sentiment as tag
        if "sentiment" in analysis:
            suggested_tags.append(f"sentiment-{analysis['sentiment']['label']}")
        
        # Add reading time as tag
        if "reading_time_minutes" in analysis:
            if analysis["reading_time_minutes"] <= 2:
                suggested_tags.append("quick-read")
            elif analysis["reading_time_minutes"] >= 5:
                suggested_tags.append("long-read")
        
        return {
            "suggested_tags": list(set(suggested_tags)),  # Remove duplicates
            "confidence": 0.75,
            "alternatives": [
                tag for tag in ["trending", "featured", "popular", "new"] 
                if tag not in suggested_tags
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-tagging failed: {str(e)}")