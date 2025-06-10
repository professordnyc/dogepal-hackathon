"""
SQLAlchemy base model and database configuration.
"""
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, DateTime, String, event
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

# Create a base class for declarative models
Base = declarative_base()

# Type variable for generic model types
ModelType = TypeVar("ModelType", bound=Base)

class TimestampMixin:
    """Mixin that adds timestamp fields to models."""
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

class SoftDeleteMixin:
    """Mixin that adds soft delete functionality to models."""
    deleted_at = Column(DateTime, nullable=True)
    
    @property
    def is_deleted(self) -> bool:
        """Check if the record is soft deleted."""
        return self.deleted_at is not None

# Add SQLite JSON type for better JSON support
from sqlalchemy.types import TypeDecorator, VARCHAR
import json

class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
    
    Usage::
        JSONEncodedDict(255)
    """
    impl = VARCHAR
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

# Alias for backward compatibility
SQLiteJSON = JSONEncodedDict

# This will be used by SQLAlchemy models
__all__ = ["Base", "TimestampMixin", "SoftDeleteMixin", "SQLiteJSON"]
