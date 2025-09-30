"""Base repository with common CRUD operations."""

from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: Type[ModelType], session: Session) -> None:
        """
        Initialize repository.
        
        Args:
            model: SQLAlchemy model class
            session: Database session
        """
        self.model = model
        self.session = session
    
    def create(self, **kwargs: Any) -> ModelType:
        """
        Create a new record.
        
        Args:
            **kwargs: Model attributes
        
        Returns:
            Created model instance
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        self.session.flush()
        self.session.refresh(instance)
        return instance
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Get record by primary key ID.
        
        Args:
            id: Primary key
        
        Returns:
            Model instance or None
        """
        return self.session.get(self.model, id)
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[ModelType]:
        """
        Get all records with optional pagination.
        
        Args:
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of model instances
        """
        query = select(self.model).offset(offset)
        if limit is not None:
            query = query.limit(limit)
        result = self.session.execute(query)
        return list(result.scalars().all())
    
    def update(self, id: int, **kwargs: Any) -> Optional[ModelType]:
        """
        Update a record by ID.
        
        Args:
            id: Primary key
            **kwargs: Attributes to update
        
        Returns:
            Updated model instance or None
        """
        instance = self.get_by_id(id)
        if instance is None:
            return None
        
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        self.session.flush()
        self.session.refresh(instance)
        return instance
    
    def delete(self, id: int) -> bool:
        """
        Hard delete a record by ID.
        
        Args:
            id: Primary key
        
        Returns:
            True if deleted, False if not found
        """
        instance = self.get_by_id(id)
        if instance is None:
            return False
        
        self.session.delete(instance)
        self.session.flush()
        return True
    
    def soft_delete(self, id: int) -> bool:
        """
        Soft delete a record by ID (if model supports it).
        
        Args:
            id: Primary key
        
        Returns:
            True if soft deleted, False if not found
        """
        instance = self.get_by_id(id)
        if instance is None:
            return False
        
        if hasattr(instance, "soft_delete"):
            instance.soft_delete()
            self.session.flush()
            return True
        
        return False
    
    def count(self) -> int:
        """
        Count total records.
        
        Returns:
            Total count
        """
        query = select(self.model)
        result = self.session.execute(query)
        return len(list(result.scalars().all()))
    
    def exists(self, id: int) -> bool:
        """
        Check if record exists.
        
        Args:
            id: Primary key
        
        Returns:
            True if exists, False otherwise
        """
        return self.get_by_id(id) is not None
