"""
AI Service for Content Analysis and Recommendations
Provides sentiment analysis, content recommendations, and intelligent features
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import faiss
import torch
from transformers import AutoTokenizer, AutoModel
from textblob import TextBlob
import nltk
import json
import pickle
from pathlib import Path

from app.core.base_service import BaseService
from app.models.post import Post
from app.models.comment import Comment
from app.models.user import User
from app.services.user import UserService
from app.services.post import PostService
from app.services.comment import CommentService

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

logger = logging.getLogger(__name__)


class SentimentResult:
    """Result of sentiment analysis"""
    
    def __init__(self, sentiment: str, confidence: float, scores: Dict[str, float]):
        self.sentiment = sentiment  # positive, negative, neutral
        self.confidence = confidence  # 0-1 confidence score
        self.scores = scores  # detailed scores for each sentiment


class ContentSimilarity:
    """Content similarity result"""
    
    def __init__(self, post_id: int, similarity_score: float, title: str):
        self.post_id = post_id
        self.similarity_score = similarity_score
        self.title = title


class RecommendationScore:
    """Content recommendation score"""
    
    def __init__(self, post_id: int, score: float, reasons: List[str]):
        self.post_id = post_id
        self.score = score
        self.reasons = reasons


class AIService(BaseService):
    """AI-powered content analysis and recommendation service"""
    
    def __init__(self, user_service: UserService, post_service: PostService, comment_service: CommentService):
        super().__init__()
        self.user_service = user_service
        self.post_service = post_service
        self.comment_service = comment_service
        
        # Initialize AI models
        self._initialize_models()
        
        # Cache for embeddings and similarity matrices
        self.embeddings_cache = {}
        self.similarity_cache = {}
        self.vectorizer_cache = None
        
        # Content clustering model
        self.content_clusterer = None
        self.content_clusters = {}
        
    def _initialize_models(self):
        """Initialize AI models"""
        try:
            # Initialize sentence transformer for embeddings
            self.tokenizer = AutoTokenizer.from_pretrained('all-MiniLM-L6-v2')
            self.model = AutoModel.from_pretrained('all-MiniLM-L6-v2')
            
            # TF-IDF vectorizer for text similarity
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            logger.info("AI models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AI models: {e}")
            # Fallback to basic features if model loading fails
            self.tfidf_vectorizer = TfidfVectorizer(max_features=500)
    
    async def analyze_sentiment(self, text: str) -> SentimentResult:
        """Analyze sentiment of text using multiple approaches"""
        try:
            # Use TextBlob for initial sentiment
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            
            # Use VADER for social media sentiment (if available)
            try:
                from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
                analyzer = SentimentIntensityAnalyzer()
                vader_scores = analyzer.polarity_scores(text)
                vader_compound = vader_scores['compound']
            except:
                vader_compound = polarity
            
            # Combine scores
            combined_score = (polarity + vader_compound) / 2
            
            # Determine sentiment
            if combined_score > 0.1:
                sentiment = "positive"
                confidence = min(abs(combined_score), 1.0)
            elif combined_score < -0.1:
                sentiment = "negative"
                confidence = min(abs(combined_score), 1.0)
            else:
                sentiment = "neutral"
                confidence = 1 - abs(combined_score)
            
            scores = {
                "textblob_polarity": polarity,
                "vader_compound": vader_compound,
                "combined_score": combined_score,
                "confidence": confidence
            }
            
            return SentimentResult(sentiment, confidence, scores)
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return SentimentResult("neutral", 0.5, {"error": str(e)})
    
    async def get_content_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for a list of texts"""
        try:
            if not texts:
                return np.array([])
            
            # Check cache first
            cache_key = hash(tuple(sorted(texts)))
            if cache_key in self.embeddings_cache:
                return self.embeddings_cache[cache_key]
            
            # Get embeddings using sentence transformer
            if hasattr(self, 'model') and self.model is not None:
                # Use transformer model
                with torch.no_grad():
                    inputs = self.tokenizer(texts, padding=True, truncation=True, 
                                          return_tensors='pt', max_length=512)
                    outputs = self.model(**inputs)
                    embeddings = outputs.last_hidden_state[:, 0, :].numpy()
            else:
                # Fallback to TF-IDF
                if self.vectorizer_cache is None:
                    self.vectorizer_cache = self.tfidf_vectorizer
                embeddings = self.vectorizer_cache.fit_transform(texts).toarray()
            
            # Cache the results
            self.embeddings_cache[cache_key] = embeddings
            return embeddings
            
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            return np.array([])
    
    async def find_similar_content(self, post_id: int, limit: int = 5) -> List[ContentSimilarity]:
        """Find similar content to a given post"""
        try:
            # Get the target post
            target_post = await self.post_service.get_by_id(post_id)
            if not target_post:
                return []
            
            # Get all posts
            all_posts = await self.post_service.get_all()
            if not all_posts:
                return []
            
            # Prepare texts for comparison
            target_text = f"{target_post.title} {target_post.content}"
            other_texts = []
            other_post_ids = []
            
            for post in all_posts:
                if post.id != post_id:
                    other_texts.append(f"{post.title} {post.content}")
                    other_post_ids.append(post.id)
            
            if not other_texts:
                return []
            
            # Combine all texts for embedding generation
            all_texts = [target_text] + other_texts
            embeddings = await self.get_content_embeddings(all_texts)
            
            if len(embeddings) < 2:
                return []
            
            # Calculate similarity
            target_embedding = embeddings[0].reshape(1, -1)
            other_embeddings = embeddings[1:]
            
            similarities = cosine_similarity(target_embedding, other_embeddings)[0]
            
            # Get top similar posts
            similar_indices = np.argsort(similarities)[::-1][:limit]
            
            similar_content = []
            for idx in similar_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    post = next(p for p in all_posts if p.id == other_post_ids[idx])
                    similar_content.append(ContentSimilarity(
                        post_id=post.id,
                        similarity_score=float(similarities[idx]),
                        title=post.title
                    ))
            
            return similar_content
            
        except Exception as e:
            logger.error(f"Error finding similar content: {e}")
            return []
    
    async def analyze_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Analyze user preferences based on their interactions"""
        try:
            # Get user's posts
            user_posts = await self.post_service.get_by_user_id(user_id)
            
            # Get user's comments and likes
            user_comments = await self.comment_service.get_by_user_id(user_id)
            
            # Analyze content preferences
            content_analysis = {
                "total_posts": len(user_posts),
                "total_comments": len(user_comments),
                "preferred_categories": {},
                "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
                "content_length_stats": {"avg": 0, "min": 0, "max": 0},
                "engagement_score": 0.0
            }
            
            if not user_posts and not user_comments:
                return content_analysis
            
            # Analyze post content
            post_sentiments = []
            content_lengths = []
            category_counts = {}
            
            for post in user_posts:
                # Sentiment analysis
                sentiment = await self.analyze_sentiment(f"{post.title} {post.content}")
                post_sentiments.append(sentiment.sentiment)
                content_lengths.append(len(post.content))
                
                # Category analysis
                if post.category:
                    category_counts[post.category.name] = category_counts.get(post.category.name, 0) + 1
            
            # Calculate stats
            if post_sentiments:
                content_analysis["sentiment_distribution"]["positive"] = post_sentiments.count("positive")
                content_analysis["sentiment_distribution"]["negative"] = post_sentiments.count("negative")
                content_analysis["sentiment_distribution"]["neutral"] = post_sentiments.count("neutral")
            
            if content_lengths:
                content_analysis["content_length_stats"]["avg"] = np.mean(content_lengths)
                content_analysis["content_length_stats"]["min"] = min(content_lengths)
                content_analysis["content_length_stats"]["max"] = max(content_lengths)
            
            content_analysis["preferred_categories"] = dict(sorted(category_counts.items(), 
                                                                 key=lambda x: x[1], reverse=True))
            
            # Calculate engagement score
            total_interactions = len(user_posts) + len(user_comments)
            content_analysis["engagement_score"] = min(total_interactions / 10.0, 1.0)  # Normalize to 0-1
            
            return content_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing user preferences: {e}")
            return {"error": str(e)}
    
    async def get_personalized_recommendations(self, user_id: int, limit: int = 10) -> List[RecommendationScore]:
        """Get personalized content recommendations for a user"""
        try:
            # Get user's preferences
            user_prefs = await self.analyze_user_preferences(user_id)
            
            # Get all posts
            all_posts = await self.post_service.get_all()
            user_posts = await self.post_service.get_by_user_id(user_id)
            
            # Filter out user's own posts
            recommended_posts = [p for p in all_posts if p.user_id != user_id]
            
            if not recommended_posts:
                return []
            
            # Calculate recommendation scores
            recommendations = []
            
            for post in recommended_posts:
                score = await self._calculate_recommendation_score(post, user_id, user_prefs)
                recommendations.append(RecommendationScore(
                    post_id=post.id,
                    score=score["total_score"],
                    reasons=score["reasons"]
                ))
            
            # Sort by score and return top recommendations
            recommendations.sort(key=lambda x: x.score, reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
    
    async def _calculate_recommendation_score(self, post: Post, user_id: int, 
                                            user_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate recommendation score for a post"""
        score = 0.0
        reasons = []
        
        try:
            # 1. Category preference score
            if post.category and post.category.name in user_prefs.get("preferred_categories", {}):
                category_score = 0.3
                score += category_score
                reasons.append(f"Matches your interest in {post.category.name}")
            
            # 2. Content similarity to user's posts
            user_posts = await self.post_service.get_by_user_id(user_id)
            if user_posts:
                user_texts = [f"{p.title} {p.content}" for p in user_posts]
                post_text = f"{post.title} {post.content}"
                
                all_texts = user_texts + [post_text]
                embeddings = await self.get_content_embeddings(all_texts)
                
                if len(embeddings) >= 2:
                    similarities = cosine_similarity([embeddings[-1]], embeddings[:-1])
                    max_similarity = np.max(similarities)
                    
                    if max_similarity > 0.3:
                        similarity_score = max_similarity * 0.4
                        score += similarity_score
                        reasons.append("Similar to your previous content")
            
            # 3. Sentiment alignment
            post_sentiment = await self.analyze_sentiment(f"{post.title} {post.content}")
            user_sentiment_dist = user_prefs.get("sentiment_distribution", {})
            
            if post_sentiment.sentiment in user_sentiment_dist and user_sentiment_dist[post_sentiment.sentiment] > 0:
                sentiment_score = 0.2
                score += sentiment_score
                reasons.append(f"Matches your preference for {post_sentiment.sentiment} content")
            
            # 4. Engagement score (likes, comments)
            engagement_score = (post.likes_count or 0) * 0.1 + (post.comments_count or 0) * 0.05
            if engagement_score > 0:
                score += min(engagement_score, 0.3)
                reasons.append("Popular content")
            
            # 5. Recency score (newer posts get higher scores)
            if hasattr(post, 'created_at') and post.created_at:
                days_old = (datetime.utcnow() - post.created_at).days
                recency_score = max(0, 0.2 - days_old * 0.01)
                score += recency_score
                if recency_score > 0.1:
                    reasons.append("Recent content")
            
            # 6. Content quality score (length, structure)
            content_length = len(post.content)
            if 100 <= content_length <= 2000:  # Optimal length
                quality_score = 0.1
                score += quality_score
                reasons.append("Well-sized content")
            
            # Normalize score to 0-1
            score = min(score, 1.0)
            
            return {
                "total_score": score,
                "reasons": reasons,
                "category_score": score * 0.3 if any("interest" in r for r in reasons) else 0,
                "similarity_score": score * 0.4 if any("Similar" in r for r in reasons) else 0,
                "sentiment_score": score * 0.2 if any("preference" in r for r in reasons) else 0,
                "engagement_score": score * 0.1 if any("Popular" in r for r in reasons) else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating recommendation score: {e}")
            return {"total_score": 0.1, "reasons": ["Default recommendation"], "error": str(e)}
    
    async def classify_content(self, title: str, content: str) -> Dict[str, Any]:
        """Classify content into categories and topics"""
        try:
            full_text = f"{title} {content}"
            
            # Analyze sentiment
            sentiment = await self.analyze_sentiment(full_text)
            
            # Extract key topics using simple keyword matching
            topics = await self._extract_topics(full_text)
            
            # Estimate reading time
            word_count = len(full_text.split())
            reading_time = max(1, word_count // 200)  # Assuming 200 words per minute
            
            # Content complexity (simple proxy using word length)
            words = full_text.split()
            avg_word_length = np.mean([len(word) for word in words])
            complexity = "simple" if avg_word_length < 5 else "complex" if avg_word_length > 7 else "medium"
            
            return {
                "sentiment": {
                    "label": sentiment.sentiment,
                    "confidence": sentiment.confidence,
                    "scores": sentiment.scores
                },
                "topics": topics,
                "reading_time_minutes": reading_time,
                "complexity": complexity,
                "word_count": word_count,
                "character_count": len(full_text),
                "estimated_engagement": await self._estimate_engagement(full_text)
            }
            
        except Exception as e:
            logger.error(f"Error classifying content: {e}")
            return {"error": str(e)}
    
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text using keyword matching"""
        try:
            # Define topic keywords
            topic_keywords = {
                "technology": ["AI", "machine learning", "coding", "programming", "software", "tech", "digital", "automation", "blockchain", "cloud"],
                "business": ["business", "startup", "entrepreneur", "revenue", "profit", "strategy", "management", "leadership"],
                "health": ["health", "fitness", "nutrition", "exercise", "wellness", "mental health", "medical", "diet"],
                "science": ["research", "study", "experiment", "theory", "data", "analysis", "scientific", "discovery"],
                "education": ["learning", "education", "teaching", "student", "course", "tutorial", "guide", "skill"],
                "entertainment": ["movie", "music", "game", "fun", "funny", "entertainment", "show", "series"],
                "travel": ["travel", "vacation", "trip", "journey", "adventure", "explore", "destination"],
                "food": ["food", "cooking", "recipe", "restaurant", "dish", "meal", "cuisine", "chef"],
                "politics": ["politics", "government", "policy", "election", "democracy", "vote", "political"],
                "sports": ["sports", "football", "basketball", "soccer", "tennis", "athlete", "competition", "game"]
            }
            
            text_lower = text.lower()
            found_topics = []
            
            for topic, keywords in topic_keywords.items():
                score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
                if score >= 1:  # Minimum threshold
                    found_topics.append({
                        "topic": topic,
                        "relevance_score": min(score / len(keywords), 1.0)
                    })
            
            # Sort by relevance and return top topics
            found_topics.sort(key=lambda x: x["relevance_score"], reverse=True)
            return found_topics[:3]  # Top 3 topics
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []
    
    async def _estimate_engagement(self, text: str) -> str:
        """Estimate potential engagement level"""
        try:
            # Factors that typically increase engagement
            engagement_indicators = 0
            
            # Question marks (encourage discussion)
            engagement_indicators += text.count('?') * 0.1
            
            # Exclamation marks (emotional content)
            engagement_indicators += text.count('!') * 0.05
            
            # Numbers and statistics (credibility)
            import re
            numbers = len(re.findall(r'\d+', text))
            engagement_indicators += numbers * 0.02
            
            # Emotional words
            emotional_words = ["amazing", "incredible", "shocking", "important", "crucial", "essential", "must"]
            engagement_indicators += sum(1 for word in emotional_words if word in text.lower()) * 0.03
            
            # Optimal length (neither too short nor too long)
            word_count = len(text.split())
            if 50 <= word_count <= 500:
                engagement_indicators += 0.1
            
            # Classify engagement level
            if engagement_indicators >= 0.5:
                return "high"
            elif engagement_indicators >= 0.2:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.error(f"Error estimating engagement: {e}")
            return "medium"
    
    async def batch_analyze_content(self, posts: List[Post]) -> Dict[int, Dict[str, Any]]:
        """Analyze multiple posts in batch"""
        try:
            results = {}
            
            # Process in batches to avoid overwhelming the system
            batch_size = 10
            for i in range(0, len(posts), batch_size):
                batch = posts[i:i + batch_size]
                batch_tasks = []
                
                for post in batch:
                    task = asyncio.create_task(
                        self.classify_content(post.title, post.content)
                    )
                    batch_tasks.append((post.id, task))
                
                # Wait for batch completion
                for post_id, task in batch_tasks:
                    try:
                        analysis = await task
                        results[post_id] = analysis
                    except Exception as e:
                        logger.error(f"Error analyzing post {post_id}: {e}")
                        results[post_id] = {"error": str(e)}
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            return {}
    
    async def moderate_content(self, title: str, content: str) -> Dict[str, Any]:
        """Moderate content for inappropriate material"""
        try:
            full_text = f"{title} {content}"
            
            # Check for inappropriate keywords (basic filter)
            inappropriate_keywords = [
                # Add your specific keywords here
                "spam", "fake", "scam", "inappropriate_content"
            ]
            
            found_issues = []
            confidence_scores = {}
            
            for keyword in inappropriate_keywords:
                if keyword in full_text.lower():
                    found_issues.append({
                        "type": "inappropriate_keyword",
                        "keyword": keyword,
                        "severity": "low",
                        "confidence": 0.7
                    })
            
            # Sentiment analysis for extreme negativity
            sentiment = await self.analyze_sentiment(full_text)
            if sentiment.sentiment == "negative" and sentiment.confidence > 0.8:
                found_issues.append({
                    "type": "negative_sentiment",
                    "description": "Highly negative content",
                    "severity": "medium",
                    "confidence": sentiment.confidence
                })
            
            # Overall moderation decision
            is_approved = len(found_issues) == 0
            severity = "high" if any(issue["severity"] == "high" for issue in found_issues) else \
                      "medium" if any(issue["severity"] == "medium" for issue in found_issues) else "low"
            
            return {
                "approved": is_approved,
                "issues_found": found_issues,
                "severity": severity,
                "total_issues": len(found_issues),
                "confidence": 1.0 - (len(found_issues) * 0.1),  # Decreases with more issues
                "action_required": "review" if severity in ["medium", "high"] else "none"
            }
            
        except Exception as e:
            logger.error(f"Error moderating content: {e}")
            return {
                "approved": False,
                "issues_found": [{"error": str(e)}],
                "severity": "unknown",
                "confidence": 0.0
            }


# Service factory function
def create_ai_service(user_service: UserService, post_service: PostService, comment_service: CommentService) -> AIService:
    """Factory function to create AI service with dependencies"""
    return AIService(user_service, post_service, comment_service)