from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import database
from app.schemas import comment as comment_schema
from app.services import comment as comment_service

router = APIRouter()

@router.get("/comments/", response_model=list[comment_schema.Comment])
def read_comments(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    comments = comment_service.get_comments(db, skip=skip, limit=limit)
    return comments

@router.get("/comments/{comment_id}", response_model=comment_schema.Comment)
def read_comment(comment_id: int, db: Session = Depends(database.get_db)):
    comment = comment_service.get_comment(db, comment_id=comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.post("/comments/", response_model=comment_schema.Comment)
def create_comment(comment: comment_schema.CommentCreate, db: Session = Depends(database.get_db)):
    return comment_service.create_comment(db, comment, comment.author_id)

@router.put("/comments/{comment_id}", response_model=comment_schema.Comment)
def update_comment(comment_id: int, comment: comment_schema.CommentUpdate, db: Session = Depends(database.get_db)):
    db_comment = comment_service.update_comment(db, comment_id, comment)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(database.get_db)):
    db_comment = comment_service.delete_comment(db, comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Comment deleted successfully"}

@router.get("/posts/{post_id}/comments/", response_model=list[comment_schema.Comment])
def read_comments_by_post(post_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    comments = comment_service.get_comments_by_post(db, post_id, skip=skip, limit=limit)
    return comments