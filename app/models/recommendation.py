"""
Recommendation Models
Models for tracking user preferences, content interactions, and recommendation feedback
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel


class UserInteraction(BaseModel):
    """Track user interactions with content for recommendation modeling"""
    
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    
    # Interaction types
    interaction_type = Column(String(50), nullable=False)  # view, like, share, comment, save, click
    interaction_score = Column(Float, default=1.0)  # Weighted score for the interaction
    
    # Context
    session_id = Column(String(255), nullable=True)  # For anonymous sessions
    user_agent = Column(Text, nullable=True)  # Browser/device info
    referrer = Column(Text, nullable=True)  # How user found the content
    
    # Engagement metrics
    time_spent_seconds = Column(Integer, default=0)  # Time spent on content
    scroll_depth = Column(Float, default=0.0)  # How far user scrolled (0-1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interactions")
    post = relationship("Post", back_populates="interactions")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_interaction_user_type', 'user_id', 'interaction_type'),
        Index('idx_user_interaction_post_type', 'post_id', 'interaction_type'),
        Index('idx_user_interaction_created', 'created_at'),
        Index('idx_user_interaction_score', 'interaction_score'),
    )


class UserPreference(BaseModel):
    """Track user preferences for content categories and topics"""
    
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Preference dimensions
    preference_type = Column(String(50), nullable=False)  # category, topic, keyword, author
    preference_value = Column(String(255), nullable=False)  # The actual preference value
    
    # Preference scores
    strength = Column(Float, default=0.0)  # Strength of preference (0-1)
    confidence = Column(Float, default=0.0)  # Confidence in this preference (0-1)
    
    # Usage statistics
    interaction_count = Column(Integer, default=0)  # How often user interacts with this preference
    positive_interactions = Column(Integer, default=0)  # Positive interactions (likes, shares)
    negative_interactions = Column(Integer, default=0)  # Negative interactions (dislikes)
    
    # Temporal information
    first_interaction = Column(DateTime(timezone=True), server_default=func.now())
    last_interaction = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    # Unique constraint to prevent duplicates
    __table_args__ = (
        Index('idx_user_preference_unique', 'user_id', 'preference_type', 'preference_value', unique=True),
        Index('idx_user_preference_strength', 'strength'),
        Index('idx_user_preference_confidence', 'confidence'),
    )


class ContentEmbedding(BaseModel):
    """Store content embeddings for similarity calculations"""
    
    __tablename__ = "content_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    
    # Embedding data
    embedding_type = Column(String(50), default="text")  # text, image, combined
    embedding_vector = Column(Text, nullable=False)  # JSON-encoded embedding vector
    
    # Model information
    model_name = Column(String(100), nullable=False)  # Name of the model used
    model_version = Column(String(50), nullable=True)  # Model version
    
    # Statistics
    vector_dimension = Column(Integer, nullable=False)  # Dimension of the embedding
    quality_score = Column(Float, default=0.0)  # Quality of the embedding
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    post = relationship("Post", back_populates="embeddings")
    
    # Indexes
    __table_args__ = (
        Index('idx_content_embedding_post_type', 'post_id', 'embedding_type'),
        Index('idx_content_embedding_quality', 'quality_score'),
    )


class RecommendationFeedback(BaseModel):
    """Track user feedback on recommendations for continuous improvement"""
    
    __tablename__ = "recommendation_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    
    # Recommendation context
    recommendation_type = Column(String(50), nullable=False)  # personalized, similar, trending, cold_start
    algorithm_version = Column(String(50), nullable=True)  # Algorithm version used
    
    # Feedback
    feedback_type = Column(String(50), nullable=False)  # click, like, share, save, dismiss, report
    feedback_score = Column(Float, default=0.0)  # Numeric feedback score (-1 to 1)
    
    # Context
    position_in_list = Column(Integer, nullable=True)  # Position in recommendation list
    recommendation_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    feedback_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Performance metrics
    time_to_feedback = Column(Integer, default=0)  # Seconds between recommendation and feedback
    
    # Relationships
    user = relationship("User", back_populates="recommendation_feedback")
    post = relationship("Post", back_populates="recommendation_feedback")
    
    # Indexes
    __table_args__ = (
        Index('idx_recommendation_feedback_user_type', 'user_id', 'recommendation_type'),
        Index('idx_recommendation_feedback_post', 'post_id'),
        Index('idx_recommendation_feedback_score', 'feedback_score'),
        Index('idx_recommendation_feedback_timestamp', 'feedback_timestamp'),
    )


class SimilarityScore(BaseModel):
    """Pre-computed similarity scores between content for faster recommendations"""
    
    __tablename__ = "similarity_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    source_post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    target_post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    
    # Similarity data
    similarity_type = Column(String(50), default="cosine")  # cosine, jaccard, euclidean, etc.
    similarity_score = Column(Float, nullable=False)  # Similarity score (0-1)
    
    # Model information
    algorithm = Column(String(100), nullable=False)  # Algorithm used (tfidf, bert, etc.)
    parameters = Column(Text, nullable=True)  # JSON-encoded algorithm parameters
    
    # Statistics
    confidence = Column(Float, default=0.0)  # Confidence in this similarity
    validation_count = Column(Integer, default=0)  # How often this similarity is validated
    
    # Timestamps
    computed_at = Column(DateTime(timezone=True), server_default=func.now())
    last_validated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    source_post = relationship("Post", foreign_keys=[source_post_id], back_populates="source_similarities")
    target_post = relationship("Post", foreign_keys=[target_post_id], back_populates="target_similarities")
    
    # Indexes
    __table_args__ = (
        Index('idx_similarity_scores_source_target', 'source_post_id', 'target_post_id'),
        Index('idx_similarity_scores_score', 'similarity_score'),
        Index('idx_similarity_scores_active', 'is_active'),
    )


class TrendingContent(BaseModel):
    """Track trending content for recommendation algorithms"""
    
    __tablename__ = "trending_content"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    
    # Trending metrics
    trend_score = Column(Float, nullable=False)  # Overall trending score
    velocity = Column(Float, default=0.0)  # Rate of change in engagement
    decay_factor = Column(Float, default=0.95)  # How quickly trend decays
    
    # Engagement metrics
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    
    # Time windows
    hour_score = Column(Float, default=0.0)  # Score for last hour
    day_score = Column(Float, default=0.0)  # Score for last day
    week_score = Column(Float, default=0.0)  # Score for last week
    
    # Metadata
    trend_category = Column(String(100), nullable=True)  # Category of trend
    tags = Column(Text, nullable=True)  # JSON-encoded trend tags
    
    # Timestamps
    first_detected = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_trending = Column(Boolean, default=True)
    
    # Relationships
    post = relationship("Post", back_populates="trending_data")
    
    # Indexes
    __table_args__ = (
        Index('idx_trending_content_score', 'trend_score'),
        Index('idx_trending_content_velocity', 'velocity'),
        Index('idx_trending_content_active', 'is_trending'),
        Index('idx_trending_content_detected', 'first_detected'),
    )