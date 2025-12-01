"""
Base service implementation with common business logic patterns.
"""

from abc import ABC
from typing import List, Optional, Dict, Any, Generic, TypeVar, Type, Union
from sqlalchemy.orm import Session
from app.core.interfaces import RepositoryInterface
from app.core.service_interfaces import ServiceInterface
from app.core.exceptions import (
    EntityNotFoundError, 
    EntityAlreadyExistsError, 
    ValidationError,
    BusinessLogicError
)

ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ServiceInterface[CreateSchemaType, UpdateSchemaType]):
    """Base service with common business logic operations."""
    
    def __init__(self, repository: RepositoryInterface[ModelType, CreateSchemaType, UpdateSchemaType]):
        self.repository = repository
    
    async def create(self, data: CreateSchemaType) -> Dict[str, Any]:
        """Create new entity with validation and error handling."""
        try:
            # Validate data before creation
            await self._validate_create_data(data)
            
            # Create entity through repository
            if isinstance(data, dict):
                entity = self.repository.create(data)
            else:
                entity = self.repository.create(data.dict())
            
            # Post-creation business logic
            await self._after_create(entity)
            
            return self._serialize_entity(entity)
            
        except EntityAlreadyExistsError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            await self._handle_create_error(e, data)
            raise BusinessLogicError(f"Failed to create entity: {str(e)}")
    
    async def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Get entity by ID with caching and error handling."""
        try:
            entity = self.repository.get_by_id(id)
            if entity is None:
                return None
            
            # Post-retrieval business logic
            await self._after_get(entity)
            
            return self._serialize_entity(entity)
            
        except Exception as e:
            await self._handle_get_error(e, id)
            raise BusinessLogicError(f"Failed to retrieve entity {id}: {str(e)}")
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all entities with pagination."""
        try:
            entities = self.repository.get_all(skip=skip, limit=limit)
            
            # Post-retrieval business logic
            for entity in entities:
                await self._after_get(entity)
            
            return [self._serialize_entity(entity) for entity in entities]
            
        except Exception as e:
            await self._handle_get_all_error(e, skip, limit)
            raise BusinessLogicError(f"Failed to retrieve entities: {str(e)}")
    
    async def update(self, id: int, data: UpdateSchemaType) -> Optional[Dict[str, Any]]:
        """Update existing entity with validation."""
        try:
            # Check if entity exists
            if not self.repository.exists(id):
                raise EntityNotFoundError(self._get_entity_name(), "id", id)
            
            # Validate update data
            await self._validate_update_data(id, data)
            
            # Update through repository
            if isinstance(data, dict):
                entity = self.repository.update(id, data)
            else:
                entity = self.repository.update(id, data.dict(exclude_unset=True))
            
            if entity is None:
                raise EntityNotFoundError(self._get_entity_name(), "id", id)
            
            # Post-update business logic
            await self._after_update(entity)
            
            return self._serialize_entity(entity)
            
        except EntityNotFoundError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            await self._handle_update_error(e, id, data)
            raise BusinessLogicError(f"Failed to update entity {id}: {str(e)}")
    
    async def delete(self, id: int) -> bool:
        """Delete entity with pre-validation."""
        try:
            # Check if entity exists
            if not self.repository.exists(id):
                raise EntityNotFoundError(self._get_entity_name(), "id", id)
            
            # Pre-deletion business logic
            await self._before_delete(id)
            
            # Delete through repository
            success = self.repository.delete(id)
            
            # Post-deletion business logic
            if success:
                await self._after_delete(id)
            
            return success
            
        except EntityNotFoundError:
            raise
        except Exception as e:
            await self._handle_delete_error(e, id)
            raise BusinessLogicError(f"Failed to delete entity {id}: {str(e)}")
    
    async def count(self) -> int:
        """Get total count of entities."""
        try:
            return self.repository.count()
        except Exception as e:
            raise BusinessLogicError(f"Failed to count entities: {str(e)}")
    
    # Abstract methods to be implemented by subclasses
    async def _validate_create_data(self, data: CreateSchemaType) -> None:
        """Validate data before creation. Override in subclasses."""
        pass
    
    async def _validate_update_data(self, id: int, data: UpdateSchemaType) -> None:
        """Validate data before update. Override in subclasses."""
        pass
    
    async def _after_create(self, entity: ModelType) -> None:
        """Post-creation business logic. Override in subclasses."""
        pass
    
    async def _after_get(self, entity: ModelType) -> None:
        """Post-retrieval business logic. Override in subclasses."""
        pass
    
    async def _after_update(self, entity: ModelType) -> None:
        """Post-update business logic. Override in subclasses."""
        pass
    
    async def _before_delete(self, id: int) -> None:
        """Pre-deletion business logic. Override in subclasses."""
        pass
    
    async def _after_delete(self, id: int) -> None:
        """Post-deletion business logic. Override in subclasses."""
        pass
    
    async def _handle_create_error(self, error: Exception, data: CreateSchemaType) -> None:
        """Handle creation errors. Override in subclasses for custom handling."""
        pass
    
    async def _handle_get_error(self, error: Exception, id: int) -> None:
        """Handle retrieval errors. Override in subclasses for custom handling."""
        pass
    
    async def _handle_get_all_error(self, error: Exception, skip: int, limit: int) -> None:
        """Handle bulk retrieval errors. Override in subclasses for custom handling."""
        pass
    
    async def _handle_update_error(self, error: Exception, id: int, data: UpdateSchemaType) -> None:
        """Handle update errors. Override in subclasses for custom handling."""
        pass
    
    async def _handle_delete_error(self, error: Exception, id: int) -> None:
        """Handle deletion errors. Override in subclasses for custom handling."""
        pass
    
    def _serialize_entity(self, entity: ModelType) -> Dict[str, Any]:
        """Serialize entity to dictionary. Override in subclasses for custom serialization."""
        if hasattr(entity, '__dict__'):
            return entity.__dict__
        return dict(entity)
    
    def _get_entity_name(self) -> str:
        """Get entity name for error messages. Override in subclasses."""
        return "Entity"