from sqlalchemy.orm import Session
from app import models
from app.schemas import comment as comment_schema

def get_comment(db: Session, comment_id: int):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

def get_comments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Comment).offset(skip).limit(limit).all()

def create_comment(db: Session, comment: comment_schema.CommentCreate, author_id: int):
    db_comment = models.Comment(
        content=comment.content,
        post_id=comment.post_id,
        author_id=author_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def update_comment(db: Session, comment_id: int, comment: comment_schema.CommentUpdate):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment:
        update_data = comment.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_comment, field, value)
        db.commit()
        db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: int):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment:
        db.delete(db_comment)
        db.commit()
    return db_comment

def get_comments_by_post(db: Session, post_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).offset(skip).limit(limit).all()

def get_comments_by_author(db: Session, author_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Comment).filter(models.Comment.author_id == author_id).offset(skip).limit(limit).all()