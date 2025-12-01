"""
Base repository implementation with common CRUD operations.
"""

from abc import ABC
from typing import List, Optional, TypeVar, Generic, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from app.core.exceptions import EntityNotFoundError

ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: type, db: Session):
        self.model = model
        self.db = db
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get entity by ID."""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except NoResultFound:
            return None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all entities with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, data: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """Create new entity."""
        if isinstance(data, dict):
            db_obj = self.model(**data)
        else:
            # Assume it's a Pydantic model with dict() method
            db_obj = self.model(**data.dict())
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, data: Union[UpdateSchemaType, Dict[str, Any]]) -> Optional[ModelType]:
        """Update existing entity."""
        db_obj = self.get_by_id(id)
        if db_obj is None:
            return None
        
        if isinstance(data, dict):
            update_data = data
        else:
            # Assume it's a Pydantic model with dict() method
            update_data = data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        db_obj = self.get_by_id(id)
        if db_obj is None:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True
    
    def exists(self, id: int) -> bool:
        """Check if entity exists by ID."""
        return self.db.query(self.db.query(self.model).filter(self.model.id == id).exists()).scalar()
    
    def count(self) -> int:
        """Get total count of entities."""
        return self.db.query(self.model).count()