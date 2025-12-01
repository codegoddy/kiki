from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app import models
from app.schemas import category as category_schema

def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()

def get_categories_with_post_count(db: Session, skip: int = 0, limit: int = 100):
    """Get categories with their post counts"""
    categories = (
        db.query(
            models.Category,
            func.count(models.Post.id).label('post_count')
        )
        .outerjoin(models.post_category_association, models.Category.id == models.post_category_association.c.category_id)
        .outerjoin(models.Post, models.post_category_association.c.post_id == models.Post.id)
        .group_by(models.Category.id)
        .order_by(desc('post_count'), models.Category.name)
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    result = []
    for category, post_count in categories:
        category_data = category_schema.Category.from_orm(category)
        category_data.post_count = post_count
        result.append(category_data)
    
    return result

def create_category(db: Session, category: category_schema.CategoryCreate):
    db_category = models.Category(
        name=category.name,
        description=category.description,
        color=category.color
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category: category_schema.CategoryUpdate):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        update_data = category.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category

def get_category_by_name(db: Session, name: str):
    return db.query(models.Category).filter(models.Category.name == name).first()

def get_categories_by_post(db: Session, post_id: int):
    """Get all categories for a specific post"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    return post.categories if post else []

def add_post_to_category(db: Session, post_id: int, category_id: int):
    """Add a post to a category"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    
    if post and category and category not in post.categories:
        post.categories.append(category)
        db.commit()
        return True
    return False

def remove_post_from_category(db: Session, post_id: int, category_id: int):
    """Remove a post from a category"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    
    if post and category and category in post.categories:
        post.categories.remove(category)
        db.commit()
        return True
    return False

def search_categories(db: Session, query: str, skip: int = 0, limit: int = 100):
    """Search categories by name or description"""
    return db.query(models.Category).filter(
        (models.Category.name.ilike(f"%{query}%")) | 
        (models.Category.description.ilike(f"%{query}%"))
    ).offset(skip).limit(limit).all()