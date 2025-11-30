from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import database
from app.schemas import post as post_schema
from app.services import post as post_service

router = APIRouter()

@router.get("/posts/", response_model=list[post_schema.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    posts = post_service.get_posts(db, skip=skip, limit=limit)
    return posts

@router.get("/posts/{post_id}", response_model=post_schema.Post)
def read_post(post_id: int, db: Session = Depends(database.get_db)):
    post = post_service.get_post(db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.post("/posts/", response_model=post_schema.Post)
def create_post(post: post_schema.PostCreate, db: Session = Depends(database.get_db)):
    return post_service.create_post(db, post, post.author_id)

@router.put("/posts/{post_id}", response_model=post_schema.Post)
def update_post(post_id: int, post: post_schema.PostUpdate, db: Session = Depends(database.get_db)):
    db_post = post_service.update_post(db, post_id, post)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

@router.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(database.get_db)):
    db_post = post_service.delete_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}

@router.get("/posts/search/", response_model=list[post_schema.Post])
def search_posts(query: str, skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    posts = post_service.search_posts(db, query=query, skip=skip, limit=limit)
    return posts