"""Post service layer with enhanced error handling and type safety."""

from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app import models
from app.schemas import post as post_schema
from app.utils.logger import logger


class PostNotFoundError(Exception):
    """Custom exception for post not found."""
    pass


class PostServiceError(Exception):
    """Base exception for post service errors."""
    pass


def get_post(db: Session, post_id: int) -> Optional[models.Post]:
    """Get a single post by ID."""
    try:
        stmt = select(models.Post).where(models.Post.id == post_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting post {post_id}: {e}")
        raise PostServiceError(f"Failed to retrieve post: {e}")


def get_posts(db: Session, skip: int = 0, limit: int = 100) -> List[models.Post]:
    """Get all posts with pagination."""
    try:
        stmt = select(models.Post).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting posts: {e}")
        raise PostServiceError(f"Failed to retrieve posts: {e}")


def create_post(db: Session, post: post_schema.PostCreate, author_id: int) -> models.Post:
    """Create a new post."""
    try:
        db_post = models.Post(
            title=post.title,
            content=post.content,
            author_id=author_id
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        logger.info(f"Created post {db_post.id} for author {author_id}")
        return db_post
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error while creating post: {e}")
        raise PostServiceError(f"Failed to create post due to data integrity issue: {e}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while creating post: {e}")
        raise PostServiceError(f"Failed to create post: {e}")


def update_post(db: Session, post_id: int, post: post_schema.PostUpdate) -> Optional[models.Post]:
    """Update an existing post."""
    try:
        # First, get the existing post
        db_post = get_post(db, post_id)
        if not db_post:
            return None
        
        # Update the fields
        update_data = post.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_post, field, value)
        
        db.commit()
        db.refresh(db_post)
        logger.info(f"Updated post {post_id}")
        return db_post
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while updating post {post_id}: {e}")
        raise PostServiceError(f"Failed to update post: {e}")


def delete_post(db: Session, post_id: int) -> Optional[models.Post]:
    """Delete a post."""
    try:
        db_post = get_post(db, post_id)
        if not db_post:
            return None
        
        db.delete(db_post)
        db.commit()
        logger.info(f"Deleted post {post_id}")
        return db_post
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error while deleting post {post_id}: {e}")
        raise PostServiceError(f"Failed to delete post: {e}")


def get_posts_by_author(db: Session, author_id: int, skip: int = 0, limit: int = 100) -> List[models.Post]:
    """Get posts by a specific author."""
    try:
        stmt = select(models.Post).where(
            models.Post.author_id == author_id
        ).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting posts by author {author_id}: {e}")
        raise PostServiceError(f"Failed to retrieve posts by author: {e}")


def search_posts(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[models.Post]:
    """Search posts by title or content using case-insensitive search."""
    try:
        search_term = f"%{query.lower()}%"
        stmt = select(models.Post).where(
            or_(
                models.Post.title.ilike(search_term),
                models.Post.content.ilike(search_term)
            )
        ).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Database error while searching posts with query '{query}': {e}")
        raise PostServiceError(f"Failed to search posts: {e}")


def get_post_with_relations(db: Session, post_id: int) -> Optional[models.Post]:
    """Get a post with all its relations (author, comments, categories)."""
    try:
        stmt = select(models.Post).where(models.Post.id == post_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting post with relations {post_id}: {e}")
        raise PostServiceError(f"Failed to retrieve post with relations: {e}")


def count_posts(db: Session) -> int:
    """Count total number of posts."""
    try:
        stmt = select(models.Post)
        result = db.execute(stmt)
        return len(result.scalars().all())
    except SQLAlchemyError as e:
        logger.error(f"Database error while counting posts: {e}")
        raise PostServiceError(f"Failed to count posts: {e}")


def get_recent_posts(db: Session, limit: int = 10) -> List[models.Post]:
    """Get the most recent posts."""
    try:
        stmt = select(models.Post).order_by(
            models.Post.created_at.desc()
        ).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Database error while getting recent posts: {e}")
        raise PostServiceError(f"Failed to retrieve recent posts: {e}")