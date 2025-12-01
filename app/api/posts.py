"""Posts API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import post as post_schema
from app.services import post as post_service

router = APIRouter()


@router.get(
    "/posts/", 
    response_model=List[post_schema.Post],
    status_code=status.HTTP_200_OK,
    summary="Get all posts",
    description="Retrieve a list of posts with optional pagination."
)
def read_posts(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
) -> List[post_schema.Post]:
    """Get all posts with pagination."""
    db_posts = post_service.get_posts(db, skip=skip, limit=limit)
    return [post_schema.Post.model_validate(post.__dict__) for post in db_posts]


@router.get(
    "/posts/{post_id}", 
    response_model=post_schema.Post,
    status_code=status.HTTP_200_OK,
    summary="Get post by ID",
    description="Retrieve a specific post by its ID."
)
def read_post(post_id: int, db: Session = Depends(get_db)) -> post_schema.Post:
    """Get a specific post by ID."""
    post = post_service.get_post(db, post_id=post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post_schema.Post.model_validate(post.__dict__)


@router.post(
    "/posts/", 
    response_model=post_schema.Post,
    status_code=status.HTTP_201_CREATED,
    summary="Create new post",
    description="Create a new post with the provided data."
)
def create_post(
    post: post_schema.PostCreate, 
    db: Session = Depends(get_db)
) -> post_schema.Post:
    """Create a new post."""
    db_post = post_service.create_post(db, post, post.author_id)
    return post_schema.Post.model_validate(db_post.__dict__)


@router.put(
    "/posts/{post_id}", 
    response_model=post_schema.Post,
    status_code=status.HTTP_200_OK,
    summary="Update post",
    description="Update an existing post with new data."
)
def update_post(
    post_id: int, 
    post: post_schema.PostUpdate, 
    db: Session = Depends(get_db)
) -> post_schema.Post:
    """Update an existing post."""
    db_post = post_service.update_post(db, post_id, post)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post_schema.Post.model_validate(db_post.__dict__)


@router.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete post",
    description="Delete a post by its ID."
)
def delete_post(post_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a post."""
    db_post = post_service.delete_post(db, post_id)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    # Return None for 204 No Content response
    return None


@router.get(
    "/posts/search/", 
    response_model=List[post_schema.Post],
    status_code=status.HTTP_200_OK,
    summary="Search posts",
    description="Search posts by title or content."
)
def search_posts(
    query: str, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
) -> List[post_schema.Post]:
    """Search posts by query string."""
    db_posts = post_service.search_posts(db, query=query, skip=skip, limit=limit)
    return [post_schema.Post.model_validate(post.__dict__) for post in db_posts]