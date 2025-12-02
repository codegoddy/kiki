"""
AI Schemas
Pydantic models for AI/ML API endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SentimentAnalysisRequest(BaseModel):
    text: str = Field(..., description="Text to analyze for sentiment")


class SentimentAnalysisResponse(BaseModel):
    sentiment: SentimentLabel
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    scores: Dict[str, float] = Field(..., description="Detailed sentiment scores")


class SimilarContentRequest(BaseModel):
    post_id: int = Field(..., description="ID of the post to find similar content for")
    limit: int = Field(default=5, ge=1, le=20, description="Maximum number of similar posts to return")


class SimilarContentResponse(BaseModel):
    similar_posts: List[Dict[str, Union[int, float, str]]] = Field(
        ..., description="List of similar posts with similarity scores"
    )


class RecommendationRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user to get recommendations for")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of recommendations to return")


class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Union[int, float, List[str]]]] = Field(
        ..., description="List of recommended posts with scores and reasons"
    )


class ContentClassificationRequest(BaseModel):
    title: str = Field(..., description="Title of the content to classify")
    content: str = Field(..., description="Content body to classify")


class ContentClassificationResponse(BaseModel):
    sentiment: Dict[str, Any] = Field(..., description="Sentiment analysis results")
    topics: List[Dict[str, Any]] = Field(..., description="Extracted topics with relevance scores")
    reading_time_minutes: int = Field(..., description="Estimated reading time in minutes")
    complexity: str = Field(..., description="Content complexity level (simple/medium/complex)")
    word_count: int = Field(..., description="Total word count")
    character_count: int = Field(..., description="Total character count")
    estimated_engagement: str = Field(..., description="Estimated engagement level (low/medium/high)")


class UserAnalysisRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user to analyze")


class UserAnalysisResponse(BaseModel):
    total_posts: int = Field(..., description="Total number of posts by user")
    total_comments: int = Field(..., description="Total number of comments by user")
    preferred_categories: Dict[str, int] = Field(..., description="Preferred content categories")
    sentiment_distribution: Dict[str, int] = Field(..., description="Distribution of sentiment in user's content")
    content_length_stats: Dict[str, float] = Field(..., description="Statistics about content length")
    engagement_score: float = Field(..., ge=0.0, le=1.0, description="User engagement score")


class ContentModerationRequest(BaseModel):
    title: str = Field(..., description="Title to moderate")
    content: str = Field(..., description="Content to moderate")


class ContentModerationResponse(BaseModel):
    approved: bool = Field(..., description="Whether content is approved")
    issues_found: List[Dict[str, Any]] = Field(default_factory=list, description="List of issues found")
    severity: str = Field(..., description="Overall severity level")
    total_issues: int = Field(..., description="Total number of issues found")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Moderation confidence score")
    action_required: str = Field(..., description="Required action (none/review/block)")


class BatchAnalysisRequest(BaseModel):
    post_ids: List[int] = Field(..., description="List of post IDs to analyze")
    include_similarity: bool = Field(default=True, description="Include similarity analysis")
    include_recommendations: bool = Field(default=False, description="Include recommendation analysis")


class BatchAnalysisResponse(BaseModel):
    task_id: str = Field(..., description="Unique task ID for tracking")
    status: str = Field(..., description="Task status (started/processing/completed/failed)")
    message: str = Field(..., description="Status message")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")


class TrendingTopic(BaseModel):
    topic: str = Field(..., description="Topic name")
    score: float = Field(..., ge=0.0, le=1.0, description="Trending score")
    growth: str = Field(..., description="Growth percentage with sign")


class AnalyticsOverview(BaseModel):
    total_content_analyzed: int = Field(..., description="Total content pieces analyzed")
    sentiment_distribution: Dict[str, int] = Field(..., description="Distribution of sentiments")
    top_topics: List[str] = Field(..., description="Most popular topics")
    moderation_stats: Dict[str, int] = Field(..., description="Content moderation statistics")
    recommendation_stats: Dict[str, Union[int, float]] = Field(..., description="Recommendation statistics")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")


class QualityMetrics(BaseModel):
    readability_score: float = Field(..., ge=0.0, le=1.0, description="Content readability score")
    seo_optimization: float = Field(..., ge=0.0, le=1.0, description="SEO optimization score")
    engagement_potential: float = Field(..., ge=0.0, le=1.0, description="Engagement potential score")
    factual_density: float = Field(..., ge=0.0, le=1.0, description="Factual content density")
    originality_score: float = Field(..., ge=0.0, le=1.0, description="Content originality score")
    overall_quality: float = Field(..., ge=0.0, le=1.0, description="Overall quality score")
    suggestions: List[str] = Field(..., description="Improvement suggestions")


class AudienceSentimentAnalysis(BaseModel):
    overall_sentiment: SentimentLabel = Field(..., description="Overall audience sentiment")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence")
    sentiment_breakdown: Dict[str, float] = Field(..., description="Detailed sentiment breakdown")
    emotional_indicators: Dict[str, float] = Field(..., description="Emotional indicators")
    engagement_metrics: Dict[str, float] = Field(..., description="Engagement metrics")


class AutoTaggingResponse(BaseModel):
    suggested_tags: List[str] = Field(..., description="Auto-generated tags")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Tagging confidence")
    alternatives: List[str] = Field(..., description="Alternative tag suggestions")


class AIHealthStatus(BaseModel):
    status: str = Field(..., description="Service health status")
    models_loaded: bool = Field(..., description="Whether AI models are loaded")
    test_sentiment: Optional[str] = Field(None, description="Test sentiment result")
    timestamp: float = Field(..., description="Health check timestamp")


# Advanced AI feature schemas
class ContentInsightRequest(BaseModel):
    post_id: int = Field(..., description="Post ID to analyze")


class TrendAnalysis(BaseModel):
    trending_topics: List[TrendingTopic] = Field(..., description="Trending topics")
    analysis_period: str = Field(..., description="Analysis time period")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence")


class InsightResponse(BaseModel):
    """Generic response for various insights"""
    data: Dict[str, Any] = Field(..., description="Insight data")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Insight confidence")


# Error responses
class AIErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


# Analytics and reporting schemas
class UserEngagementMetrics(BaseModel):
    user_id: int = Field(..., description="User ID")
    posts_created: int = Field(..., description="Posts created by user")
    comments_made: int = Field(..., description="Comments made by user")
    likes_received: int = Field(..., description="Likes received")
    shares_received: int = Field(..., description="Shares received")
    avg_engagement_rate: float = Field(..., ge=0.0, le=1.0, description="Average engagement rate")
    content_quality_score: float = Field(..., ge=0.0, le=1.0, description="Content quality score")
    recommendation_accuracy: float = Field(..., ge=0.0, le=1.0, description="Recommendation accuracy")


class ContentPerformanceMetrics(BaseModel):
    post_id: int = Field(..., description="Post ID")
    views: int = Field(..., description="Number of views")
    likes: int = Field(..., description="Number of likes")
    comments: int = Field(..., description="Number of comments")
    shares: int = Field(..., description="Number of shares")
    engagement_rate: float = Field(..., ge=0.0, le=1.0, description="Engagement rate")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score")
    virality_score: float = Field(..., ge=0.0, le=1.0, description="Virality score")


class PlatformAnalytics(BaseModel):
    total_users: int = Field(..., description="Total registered users")
    active_users: int = Field(..., description="Active users (last 30 days)")
    total_posts: int = Field(..., description="Total posts created")
    total_comments: int = Field(..., description="Total comments made")
    avg_sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Average sentiment score")
    top_categories: List[str] = Field(..., description="Most popular content categories")
    engagement_trend: str = Field(..., description="Engagement trend (up/down/stable)")
    ai_accuracy_score: float = Field(..., ge=0.0, le=1.0, description="AI recommendation accuracy")