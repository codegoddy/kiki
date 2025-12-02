"""
Enhanced Recommendation Service
Advanced AI-powered content recommendation system with collaborative and content-based filtering
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import TruncatedSVD
from collections import defaultdict, Counter
import json
import pickle
from pathlib import Path

from app.core.base_service import BaseService
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.recommendation import (
    UserInteraction, UserPreference, ContentEmbedding, RecommendationFeedback,
    SimilarityScore, TrendingContent
)
from app.services.user import UserService
from app.services.post import PostService
from app.services.comment import CommentService
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class EnhancedRecommendationService(BaseService):
    """Enhanced recommendation service with advanced algorithms"""
    
    def __init__(self, db: Session, user_service: UserService, post_service: PostService, 
                 comment_service: CommentService, ai_service: AIService):
        super().__init__()
        self.db = db
        self.user_service = user_service
        self.post_service = post_service
        self.comment_service = comment_service
        self.ai_service = ai_service
        
        # Recommendation algorithms cache
        self.user_item_matrix = None
        self.item_similarity_matrix = None
        self.trending_scores = {}
        self.user_profiles = {}
        
        # Algorithm weights (tunable parameters)
        self.weights = {
            "collaborative": 0.4,  # User-based collaborative filtering
            "content_based": 0.3,  # Content-based filtering
            "trending": 0.2,       # Trending content
            "diversity": 0.1       # Content diversity
        }
    
    async def log_user_interaction(self, user_id: int, post_id: int, 
                                 interaction_type: str, score: float = 1.0,
                                 time_spent: int = 0, scroll_depth: float = 0.0,
                                 session_id: Optional[str] = None) -> bool:
        """Log user interaction for recommendation learning"""
        try:
            interaction = UserInteraction(
                user_id=user_id,
                post_id=post_id,
                interaction_type=interaction_type,
                interaction_score=score,
                session_id=session_id,
                time_spent_seconds=time_spent,
                scroll_depth=scroll_depth
            )
            
            self.db.add(interaction)
            await self._update_user_preferences(user_id, post_id, interaction_type, score)
            await self._update_post_trending_score(post_id)
            
            await asyncio.to_thread(self.db.commit)
            return True
            
        except Exception as e:
            logger.error(f"Error logging user interaction: {e}")
            await asyncio.to_thread(self.db.rollback)
            return False
    
    async def _update_user_preferences(self, user_id: int, post_id: int, 
                                     interaction_type: str, score: float):
        """Update user preferences based on interaction"""
        try:
            post = await self.post_service.get_by_id(post_id)
            if not post:
                return
            
            # Extract preferences from post
            preferences_to_update = []
            
            # Category preference
            if post.categories:
                for category in post.categories:
                    preferences_to_update.append(("category", category.name, interaction_type))
            
            # Author preference
            preferences_to_update.append(("author", post.author.username, interaction_type))
            
            # Content-based preferences (from AI analysis)
            classification = await self.ai_service.classify_content(post.title, post.content)
            if "topics" in classification:
                for topic in classification["topics"][:3]:  # Top 3 topics
                    preferences_to_update.append(("topic", topic["topic"], interaction_type))
            
            # Sentiment preference
            if "sentiment" in classification:
                sentiment = classification["sentiment"]["label"]
                preferences_to_update.append(("sentiment", sentiment, interaction_type))
            
            # Update preferences
            for pref_type, pref_value, interaction in preferences_to_update:
                await self._update_single_preference(user_id, pref_type, pref_value, interaction, score)
                
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
    
    async def _update_single_preference(self, user_id: int, pref_type: str, 
                                      pref_value: str, interaction: str, score: float):
        """Update a single user preference"""
        try:
            # Find existing preference
            existing_pref = self.db.query(UserPreference).filter(
                and_(
                    UserPreference.user_id == user_id,
                    UserPreference.preference_type == pref_type,
                    UserPreference.preference_value == pref_value,
                    UserPreference.is_active == True
                )
            ).first()
            
            if existing_pref:
                # Update existing preference
                existing_pref.interaction_count += 1
                existing_pref.last_interaction = datetime.utcnow()
                
                if interaction in ["like", "share", "save", "comment"]:
                    existing_pref.positive_interactions += 1
                elif interaction in ["dislike", "report"]:
                    existing_pref.negative_interactions += 1
                
                # Recalculate strength and confidence
                total_interactions = existing_pref.interaction_count
                positive_ratio = existing_pref.positive_interactions / max(total_interactions, 1)
                existing_pref.strength = min(existing_pref.strength + score * 0.1, 1.0)
                existing_pref.confidence = min(total_interactions / 10.0, 1.0)
                
            else:
                # Create new preference
                new_pref = UserPreference(
                    user_id=user_id,
                    preference_type=pref_type,
                    preference_value=pref_value,
                    strength=score * 0.5,
                    confidence=0.1,
                    interaction_count=1,
                    positive_interactions=1 if interaction in ["like", "share", "save", "comment"] else 0,
                    negative_interactions=1 if interaction in ["dislike", "report"] else 0
                )
                self.db.add(new_pref)
                
        except Exception as e:
            logger.error(f"Error updating single preference: {e}")
    
    async def _update_post_trending_score(self, post_id: int):
        """Update trending score for a post"""
        try:
            # Get recent interactions for this post
            recent_interactions = self.db.query(UserInteraction).filter(
                and_(
                    UserInteraction.post_id == post_id,
                    UserInteraction.created_at >= datetime.utcnow() - timedelta(hours=24)
                )
            ).all()
            
            if not recent_interactions:
                return
            
            # Calculate trending metrics
            total_views = sum(1 for i in recent_interactions if i.interaction_type == "view")
            total_likes = sum(1 for i in recent_interactions if i.interaction_type == "like")
            total_shares = sum(1 for i in recent_interactions if i.interaction_type == "share")
            total_comments = sum(1 for i in recent_interactions if i.interaction_type == "comment")
            
            # Calculate velocity (rate of change)
            hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_hour = [i for i in recent_interactions if i.created_at >= hour_ago]
            hour_velocity = len(recent_hour) / max(total_views, 1)
            
            # Calculate trend score
            trend_score = (total_likes * 2 + total_shares * 3 + total_comments * 2) / max(total_views, 1)
            
            # Update or create trending record
            trending = self.db.query(TrendingContent).filter(
                TrendingContent.post_id == post_id
            ).first()
            
            if trending:
                trending.trend_score = trend_score
                trending.velocity = hour_velocity
                trending.views_count = total_views
                trending.likes_count = total_likes
                trending.shares_count = total_shares
                trending.comments_count = total_comments
                trending.last_updated = datetime.utcnow()
            else:
                trending = TrendingContent(
                    post_id=post_id,
                    trend_score=trend_score,
                    velocity=hour_velocity,
                    views_count=total_views,
                    likes_count=total_likes,
                    shares_count=total_shares,
                    comments_count=total_comments
                )
                self.db.add(trending)
                
        except Exception as e:
            logger.error(f"Error updating trending score: {e}")
    
    async def get_personalized_recommendations(self, user_id: int, limit: int = 10,
                                             include_types: List[str] = None) -> List[Dict[str, Any]]:
        """Get personalized recommendations using hybrid approach"""
        try:
            include_types = include_types or ["personalized", "similar", "trending"]
            
            # Get recommendations from different algorithms
            recommendations = []
            
            if "personalized" in include_types:
                personalized = await self._get_collaborative_recommendations(user_id, limit // 2)
                recommendations.extend(personalized)
            
            if "similar" in include_types:
                similar = await self._get_content_based_recommendations(user_id, limit // 2)
                recommendations.extend(similar)
            
            if "trending" in include_types:
                trending = await self._get_trending_recommendations(user_id, limit // 2)
                recommendations.extend(trending)
            
            # Sort and deduplicate
            recommendations = self._merge_and_deduplicate_recommendations(recommendations)
            
            # Apply diversity algorithm
            recommendations = await self._apply_diversity(recommendations, limit)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {e}")
            return []
    
    async def _get_collaborative_recommendations(self, user_id: int, limit: int) -> List[Dict[str, Any]]:
        """Get recommendations using collaborative filtering"""
        try:
            # Get user's interaction history
            user_interactions = self.db.query(UserInteraction).filter(
                UserInteraction.user_id == user_id
            ).all()
            
            if not user_interactions:
                return await self._get_cold_start_recommendations(limit)
            
            # Find similar users based on interactions
            similar_users = await self._find_similar_users(user_id, user_interactions)
            
            # Get recommendations from similar users
            recommendations = []
            for similar_user_id, similarity_score in similar_users[:10]:
                similar_user_posts = self.db.query(UserInteraction).filter(
                    and_(
                        UserInteraction.user_id == similar_user_id,
                        UserInteraction.interaction_type.in_(["like", "share", "save"]),
                        UserInteraction.post_id.notin_([i.post_id for i in user_interactions])
                    )
                ).order_by(desc(UserInteraction.interaction_score)).limit(limit // 2).all()
                
                for interaction in similar_user_posts:
                    post = await self.post_service.get_by_id(interaction.post_id)
                    if post:
                        recommendations.append({
                            "post_id": post.id,
                            "score": interaction.interaction_score * similarity_score * self.weights["collaborative"],
                            "reason": f"Because users like you enjoyed this",
                            "algorithm": "collaborative",
                            "confidence": similarity_score
                        })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in collaborative filtering: {e}")
            return []
    
    async def _get_content_based_recommendations(self, user_id: int, limit: int) -> List[Dict[str, Any]]:
        """Get recommendations using content-based filtering"""
        try:
            # Get user's preferences
            user_prefs = self.db.query(UserPreference).filter(
                and_(
                    UserPreference.user_id == user_id,
                    UserPreference.is_active == True
                )
            ).all()
            
            if not user_prefs:
                return []
            
            # Get posts that match user preferences
            candidate_posts = await self._get_candidate_posts_for_user(user_id, user_prefs)
            
            # Calculate content similarity scores
            recommendations = []
            for post in candidate_posts[:limit * 2]:  # Get more candidates
                similarity_score = await self._calculate_content_similarity(user_id, post)
                if similarity_score > 0.1:
                    recommendations.append({
                        "post_id": post.id,
                        "score": similarity_score * self.weights["content_based"],
                        "reason": "Matches your interests",
                        "algorithm": "content_based",
                        "confidence": similarity_score
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in content-based filtering: {e}")
            return []
    
    async def _get_trending_recommendations(self, user_id: int, limit: int) -> List[Dict[str, Any]]:
        """Get trending content recommendations"""
        try:
            # Get trending posts
            trending_posts = self.db.query(TrendingContent).filter(
                and_(
                    TrendingContent.is_trending == True,
                    TrendingContent.trend_score > 0.1
                )
            ).order_by(desc(TrendingContent.trend_score)).limit(limit * 2).all()
            
            recommendations = []
            for trending in trending_posts:
                post = await self.post_service.get_by_id(trending.post_id)
                if post:
                    # Filter out posts user has already seen
                    user_interactions = self.db.query(UserInteraction).filter(
                        and_(
                            UserInteraction.user_id == user_id,
                            UserInteraction.post_id == post.id
                        )
                    ).first()
                    
                    if not user_interactions:
                        recommendations.append({
                            "post_id": post.id,
                            "score": trending.trend_score * self.weights["trending"],
                            "reason": "Trending now",
                            "algorithm": "trending",
                            "confidence": min(trending.trend_score, 1.0)
                        })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in trending recommendations: {e}")
            return []
    
    async def _find_similar_users(self, user_id: int, user_interactions: List[UserInteraction]) -> List[Tuple[int, float]]:
        """Find users with similar preferences"""
        try:
            # Get posts user has interacted with
            user_posts = [i.post_id for i in user_interactions]
            
            # Find users who have interacted with the same posts
            similar_interactions = self.db.query(UserInteraction).filter(
                and_(
                    UserInteraction.post_id.in_(user_posts),
                    UserInteraction.user_id != user_id,
                    UserInteraction.interaction_type.in_(["like", "share", "save"])
                )
            ).all()
            
            # Calculate similarity scores
            user_post_scores = defaultdict(dict)
            for interaction in similar_interactions:
                user_post_scores[interaction.user_id][interaction.post_id] = interaction.interaction_score
            
            # Calculate cosine similarity
            similarities = []
            user_vector = {post_id: 1.0 for post_id in user_posts}  # User's preference vector
            
            for other_user_id, other_posts in user_post_scores.items():
                # Calculate cosine similarity
                common_posts = set(user_posts) & set(other_posts.keys())
                if len(common_posts) < 2:  # Need at least 2 common posts
                    continue
                
                dot_product = sum(user_vector[post_id] * other_posts[post_id] for post_id in common_posts)
                magnitude_user = np.sqrt(len(user_posts))
                magnitude_other = np.sqrt(len(other_posts))
                
                if magnitude_user > 0 and magnitude_other > 0:
                    similarity = dot_product / (magnitude_user * magnitude_other)
                    similarities.append((other_user_id, similarity))
            
            # Sort by similarity and return top matches
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:20]  # Top 20 similar users
            
        except Exception as e:
            logger.error(f"Error finding similar users: {e}")
            return []
    
    async def _get_candidate_posts_for_user(self, user_id: int, user_prefs: List[UserPreference]) -> List[Post]:
        """Get candidate posts that match user preferences"""
        try:
            # Build query based on preferences
            query = self.db.query(Post).filter(Post.author_id != user_id)  # Exclude own posts
            
            # Add preference filters
            category_names = [p.preference_value for p in user_prefs if p.preference_type == "category" and p.strength > 0.3]
            author_usernames = [p.preference_value for p in user_prefs if p.preference_type == "author" and p.strength > 0.3]
            
            # Filter by categories
            if category_names:
                query = query.join(Post.categories).filter(
                    func.lower(Category.name).in_([name.lower() for name in category_names])
                )
            
            # Filter by authors user follows
            if author_usernames:
                query = query.join(User).filter(
                    func.lower(User.username).in_([name.lower() for name in author_usernames])
                )
            
            # Get posts from last 30 days to ensure recency
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            query = query.filter(Post.created_at >= thirty_days_ago)
            
            # Order by creation date (newer first) and limit
            candidate_posts = query.order_by(desc(Post.created_at)).limit(100).all()
            
            return candidate_posts
            
        except Exception as e:
            logger.error(f"Error getting candidate posts: {e}")
            return []
    
    async def _calculate_content_similarity(self, user_id: int, post: Post) -> float:
        """Calculate content similarity score for a user and post"""
        try:
            # Get user preferences for content-based scoring
            user_prefs = self.db.query(UserPreference).filter(
                and_(
                    UserPreference.user_id == user_id,
                    UserPreference.is_active == True
                )
            ).all()
            
            similarity_score = 0.0
            pref_weights = {}
            
            # Normalize preference weights
            total_strength = sum(p.strength for p in user_prefs)
            if total_strength == 0:
                return 0.0
            
            for pref in user_prefs:
                pref_weights[(pref.preference_type, pref.preference_value)] = pref.strength / total_strength
            
            # Category similarity
            if post.categories:
                for category in post.categories:
                    if ("category", category.name) in pref_weights:
                        similarity_score += pref_weights[("category", category.name)] * 0.4
            
            # Author similarity
            if ("author", post.author.username) in pref_weights:
                similarity_score += pref_weights[("author", post.author.username)] * 0.3
            
            # Content similarity using AI embeddings
            user_posts = self.db.query(Post).filter(Post.author_id == user_id).limit(5).all()
            if user_posts:
                content_similarity = await self.ai_service.find_similar_content(post.id, limit=5)
                if content_similarity:
                    avg_similarity = np.mean([s.similarity_score for s in content_similarity])
                    similarity_score += avg_similarity * 0.3
            
            return min(similarity_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating content similarity: {e}")
            return 0.0
    
    async def _get_cold_start_recommendations(self, limit: int) -> List[Dict[str, Any]]:
        """Get recommendations for new users (cold start problem)"""
        try:
            # Get popular posts from the last week
            week_ago = datetime.utcnow() - timedelta(days=7)
            
            popular_posts = self.db.query(Post).filter(
                Post.created_at >= week_ago
            ).order_by(desc(Post.created_at)).limit(limit).all()
            
            recommendations = []
            for post in popular_posts:
                recommendations.append({
                    "post_id": post.id,
                    "score": 0.5,  # Default score for new users
                    "reason": "Popular content to get you started",
                    "algorithm": "cold_start",
                    "confidence": 0.5
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting cold start recommendations: {e}")
            return []
    
    def _merge_and_deduplicate_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge recommendations from different algorithms and deduplicate"""
        try:
            # Group by post_id
            post_recommendations = defaultdict(list)
            for rec in recommendations:
                post_recommendations[rec["post_id"]].append(rec)
            
            # Merge recommendations for the same post
            merged_recommendations = []
            for post_id, recs in post_recommendations.items():
                total_score = sum(r["score"] for r in recs)
                algorithms = [r["algorithm"] for r in recs]
                reasons = [r["reason"] for r in recs]
                confidences = [r["confidence"] for r in recs]
                
                merged_recommendations.append({
                    "post_id": post_id,
                    "score": total_score,
                    "algorithm": "+".join(set(algorithms)),
                    "reason": "; ".join(set(reasons)),
                    "confidence": np.mean(confidences)
                })
            
            # Sort by score
            merged_recommendations.sort(key=lambda x: x["score"], reverse=True)
            return merged_recommendations
            
        except Exception as e:
            logger.error(f"Error merging recommendations: {e}")
            return recommendations
    
    async def _apply_diversity(self, recommendations: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Apply diversity to recommendations to avoid filter bubbles"""
        try:
            if len(recommendations) <= limit:
                return recommendations
            
            diverse_recommendations = []
            used_authors = set()
            used_categories = set()
            
            # Sort by score first
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            
            for rec in recommendations:
                post = await self.post_service.get_by_id(rec["post_id"])
                if not post:
                    continue
                
                # Check diversity constraints
                author_id = post.author_id
                post_categories = [cat.name for cat in post.categories] if post.categories else []
                
                # Allow up to 3 recommendations from same author
                author_count = sum(1 for r in diverse_recommendations if 
                                 any(d["post_id"] == r["post_id"] and 
                                     self.db.query(Post).get(r["post_id"]).author_id == author_id 
                                     for d in diverse_recommendations))
                
                if author_count < 3:
                    diverse_recommendations.append(rec)
                    
                    if len(diverse_recommendations) >= limit:
                        break
            
            # If we don't have enough recommendations, add the highest scoring ones
            if len(diverse_recommendations) < limit:
                remaining = [r for r in recommendations if r not in diverse_recommendations]
                diverse_recommendations.extend(remaining[:limit - len(diverse_recommendations)])
            
            return diverse_recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error applying diversity: {e}")
            return recommendations[:limit]
    
    async def get_similar_content(self, post_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get content similar to a given post"""
        try:
            # Check if we have pre-computed similarities
            similarities = self.db.query(SimilarityScore).filter(
                and_(
                    SimilarityScore.source_post_id == post_id,
                    SimilarityScore.similarity_score > 0.1,
                    SimilarityScore.is_active == True
                )
            ).order_by(desc(SimilarityScore.similarity_score)).limit(limit).all()
            
            if similarities:
                # Return pre-computed similarities
                return [{
                    "post_id": sim.target_post_id,
                    "similarity_score": sim.similarity_score,
                    "algorithm": sim.algorithm,
                    "confidence": sim.confidence
                } for sim in similarities]
            
            # Compute similarities on-the-fly
            ai_similarities = await self.ai_service.find_similar_content(post_id, limit)
            
            # Store computed similarities for future use
            for sim in ai_similarities:
                similarity_record = SimilarityScore(
                    source_post_id=post_id,
                    target_post_id=sim.post_id,
                    similarity_score=sim.similarity_score,
                    algorithm="ai_embeddings",
                    confidence=0.8
                )
                self.db.add(similarity_record)
            
            await asyncio.to_thread(self.db.commit)
            
            return [{
                "post_id": sim.post_id,
                "similarity_score": sim.similarity_score,
                "algorithm": "ai_embeddings",
                "confidence": 0.8
            } for sim in ai_similarities]
            
        except Exception as e:
            logger.error(f"Error getting similar content: {e}")
            return []
    
    async def update_recommendation_feedback(self, user_id: int, post_id: int, 
                                           feedback_type: str, feedback_score: float = 0.0,
                                           recommendation_type: str = "personalized") -> bool:
        """Update recommendation feedback for algorithm improvement"""
        try:
            feedback = RecommendationFeedback(
                user_id=user_id,
                post_id=post_id,
                recommendation_type=recommendation_type,
                feedback_type=feedback_type,
                feedback_score=feedback_score
            )
            
            self.db.add(feedback)
            await asyncio.to_thread(self.db.commit)
            return True
            
        except Exception as e:
            logger.error(f"Error updating recommendation feedback: {e}")
            await asyncio.to_thread(self.db.rollback)
            return False