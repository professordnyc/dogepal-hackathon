from datetime import date as dt_date, datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum

# Enums for validation
class CategoryEnum(str, Enum):
    OFFICE_SUPPLIES = "office_supplies"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    TRAVEL = "travel"
    TRAINING = "training"
    CONSULTING = "consulting"
    OTHER = "other"

class DepartmentEnum(str, Enum):
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
    category: CategoryEnum = Field(..., description="Spending category")
    vendor: str = Field(..., min_length=2, max_length=100, description="Vendor name")
    justification: Optional[str] = Field(None, max_length=500, description="Reason for the expense")
    spending_date: dt_date = Field(..., description="Transaction date")
    department: DepartmentEnum = Field(..., description="Department or team")
    user_id: Optional[str] = Field("demo_user_123", description="User/team identifier")
    user_type: Optional[str] = Field(None, description="Type of user")
    project_name: Optional[str] = Field(None, description="Name of the project/initiative")
    borough: Optional[str] = Field(None, description="NYC borough")
    approval_status: Optional[str] = Field("pending", description="Status: pending, approved, rejected")

    # Validator for amount to ensure it has up to 2 decimal places
    @field_validator('amount')
    def round_amount(cls, v):
        return round(v, 2)

# Schema for creating a new spending record
class SpendingCreate(SpendingBase):
    pass

# Schema for updating an existing spending record
class SpendingUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[CategoryEnum] = None
    vendor: Optional[str] = Field(None, min_length=2, max_length=100)
    justification: Optional[str] = Field(None, max_length=500)
    spending_date: Optional[dt_date] = None
    department: Optional[DepartmentEnum] = None
    user_id: Optional[str] = None
    user_type: Optional[str] = None
    project_name: Optional[str] = None
    borough: Optional[str] = None
    approval_status: Optional[str] = None

# Base schema for database representation
class SpendingInDBBase(SpendingBase):
    transaction_id: str
    metadata_field: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }

# Schema for returning spending data (without sensitive info)
class Spending(SpendingInDBBase):
    pass

# Schema for database model (includes all fields)
class SpendingInDB(SpendingInDBBase):
    pass
