"""
AI Background Tasks
Handles ML model training, content analysis, and scheduled tasks
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from app.core.background_tasks import BaseBackgroundTask
from app.services.ai_service import AIService, create_ai_service
from app.services.user import UserService
from app.services.post import PostService
from app.services.comment import CommentService
from app.models.post import Post
from app.models.user import User

logger = logging.getLogger(__name__)


class ContentAnalysisTask(BaseBackgroundTask):
    """Background task for analyzing new content"""
    
    def __init__(self, ai_service: AIService, post_service: PostService):
        super().__init__(name="content_analysis", interval_seconds=300)  # Run every 5 minutes
        self.ai_service = ai_service
        self.post_service = post_service
        self.last_checked = datetime.utcnow()
    
    async def execute(self):
        """Execute content analysis for unanalyzed posts"""
        try:
            logger.info("Starting content analysis task...")
            
            # Get posts that haven't been analyzed yet
            # This would typically filter by a "needs_analysis" flag in the database
            # For now, we'll analyze recent posts
            
            recent_posts = await self._get_recent_posts()
            
            if not recent_posts:
                logger.debug("No new posts to analyze")
                return
            
            # Analyze posts in batches
            batch_size = 10
            for i in range(0, len(recent_posts), batch_size):
                batch = recent_posts[i:i + batch_size]
                
                try:
                    analysis_results = await self.ai_service.batch_analyze_content(batch)
                    
                    # Save analysis results to database
                    await self._save_analysis_results(analysis_results)
                    
                    logger.info(f"Analyzed batch of {len(batch)} posts")
                    
                except Exception as e:
                    logger.error(f"Error analyzing batch: {e}")
                    continue
            
            self.last_checked = datetime.utcnow()
            logger.info("Content analysis task completed")
            
        except Exception as e:
            logger.error(f"Error in content analysis task: {e}")
    
    async def _get_recent_posts(self) -> List[Post]:
        """Get recent posts that need analysis"""
        try:
            # This would typically query posts from the last day that haven't been analyzed
            # For now, get recent posts from post service
            all_posts = await self.post_service.get_all()
            
            # Filter posts created in the last 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            recent_posts = [
                post for post in all_posts 
                if hasattr(post, 'created_at') and post.created_at and post.created_at > cutoff_time
            ]
            
            return recent_posts
            
        except Exception as e:
            logger.error(f"Error getting recent posts: {e}")
            return []
    
    async def _save_analysis_results(self, results: Dict[int, Dict[str, Any]]):
        """Save analysis results to database"""
        try:
            # This would save results to the database
            # For now, just log the results
            for post_id, analysis in results.items():
                logger.debug(f"Analysis for post {post_id}: {analysis}")
                
                # In a real implementation, you would:
                # 1. Update the post record with analysis results
                # 2. Store sentiment scores, topics, etc.
                # 3. Update recommendation scores
                
        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")


class ModelTrainingTask(BaseBackgroundTask):
    """Background task for training ML models"""
    
    def __init__(self, ai_service: AIService, post_service: PostService, comment_service: CommentService):
        super().__init__(name="model_training", interval_seconds=3600)  # Run every hour
        self.ai_service = ai_service
        self.post_service = post_service
        self.comment_service = comment_service
        self.last_trained = None
    
    async def execute(self):
        """Execute model training and updates"""
        try:
            logger.info("Starting model training task...")
            
            # Check if training is needed
            if self.last_trained and (datetime.utcnow() - self.last_trained).seconds < 3600:
                logger.debug("Training recently completed, skipping")
                return
            
            # Collect training data
            training_data = await self._collect_training_data()
            
            if not training_data:
                logger.debug("No training data available")
                return
            
            # Train/update models
            await self._train_content_similarity_model(training_data)
            await self._train_sentiment_model(training_data)
            await self._update_content_clusters(training_data)
            
            self.last_trained = datetime.utcnow()
            
            # Save model state
            await self._save_model_state()
            
            logger.info("Model training task completed")
            
        except Exception as e:
            logger.error(f"Error in model training task: {e}")
    
    async def _collect_training_data(self) -> Dict[str, List[Any]]:
        """Collect data for training"""
        try:
            # Get posts and comments from the last week
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            
            posts = await self.post_service.get_all()
            comments = await self.comment_service.get_all()
            
            # Filter by date and extract relevant data
            recent_posts = [
                {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "category": getattr(post.category, 'name', None) if hasattr(post, 'category') else None,
                    "likes_count": getattr(post, 'likes_count', 0),
                    "comments_count": getattr(post, 'comments_count', 0),
                    "created_at": post.created_at
                }
                for post in posts
                if hasattr(post, 'created_at') and post.created_at and post.created_at > cutoff_time
            ]
            
            recent_comments = [
                {
                    "id": comment.id,
                    "content": comment.content,
                    "post_id": comment.post_id,
                    "likes_count": getattr(comment, 'likes_count', 0),
                    "created_at": comment.created_at
                }
                for comment in comments
                if hasattr(comment, 'created_at') and comment.created_at and comment.created_at > cutoff_time
            ]
            
            return {
                "posts": recent_posts,
                "comments": recent_comments
            }
            
        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
            return {}
    
    async def _train_content_similarity_model(self, training_data: Dict[str, List[Any]]):
        """Train/update content similarity model"""
        try:
            logger.info("Training content similarity model...")
            
            posts = training_data["posts"]
            if len(posts) < 10:
                logger.debug("Insufficient data for similarity model training")
                return
            
            # Extract text for similarity analysis
            texts = [f"{post['title']} {post['content']}" for post in posts]
            
            # Generate embeddings and similarity matrix
            embeddings = await self.ai_service.get_content_embeddings(texts)
            
            if len(embeddings) > 1:
                from sklearn.metrics.pairwise import cosine_similarity
                similarity_matrix = cosine_similarity(embeddings)
                
                # Save similarity matrix for later use
                self.ai_service.similarity_cache["posts_similarity"] = similarity_matrix
                
                logger.info(f"Content similarity model updated with {len(texts)} documents")
            
        except Exception as e:
            logger.error(f"Error training similarity model: {e}")
    
    async def _train_sentiment_model(self, training_data: Dict[str, List[Any]]):
        """Train/update sentiment analysis model"""
        try:
            logger.info("Training sentiment model...")
            
            # For now, just update the model cache
            # In a real implementation, you would fine-tune models with your data
            logger.debug("Sentiment model training (placeholder)")
            
            # Could implement custom fine-tuning here
            # using training_data for supervised learning
            
        except Exception as e:
            logger.error(f"Error training sentiment model: {e}")
    
    async def _update_content_clusters(self, training_data: Dict[str, List[Any]]):
        """Update content clustering model"""
        try:
            logger.info("Updating content clusters...")
            
            posts = training_data["posts"]
            if len(posts) < 20:
                logger.debug("Insufficient data for clustering")
                return
            
            # Extract text and prepare for clustering
            texts = [f"{post['title']} {post['content']}" for post in posts]
            embeddings = await self.ai_service.get_content_embeddings(texts)
            
            if len(embeddings) > 1:
                from sklearn.cluster import KMeans
                
                # Determine optimal number of clusters
                n_clusters = min(max(len(texts) // 10, 3), 10)
                
                # Perform clustering
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                cluster_labels = kmeans.fit_predict(embeddings)
                
                # Update clusters
                self.ai_service.content_clusters.clear()
                for i, label in enumerate(cluster_labels):
                    if label not in self.ai_service.content_clusters:
                        self.ai_service.content_clusters[label] = []
                    
                    self.ai_service.content_clusters[label].append({
                        "post_id": posts[i]["id"],
                        "text": texts[i],
                        "embedding": embeddings[i].tolist()
                    })
                
                logger.info(f"Content clusters updated with {n_clusters} clusters")
            
        except Exception as e:
            logger.error(f"Error updating content clusters: {e}")
    
    async def _save_model_state(self):
        """Save model state to disk"""
        try:
            # Create models directory if it doesn't exist
            models_dir = Path("models")
            models_dir.mkdir(exist_ok=True)
            
            # Save AI service state
            state = {
                "last_trained": self.last_trained.isoformat() if self.last_trained else None,
                "clusters": self.ai_service.content_clusters,
                "similarity_cache_size": len(self.ai_service.similarity_cache),
                "embeddings_cache_size": len(self.ai_service.embeddings_cache)
            }
            
            # In a real implementation, you would pickle/save actual model weights
            with open(models_dir / "ai_service_state.json", "w") as f:
                json.dump(state, f, default=str)
            
            logger.info("Model state saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving model state: {e}")


class AnalyticsUpdateTask(BaseBackgroundTask):
    """Background task for updating analytics"""
    
    def __init__(self, ai_service: AIService):
        super().__init__(name="analytics_update", interval_seconds=1800)  # Run every 30 minutes
        self.ai_service = ai_service
    
    async def execute(self):
        """Execute analytics updates"""
        try:
            logger.info("Starting analytics update task...")
            
            # Update various analytics metrics
            await self._update_sentiment_analytics()
            await self._update_recommendation_analytics()
            await self._update_moderation_analytics()
            
            logger.info("Analytics update task completed")
            
        except Exception as e:
            logger.error(f"Error in analytics update task: {e}")
    
    async def _update_sentiment_analytics(self):
        """Update sentiment analysis analytics"""
        try:
            # This would calculate and store sentiment analytics
            logger.debug("Updating sentiment analytics")
            
            # Could update:
            # - Overall sentiment distribution
            # - Trend analysis
            # - User sentiment patterns
            
        except Exception as e:
            logger.error(f"Error updating sentiment analytics: {e}")
    
    async def _update_recommendation_analytics(self):
        """Update recommendation system analytics"""
        try:
            # This would calculate recommendation system metrics
            logger.debug("Updating recommendation analytics")
            
            # Could track:
            # - Click-through rates
            # - Recommendation accuracy
            # - User satisfaction metrics
            
        except Exception as e:
            logger.error(f"Error updating recommendation analytics: {e}")
    
    async def _update_moderation_analytics(self):
        """Update content moderation analytics"""
        try:
            # This would calculate moderation metrics
            logger.debug("Updating moderation analytics")
            
            # Could track:
            # - Content approval rates
            # - False positive/negative rates
            # - Moderation workload
            
        except Exception as e:
            logger.error(f"Error updating moderation analytics: {e}")


class UserEngagementAnalysisTask(BaseBackgroundTask):
    """Background task for analyzing user engagement"""
    
    def __init__(self, ai_service: AIService, user_service: UserService, post_service: PostService):
        super().__init__(name="user_engagement_analysis", interval_seconds=3600)  # Run every hour
        self.ai_service = ai_service
        self.user_service = user_service
        self.post_service = post_service
    
    async def execute(self):
        """Execute user engagement analysis"""
        try:
            logger.info("Starting user engagement analysis task...")
            
            # Get all users
            users = await self.user_service.get_all()
            
            # Analyze engagement for each user (in batches)
            batch_size = 50
            for i in range(0, len(users), batch_size):
                batch = users[i:i + batch_size]
                
                try:
                    for user in batch:
                        await self._analyze_user_engagement(user.id)
                    
                    logger.info(f"Analyzed engagement for batch of {len(batch)} users")
                    
                except Exception as e:
                    logger.error(f"Error analyzing user engagement batch: {e}")
                    continue
            
            logger.info("User engagement analysis task completed")
            
        except Exception as e:
            logger.error(f"Error in user engagement analysis task: {e}")
    
    async def _analyze_user_engagement(self, user_id: int):
        """Analyze engagement for a specific user"""
        try:
            # Get user preferences and behavior analysis
            analysis = await self.ai_service.analyze_user_preferences(user_id)
            
            # Store engagement metrics
            # In a real implementation, you would save this to database
            
            logger.debug(f"Updated engagement analysis for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing engagement for user {user_id}: {e}")


# Task registry and management
class AIBackgroundTaskManager:
    """Manager for AI background tasks"""
    
    def __init__(self, ai_service: AIService, user_service: UserService, 
                 post_service: PostService, comment_service: CommentService):
        self.ai_service = ai_service
        self.user_service = user_service
        self.post_service = post_service
        self.comment_service = comment_service
        self.tasks = []
        self.running = False
    
    async def initialize_tasks(self):
        """Initialize all AI background tasks"""
        try:
            self.tasks = [
                ContentAnalysisTask(self.ai_service, self.post_service),
                ModelTrainingTask(self.ai_service, self.post_service, self.comment_service),
                AnalyticsUpdateTask(self.ai_service),
                UserEngagementAnalysisTask(self.ai_service, self.user_service, self.post_service)
            ]
            
            logger.info(f"Initialized {len(self.tasks)} AI background tasks")
            
        except Exception as e:
            logger.error(f"Error initializing AI tasks: {e}")
    
    async def start_tasks(self):
        """Start all background tasks"""
        try:
            if self.running:
                logger.warning("Tasks already running")
                return
            
            await self.initialize_tasks()
            
            self.running = True
            
            # Start all tasks
            for task in self.tasks:
                asyncio.create_task(task.run())
            
            logger.info("All AI background tasks started")
            
        except Exception as e:
            logger.error(f"Error starting AI tasks: {e}")
    
    async def stop_tasks(self):
        """Stop all background tasks"""
        try:
            self.running = False
            
            # Stop all tasks
            for task in self.tasks:
                await task.stop()
            
            self.tasks.clear()
            
            logger.info("All AI background tasks stopped")
            
        except Exception as e:
            logger.error(f"Error stopping AI tasks: {e}")
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get status of all tasks"""
        try:
            status = {
                "running": self.running,
                "total_tasks": len(self.tasks),
                "tasks": []
            }
            
            for task in self.tasks:
                task_info = {
                    "name": task.name,
                    "status": "running" if task.running else "stopped",
                    "interval_seconds": task.interval_seconds,
                    "last_execution": task.last_execution.isoformat() if task.last_execution else None,
                    "execution_count": task.execution_count,
                    "error_count": task.error_count
                }
                status["tasks"].append(task_info)
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting task status: {e}")
            return {"error": str(e)}


# Factory function
async def create_ai_background_task_manager(
    ai_service: AIService,
    user_service: UserService,
    post_service: PostService,
    comment_service: CommentService
) -> AIBackgroundTaskManager:
    """Factory function to create AI background task manager"""
    manager = AIBackgroundTaskManager(ai_service, user_service, post_service, comment_service)
    return manager