"""
Recommendation Schemas
Pydantic models for recommendation API endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class InteractionType(str, Enum):
    VIEW = "view"
    LIKE = "like"
    SHARE = "share"
    COMMENT = "comment"
    SAVE = "save"
    CLICK = "click"
    DISMISS = "dismiss"
    REPORT = "report"


class FeedbackType(str, Enum):
    CLICK = "click"
    LIKE = "like"
    SHARE = "share"
    SAVE = "save"
    DISMISS = "dismiss"
    REPORT = "report"


class RecommendationType(str, Enum):
    PERSONALIZED = "personalized"
    SIMILAR = "similar"
    TRENDING = "trending"
    COLD_START = "cold_start"
    EXPLORE = "explore"


class InteractionLogRequest(BaseModel):
    user_id: int = Field(..., description="User ID who performed the interaction")
    post_id: int = Field(..., description="Post ID that was interacted with")
    interaction_type: InteractionType = Field(..., description="Type of interaction")
    score: float = Field(default=1.0, ge=0.0, le=1.0, description="Interaction score/weight")
    time_spent_seconds: int = Field(default=0, ge=0, description="Time spent on content")
    scroll_depth: float = Field(default=0.0, ge=0.0, le=1.0, description="Scroll depth (0-1)")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")


class InteractionLogResponse(BaseModel):
    success: bool = Field(..., description="Whether the interaction was logged successfully")
    message: str = Field(..., description="Response message")
    timestamp: float = Field(..., description="Response timestamp")


class RecommendationRequest(BaseModel):
    user_id: int = Field(..., description="User ID to get recommendations for")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of recommendations")
    include_types: Optional[List[str]] = Field(default=["personalized", "similar", "trending"], 
                                               description="Types of recommendations to include")


class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]] = Field(..., description="List of recommended posts")
    algorithm: str = Field(..., description="Algorithm used for recommendations")
    generated_at: float = Field(..., description="Generation timestamp")
    total_count: int = Field(..., description="Total number of recommendations")


class SimilarContentRequest(BaseModel):
    post_id: int = Field(..., description="Post ID to find similar content for")
    limit: int = Field(default=5, ge=1, le=20, description="Maximum number of similar posts")


class SimilarContentResponse(BaseModel):
    similar_posts: List[Dict[str, Any]] = Field(..., description="List of similar posts")
    source_post_id: int = Field(..., description="Source post ID")
    generated_at: float = Field(..., description="Generation timestamp")


class PreferenceUpdateRequest(BaseModel):
    user_id: int = Field(..., description="User ID")
    preference_type: str = Field(..., description="Type of preference (category, topic, author, etc.)")
    preference_value: str = Field(..., description="Preference value")
    action: str = Field(..., description="Action (add, remove, update)")
    strength: Optional[float] = Field(None, ge=0.0, le=1.0, description="Preference strength")


class PreferenceUpdateResponse(BaseModel):
    success: bool = Field(..., description="Whether the preference was updated")
    message: str = Field(..., description="Response message")
    preference_id: Optional[int] = Field(None, description="Updated preference ID")


class FeedbackRequest(BaseModel):
    user_id: int = Field(..., description="User ID who is providing feedback")
    post_id: int = Field(..., description="Post ID that was recommended")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    feedback_score: float = Field(default=0.0, ge=-1.0, le=1.0, description="Feedback score")
    recommendation_type: RecommendationType = Field(default=RecommendationType.PERSONALIZED, 
                                                   description="Type of recommendation")


class FeedbackResponse(BaseModel):
    success: bool = Field(..., description="Whether feedback was recorded")
    message: str = Field(..., description="Response message")
    timestamp: float = Field(..., description="Response timestamp")


class TrendingRequest(BaseModel):
    limit: int = Field(default=10, ge=1, le=50, description="Number of trending posts")
    timeframe: str = Field(default="day", description="Time period (hour, day, or week)")
    category: Optional[str] = Field(None, description="Category filter")


class TrendingResponse(BaseModel):
    trending_posts: List[Dict[str, Any]] = Field(..., description="List of trending posts")
    timeframe: str = Field(..., description="Analysis time period")
    generated_at: float = Field(..., description="Generation timestamp")
    total_count: int = Field(..., description="Total number of trending posts")


class AnalyticsRequest(BaseModel):
    user_id: int = Field(..., description="User ID to analyze")
    days: int = Field(default=30, ge=1, le=365, description="Analysis period in days")


class AnalyticsResponse(BaseModel):
    user_id: int = Field(..., description="Analyzed user ID")
    analysis_period_days: int = Field(..., description="Analysis period length")
    total_interactions: int = Field(..., description="Total user interactions")
    interaction_types: Dict[str, int] = Field(..., description="Breakdown by interaction type")
    engagement_rate: float = Field(..., ge=0.0, le=1.0, description="User engagement rate")
    top_preferences: List[Dict[str, Any]] = Field(..., description="User's top preferences")
    recommendation_accuracy: float = Field(..., ge=0.0, le=1.0, description="Recommendation accuracy")
    generated_at: float = Field(..., description="Generation timestamp")


class UserPreference(BaseModel):
    id: int = Field(..., description="Preference ID")
    type: str = Field(..., description="Preference type")
    value: str = Field(..., description="Preference value")
    strength: float = Field(..., ge=0.0, le=1.0, description="Preference strength")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in preference")
    interaction_count: int = Field(..., description="Number of interactions")
    positive_interactions: int = Field(..., description="Positive interactions")
    negative_interactions: int = Field(..., description="Negative interactions")
    last_interaction: Optional[str] = Field(None, description="Last interaction timestamp")


class UserPreferenceResponse(BaseModel):
    user_id: int = Field(..., description="User ID")
    total_preferences: int = Field(..., description="Total number of preferences")
    preferences: List[UserPreference] = Field(..., description="List of user preferences")
    generated_at: float = Field(..., description="Generation timestamp")


class ExplorationRequest(BaseModel):
    user_id: int = Field(..., description="User ID for exploration")
    limit: int = Field(default=10, ge=1, le=20, description="Number of exploration items")
    exclude_categories: Optional[List[str]] = Field(None, description="Categories to exclude")
    exclude_authors: Optional[List[str]] = Field(None, description="Authors to exclude")


class ExplorationResponse(BaseModel):
    user_id: int = Field(..., description="User ID")
    exploration_recommendations: List[Dict[str, Any]] = Field(..., description="Exploration recommendations")
    strategy: str = Field(..., description="Exploration strategy used")
    generated_at: float = Field(..., description="Generation timestamp")


class ColdStartRequest(BaseModel):
    user_id: int = Field(..., description="New user ID")
    interests: Optional[List[str]] = Field(None, description="User-provided initial interests")
    limit: int = Field(default=10, ge=1, le=20, description="Number of recommendations")


class ColdStartResponse(BaseModel):
    user_id: int = Field(..., description="User ID")
    cold_start_recommendations: List[Dict[str, Any]] = Field(..., description="Cold start recommendations")
    strategy: str = Field(..., description="Strategy used")
    interests_provided: bool = Field(..., description="Whether interests were provided")
    generated_at: float = Field(..., description="Generation timestamp")


class RecommendationHealth(BaseModel):
    status: str = Field(..., description="Service health status")
    timestamp: float = Field(..., description="Health check timestamp")
    algorithms: Dict[str, bool] = Field(..., description="Algorithm status")
    database_connection: bool = Field(..., description="Database connectivity")
    ai_service: bool = Field(..., description="AI service availability")


class BatchRecommendationRequest(BaseModel):
    user_ids: List[int] = Field(..., description="List of user IDs")
    limit: int = Field(default=10, ge=1, le=50, description="Recommendations per user")
    include_types: Optional[List[str]] = Field(default=["personalized", "trending"], 
                                               description="Types of recommendations")


class BatchRecommendationResponse(BaseModel):
    batch_id: str = Field(..., description="Batch processing ID")
    status: str = Field(..., description="Batch status")
    total_users: int = Field(..., description="Total users in batch")
    completed_users: int = Field(..., description="Completed users")
    results: Dict[int, List[Dict[str, Any]]] = Field(..., description="Recommendations per user")
    generated_at: float = Field(..., description="Generation timestamp")


class RecommendationInsight(BaseModel):
    user_id: int = Field(..., description="User ID")
    insight_type: str = Field(..., description="Type of insight")
    description: str = Field(..., description="Insight description")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Insight confidence")
    supporting_data: Dict[str, Any] = Field(..., description="Data supporting the insight")
    generated_at: float = Field(..., description="Generation timestamp")


class DiversityMetrics(BaseModel):
    author_diversity: float = Field(..., ge=0.0, le=1.0, description="Author diversity score")
    category_diversity: float = Field(..., ge=0.0, le=1.0, description="Category diversity score")
    topic_diversity: float = Field(..., ge=0.0, le=1.0, description="Topic diversity score")
    novelty_score: float = Field(..., ge=0.0, le=1.0, description="Content novelty score")
    serendipity_score: float = Field(..., ge=0.0, le=1.0, description="Serendipity score")


class RecommendationPerformance(BaseModel):
    algorithm: str = Field(..., description="Algorithm name")
    precision: float = Field(..., ge=0.0, le=1.0, description="Precision score")
    recall: float = Field(..., ge=0.0, le=1.0, description="Recall score")
    f1_score: float = Field(..., ge=0.0, le=1.0, description="F1 score")
    click_through_rate: float = Field(..., ge=0.0, le=1.0, description="Click-through rate")
    conversion_rate: float = Field(..., ge=0.0, le=1.0, description="Conversion rate")
    diversity_metrics: DiversityMetrics = Field(..., description="Diversity metrics")


class RecommendationError(BaseModel):
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    user_id: Optional[int] = Field(None, description="User ID if applicable")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")