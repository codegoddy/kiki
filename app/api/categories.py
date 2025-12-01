from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import database
from app.schemas import category as category_schema
from app.services import category as category_service

router = APIRouter()

@router.get("/categories/", response_model=list[category_schema.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    categories = category_service.get_categories(db, skip=skip, limit=limit)
    return categories

@router.get("/categories/with-counts/", response_model=list[category_schema.Category])
def read_categories_with_counts(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    categories = category_service.get_categories_with_post_count(db, skip=skip, limit=limit)
    return categories

@router.get("/categories/{category_id}", response_model=category_schema.Category)
def read_category(category_id: int, db: Session = Depends(database.get_db)):
    category = category_service.get_category(db, category_id=category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/categories/", response_model=category_schema.Category)
def create_category(category: category_schema.CategoryCreate, db: Session = Depends(database.get_db)):
    # Check if category name already exists
    existing_category = category_service.get_category_by_name(db, name=category.name)
    if existing_category:
        raise HTTPException(status_code=400, detail="Category name already exists")
    return category_service.create_category(db, category)

@router.put("/categories/{category_id}", response_model=category_schema.Category)
def update_category(category_id: int, category: category_schema.CategoryUpdate, db: Session = Depends(database.get_db)):
    db_category = category_service.update_category(db, category_id, category)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(database.get_db)):
    db_category = category_service.delete_category(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}

@router.get("/categories/search/", response_model=list[category_schema.Category])
def search_categories(query: str, skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    categories = category_service.search_categories(db, query=query, skip=skip, limit=limit)
    return categories

@router.get("/posts/{post_id}/categories/", response_model=list[category_schema.Category])
def get_post_categories(post_id: int, db: Session = Depends(database.get_db)):
    categories = category_service.get_categories_by_post(db, post_id=post_id)
    return categories

@router.post("/posts/{post_id}/categories/")
def add_post_to_category(post_id: int, category_id: int, db: Session = Depends(database.get_db)):
    success = category_service.add_post_to_category(db, post_id=post_id, category_id=category_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add post to category (post or category may not exist)")
    return {"message": "Post added to category successfully"}

@router.delete("/posts/{post_id}/categories/{category_id}")
def remove_post_from_category(post_id: int, category_id: int, db: Session = Depends(database.get_db)):
    success = category_service.remove_post_from_category(db, post_id=post_id, category_id=category_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove post from category")
    return {"message": "Post removed from category successfully"}