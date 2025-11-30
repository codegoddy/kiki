from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import database
from app.schemas import admin as admin_schema
from app.services import admin as admin_service

router = APIRouter()

@router.get("/users/", response_model=list[admin_schema.UserAdmin])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    users = admin_service.get_users(db, skip=skip, limit=limit)
    return users

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    db_user = admin_service.delete_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@router.get("/posts/", response_model=list[admin_schema.PostAdmin])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    posts = admin_service.get_posts(db, skip=skip, limit=limit)
    return posts

@router.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(database.get_db)):
    db_post = admin_service.delete_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}