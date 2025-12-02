"""
Recommendation Background Tasks
Handles batch processing and periodic updates for recommendation algorithms
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from app.core.base_service import BaseService
from app.models.user import User
from app.models.post import Post
from app.models.recommendation import (
    UserInteraction, UserPreference, ContentEmbedding, SimilarityScore, 
    TrendingContent, RecommendationFeedback
)
from app.services.recommendation_service import EnhancedRecommendationService
from app.services.ai_service import AIService
from app.services.user import UserService
from app.services.post import PostService
from app.services.comment import CommentService

logger = logging.getLogger(__name__)


class RecommendationBackgroundTaskManager(BaseService):
    """Manages background tasks for recommendation system"""
    
    def __init__(self, db: Session, recommendation_service: EnhancedRecommendationService,
                 ai_service: AIService, user_service: UserService, post_service: PostService,
                 comment_service: CommentService):
        super().__init__()
        self.db = db
        self.recommendation_service = recommendation_service
        self.ai_service = ai_service
        self.user_service = user_service
        self.post_service = post_service
        self.comment_service = comment_service
        
        # Task configuration
        self.tasks_config = {
            "content_analysis": {"interval": 300, "enabled": True},  # 5 minutes
            "preference_update": {"interval": 1800, "enabled": True},  # 30 minutes
            "similarity_calculation": {"interval": 3600, "enabled": True},  # 1 hour
            "trending_update": {"interval": 600, "enabled": True},  # 10 minutes
            "model_training": {"interval": 86400, "enabled": True},  # 24 hours
            "feedback_analysis": {"interval": 7200, "enabled": True},  # 2 hours
            "cleanup_old_data": {"interval": 604800, "enabled": True}  # 1 week
        }
        
        # Task tracking
        self.running_tasks = {}
        self.task_status = {}
    
    async def start_all_tasks(self):
        """Start all background tasks"""
        logger.info("Starting recommendation background tasks")
        
        for task_name, config in self.tasks_config.items():
            if config["enabled"]:
                try:
                    task = asyncio.create_task(self._run_periodic_task(task_name))
                    self.running_tasks[task_name] = task
                    logger.info(f"Started background task: {task_name}")
                except Exception as e:
                    logger.error(f"Failed to start task {task_name}: {e}")
    
    async def stop_all_tasks(self):
        """Stop all background tasks"""
        logger.info("Stopping recommendation background tasks")
        
        for task_name, task in self.running_tasks.items():
            try:
                task.cancel()
                logger.info(f"Stopped background task: {task_name}")
            except Exception as e:
                logger.error(f"Error stopping task {task_name}: {e}")
        
        # Wait for tasks to complete
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
        
        self.running_tasks.clear()
    
    async def _run_periodic_task(self, task_name: str):
        """Run a task periodically based on its configuration"""
        config = self.tasks_config[task_name]
        interval = config["interval"]
        
        while True:
            try:
                start_time = datetime.utcnow()
                logger.info(f"Starting {task_name} task")
                
                # Execute the specific task
                if task_name == "content_analysis":
                    await self._batch_analyze_content()
                elif task_name == "preference_update":
                    await self._update_user_preferences()
                elif task_name == "similarity_calculation":
                    await self._calculate_content_similarities()
                elif task_name == "trending_update":
                    await self._update_trending_scores()
                elif task_name == "model_training":
                    await self._train_recommendation_models()
                elif task_name == "feedback_analysis":
                    await self._analyze_feedback_data()
                elif task_name == "cleanup_old_data":
                    await self._cleanup_old_data()
                
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                self.task_status[task_name] = {
                    "last_run": start_time,
                    "execution_time": execution_time,
                    "status": "success"
                }
                
                logger.info(f"Completed {task_name} task in {execution_time:.2f}s")
                
                # Wait for the next interval
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                logger.info(f"Task {task_name} was cancelled")
                break
            except Exception as e:
                logger.error(f"Error in {task_name} task: {e}")
                self.task_status[task_name] = {
                    "last_run": datetime.utcnow(),
                    "error": str(e),
                    "status": "failed"
                }
                
                # Wait before retrying
                await asyncio.sleep(min(interval, 300))  # Max 5 minutes retry
    
    async def _batch_analyze_content(self):
        """Analyze newly created or updated content"""
        try:
            # Get posts created or updated in the last hour
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            posts_to_analyze = self.db.query(Post).filter(
                Post.created_at >= one_hour_ago
            ).limit(50).all()  # Limit batch size
            
            if not posts_to_analyze:
                return
            
            logger.info(f"Analyzing {len(posts_to_analyze)} posts")
            
            for post in posts_to_analyze:
                try:
                    # Generate content embeddings
                    await self._generate_content_embedding(post)
                    
                    # Update similarity scores
                    await self._update_post_similarities(post.id)
                    
                    # Analyze content for recommendations
                    await self._analyze_content_for_recommendations(post)
                    
                except Exception as e:
                    logger.error(f"Error analyzing post {post.id}: {e}")
            
            await asyncio.to_thread(self.db.commit)
            
        except Exception as e:
            logger.error(f"Error in batch content analysis: {e}")
            await asyncio.to_thread(self.db.rollback)
    
    async def _generate_content_embedding(self, post: Post):
        """Generate and store content embeddings"""
        try:
            # Check if embedding already exists
            existing_embedding = self.db.query(ContentEmbedding).filter(
                and_(
                    ContentEmbedding.post_id == post.id,
                    ContentEmbedding.embedding_type == "text",
                    ContentEmbedding.is_active == True
                )
            ).first()
            
            if existing_embedding:
                return  # Skip if already exists
            
            # Generate embedding using AI service
            full_text = f"{post.title} {post.content}"
            embeddings = await self.ai_service.get_content_embeddings([full_text])
            
            if len(embeddings) > 0:
                # Store embedding
                embedding_record = ContentEmbedding(
                    post_id=post.id,
                    embedding_type="text",
                    embedding_vector=np.array(embeddings[0]).tolist(),  # Convert to list for JSON
                    model_name="all-MiniLM-L6-v2",
                    vector_dimension=len(embeddings[0]),
                    quality_score=0.8  # Placeholder score
                )
                
                self.db.add(embedding_record)
                
        except Exception as e:
            logger.error(f"Error generating embedding for post {post.id}: {e}")
    
    async def _update_post_similarities(self, post_id: int):
        """Update similarity scores for a post"""
        try:
            # Get the post
            post = await self.post_service.get_by_id(post_id)
            if not post:
                return
            
            # Find similar posts using AI service
            similar_posts = await self.ai_service.find_similar_content(post_id, limit=10)
            
            for similar_post in similar_posts:
                # Store similarity score
                similarity_record = SimilarityScore(
                    source_post_id=post_id,
                    target_post_id=similar_post.post_id,
                    similarity_score=similar_post.similarity_score,
                    algorithm="ai_embeddings",
                    confidence=0.8
                )
                self.db.add(similarity_record)
                
        except Exception as e:
            logger.error(f"Error updating similarities for post {post_id}: {e}")
    
    async def _analyze_content_for_recommendations(self, post: Post):
        """Analyze content to extract features for recommendations"""
        try:
            # Use AI service to classify content
            classification = await self.ai_service.classify_content(post.title, post.content)
            
            # Store analysis results (could be used for enhanced recommendations)
            # This could be expanded to store in a dedicated analysis table
            
            logger.debug(f"Analyzed content for post {post.id}: {classification}")
            
        except Exception as e:
            logger.error(f"Error analyzing content for post {post.id}: {e}")
    
    async def _update_user_preferences(self):
        """Update user preferences based on recent interactions"""
        try:
            # Get users with recent interactions
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            users_with_interactions = self.db.query(UserInteraction.user_id).filter(
                UserInteraction.created_at >= one_hour_ago
            ).distinct().all()
            
            if not users_with_interactions:
                return
            
            logger.info(f"Updating preferences for {len(users_with_interactions)} users")
            
            for (user_id,) in users_with_interactions:
                try:
                    await self._update_single_user_preferences(user_id)
                except Exception as e:
                    logger.error(f"Error updating preferences for user {user_id}: {e}")
            
            await asyncio.to_thread(self.db.commit)
            
        except Exception as e:
            logger.error(f"Error in user preference update: {e}")
            await asyncio.to_thread(self.db.rollback)
    
    async def _update_single_user_preferences(self, user_id: int):
        """Update preferences for a single user"""
        try:
            # Get recent interactions for this user
            recent_interactions = self.db.query(UserInteraction).filter(
                and_(
                    UserInteraction.user_id == user_id,
                    UserInteraction.created_at >= datetime.utcnow() - timedelta(days=7)
                )
            ).all()
            
            if not recent_interactions:
                return
            
            # Group interactions by type and calculate preference updates
            interaction_summary = {}
            for interaction in recent_interactions:
                if interaction.interaction_type not in interaction_summary:
                    interaction_summary[interaction.interaction_type] = []
                interaction_summary[interaction.interaction_type].append(interaction)
            
            # Update preferences based on interaction patterns
            for interaction_type, interactions in interaction_summary.items():
                await self._process_interaction_type_preferences(user_id, interaction_type, interactions)
                
        except Exception as e:
            logger.error(f"Error updating single user preferences for {user_id}: {e}")
    
    async def _process_interaction_type_preferences(self, user_id: int, interaction_type: str, interactions: List[UserInteraction]):
        """Process preferences for a specific interaction type"""
        try:
            # Group by post to avoid double counting
            post_interactions = {}
            for interaction in interactions:
                if interaction.post_id not in post_interactions:
                    post_interactions[interaction.post_id] = []
                post_interactions[interaction.post_id].append(interaction)
            
            # Process each post
            for post_id, post_interactions_list in post_interactions.items():
                post = await self.post_service.get_by_id(post_id)
                if not post:
                    continue
                
                # Calculate aggregate score for this post
                total_score = sum(i.interaction_score for i in post_interactions_list)
                avg_time_spent = np.mean([i.time_spent_seconds for i in post_interactions_list if i.time_spent_seconds > 0])
                
                # Update preferences based on interaction
                if interaction_type in ["like", "share", "save"]:
                    await self._update_preference_for_interaction(user_id, post, total_score, positive=True)
                elif interaction_type in ["dislike", "report"]:
                    await self._update_preference_for_interaction(user_id, post, total_score, positive=False)
                
        except Exception as e:
            logger.error(f"Error processing interaction type {interaction_type} for user {user_id}: {e}")
    
    async def _update_preference_for_interaction(self, user_id: int, post: Post, score: float, positive: bool):
        """Update user preference based on interaction with a post"""
        try:
            # Extract features from post
            features_to_update = []
            
            # Add categories
            if post.categories:
                for category in post.categories:
                    features_to_update.append(("category", category.name))
            
            # Add author
            features_to_update.append(("author", post.author.username))
            
            # Add AI-detected topics (simplified)
            features_to_update.append(("topic", "general"))  # Placeholder
            
            # Update each feature preference
            for pref_type, pref_value in features_to_update:
                existing_pref = self.db.query(UserPreference).filter(
                    and_(
                        UserPreference.user_id == user_id,
                        UserPreference.preference_type == pref_type,
                        UserPreference.preference_value == pref_value,
                        UserPreference.is_active == True
                    )
                ).first()
                
                if existing_pref:
                    if positive:
                        existing_pref.strength = min(existing_pref.strength + score * 0.1, 1.0)
                        existing_pref.positive_interactions += 1
                    else:
                        existing_pref.strength = max(existing_pref.strength - score * 0.1, 0.0)
                        existing_pref.negative_interactions += 1
                    
                    existing_pref.interaction_count += 1
                    existing_pref.last_interaction = datetime.utcnow()
                    
                else:
                    # Create new preference
                    new_pref = UserPreference(
                        user_id=user_id,
                        preference_type=pref_type,
                        preference_value=pref_value,
                        strength=score * 0.5 if positive else 0.1,
                        confidence=0.1,
                        interaction_count=1,
                        positive_interactions=1 if positive else 0,
                        negative_interactions=0 if positive else 1
                    )
                    self.db.add(new_pref)
                    
        except Exception as e:
            logger.error(f"Error updating preference for interaction: {e}")
    
    async def _calculate_content_similarities(self):
        """Calculate content similarities for recommendation improvements"""
        try:
            # Get posts that need similarity updates
            posts_needing_similarity = self.db.query(Post).filter(
                Post.created_at >= datetime.utcnow() - timedelta(days=1)
            ).limit(20).all()
            
            if not posts_needing_similarity:
                return
            
            logger.info(f"Calculating similarities for {len(posts_needing_similarity)} posts")
            
            for post in posts_needing_similarity:
                try:
                    await self._update_post_similarities(post.id)
                except Exception as e:
                    logger.error(f"Error calculating similarities for post {post.id}: {e}")
            
            await asyncio.to_thread(self.db.commit)
            
        except Exception as e:
            logger.error(f"Error in similarity calculation: {e}")
            await asyncio.to_thread(self.db.rollback)
    
    async def _update_trending_scores(self):
        """Update trending scores for all posts"""
        try:
            # Get all posts with recent interactions
            recent_threshold = datetime.utcnow() - timedelta(hours=24)
            
            posts_with_interactions = self.db.query(UserInteraction.post_id).filter(
                UserInteraction.created_at >= recent_threshold
            ).distinct().all()
            
            if not posts_with_interactions:
                return
            
            logger.info(f"Updating trending scores for {len(posts_with_interactions)} posts")
            
            for (post_id,) in posts_with_interactions:
                try:
                    await self.recommendation_service._update_post_trending_score(post_id)
                except Exception as e:
                    logger.error(f"Error updating trending score for post {post_id}: {e}")
            
            await asyncio.to_thread(self.db.commit)
            
        except Exception as e:
            logger.error(f"Error in trending score update: {e}")
            await asyncio.to_thread(self.db.rollback)
    
    async def _train_recommendation_models(self):
        """Train and update recommendation models"""
        try:
            logger.info("Training recommendation models")
            
            # This is a placeholder for more sophisticated model training
            # In a real implementation, you might:
            # 1. Train matrix factorization models
            # 2. Update neural collaborative filtering models
            # 3. Retrain content-based models
            # 4. Update ensemble weights
            
            # For now, just update algorithm weights based on recent performance
            await self._update_algorithm_weights()
            
        except Exception as e:
            logger.error(f"Error in model training: {e}")
    
    async def _update_algorithm_weights(self):
        """Update algorithm weights based on recent performance"""
        try:
            # Analyze recent feedback to adjust algorithm weights
            recent_feedback = self.db.query(RecommendationFeedback).filter(
                RecommendationFeedback.feedback_timestamp >= datetime.utcnow() - timedelta(days=7)
            ).all()
            
            if not recent_feedback:
                return
            
            # Calculate performance metrics for each algorithm
            algorithm_performance = {}
            for feedback in recent_feedback:
                if feedback.feedback_type in ["click", "like", "share"]:
                    alg = feedback.recommendation_type
                    if alg not in algorithm_performance:
                        algorithm_performance[alg] = {"positive": 0, "total": 0}
                    
                    algorithm_performance[alg]["total"] += 1
                    if feedback.feedback_score > 0:
                        algorithm_performance[alg]["positive"] += 1
            
            # Update weights based on performance
            if algorithm_performance:
                total_performance = sum(
                    perf["positive"] / max(perf["total"], 1) 
                    for perf in algorithm_performance.values()
                )
                
                # Adjust weights (simplified approach)
                if total_performance > 0:
                    # This is a simplified weight adjustment
                    # In practice, you'd want more sophisticated weight optimization
                    logger.info(f"Algorithm performance: {algorithm_performance}")
            
        except Exception as e:
            logger.error(f"Error updating algorithm weights: {e}")
    
    async def _analyze_feedback_data(self):
        """Analyze recommendation feedback for insights"""
        try:
            # Get recent feedback
            recent_feedback = self.db.query(RecommendationFeedback).filter(
                RecommendationFeedback.feedback_timestamp >= datetime.utcnow() - timedelta(hours=2)
            ).limit(1000).all()
            
            if not recent_feedback:
                return
            
            # Analyze feedback patterns
            feedback_analysis = {
                "total_feedback": len(recent_feedback),
                "positive_feedback": len([f for f in recent_feedback if f.feedback_score > 0]),
                "negative_feedback": len([f for f in recent_feedback if f.feedback_score < 0]),
                "algorithm_breakdown": {}
            }
            
            for feedback in recent_feedback:
                alg = feedback.recommendation_type
                if alg not in feedback_analysis["algorithm_breakdown"]:
                    feedback_analysis["algorithm_breakdown"][alg] = 0
                feedback_analysis["algorithm_breakdown"][alg] += 1
            
            # Log analysis results
            logger.info(f"Feedback analysis: {feedback_analysis}")
            
            # This could trigger model updates, weight adjustments, etc.
            
        except Exception as e:
            logger.error(f"Error analyzing feedback data: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old recommendation data to maintain performance"""
        try:
            logger.info("Cleaning up old recommendation data")
            
            # Clean up old interactions (older than 90 days)
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            
            old_interactions = self.db.query(UserInteraction).filter(
                UserInteraction.created_at < cutoff_date
            ).count()
            
            if old_interactions > 0:
                self.db.query(UserInteraction).filter(
                    UserInteraction.created_at < cutoff_date
                ).delete()
                logger.info(f"Deleted {old_interactions} old interactions")
            
            # Clean up old similarity scores (keep only recent and high-confidence ones)
            similarity_cutoff = datetime.utcnow() - timedelta(days=30)
            
            old_similarities = self.db.query(SimilarityScore).filter(
                and_(
                    SimilarityScore.computed_at < similarity_cutoff,
                    SimilarityScore.confidence < 0.5
                )
            ).count()
            
            if old_similarities > 0:
                self.db.query(SimilarityScore).filter(
                    and_(
                        SimilarityScore.computed_at < similarity_cutoff,
                        SimilarityScore.confidence < 0.5
                    )
                ).delete()
                logger.info(f"Deleted {old_similarities} old similarity scores")
            
            # Clean up inactive preferences with no recent interactions
            inactive_cutoff = datetime.utcnow() - timedelta(days=60)
            
            inactive_preferences = self.db.query(UserPreference).filter(
                and_(
                    UserPreference.last_interaction < inactive_cutoff,
                    UserPreference.is_active == True
                )
            ).count()
            
            if inactive_preferences > 0:
                self.db.query(UserPreference).filter(
                    and_(
                        UserPreference.last_interaction < inactive_cutoff,
                        UserPreference.is_active == True
                    )
                ).update({"is_active": False})
                logger.info(f"Deactivated {inactive_preferences} inactive preferences")
            
            await asyncio.to_thread(self.db.commit)
            
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
            await asyncio.to_thread(self.db.rollback)
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get status of all background tasks"""
        return {
            "running_tasks": list(self.running_tasks.keys()),
            "task_status": self.task_status,
            "config": self.tasks_config
        }


# Factory function
async def create_recommendation_background_task_manager(
    db: Session,
    recommendation_service: EnhancedRecommendationService,
    ai_service: AIService,
    user_service: UserService,
    post_service: PostService,
    comment_service: CommentService
) -> RecommendationBackgroundTaskManager:
    """Factory function to create background task manager"""
    return RecommendationBackgroundTaskManager(
        db=db,
        recommendation_service=recommendation_service,
        ai_service=ai_service,
        user_service=user_service,
        post_service=post_service,
        comment_service=comment_service
    )