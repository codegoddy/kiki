from sqlalchemy.orm import Session
from app import models
from app.schemas import post as post_schema

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()

def create_post(db: Session, post: post_schema.PostCreate, author_id: int):
    db_post = models.Post(
        title=post.title,
        content=post.content,
        author_id=author_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def update_post(db: Session, post_id: int, post: post_schema.PostUpdate):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post:
        update_data = post.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_post, field, value)
        db.commit()
        db.refresh(db_post)
    return db_post

def delete_post(db: Session, post_id: int):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post:
        db.delete(db_post)
        db.commit()
    return db_post

def get_posts_by_author(db: Session, author_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Post).filter(models.Post.author_id == author_id).offset(skip).limit(limit).all()