from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

# Enums for validation
class Category(str, Enum):
    OFFICE_SUPPLIES = "office_supplies"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    TRAVEL = "travel"
    TRAINING = "training"
    CONSULTING = "consulting"
    OTHER = "other"

class Department(str, Enum):
    ENGINEERING = "engineering"
    MARKETING = "marketing"
    SALES = "sales"
    FINANCE = "finance"
    HR = "hr"
    OPERATIONS = "operations"
    OTHER = "other"

# Base schema with common fields
class SpendingBase(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount must be greater than 0")
    category: Category = Field(..., description="Spending category")
    vendor: str = Field(..., min_length=2, max_length=100, description="Vendor name")
    description: Optional[str] = Field(None, max_length=500, description="Transaction description")
    date: date = Field(..., description="Transaction date")
    department: Department = Field(..., description="Department or team")

    # Validator for amount to ensure it has up to 2 decimal places
    @validator('amount')
    def round_amount(cls, v):
        return round(v, 2)

# Schema for creating a new spending record
class SpendingCreate(SpendingBase):
    pass

# Schema for updating an existing spending record
class SpendingUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[Category] = None
    vendor: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    date: Optional[date] = None
    department: Optional[Department] = None

# Base schema for database representation
class SpendingInDBBase(SpendingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema for returning spending data (without sensitive info)
class Spending(SpendingInDBBase):
    pass

# Schema for database model (includes all fields)
class SpendingInDB(SpendingInDBBase):
    pass
