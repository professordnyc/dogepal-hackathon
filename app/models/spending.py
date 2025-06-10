from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

# Import Base from our central database configuration
from database import Base

class Spending(Base):
    """
    Model representing a spending transaction for DOGEPAL - AI-powered spending analysis.
    """
    __tablename__ = "spending"
    
    # Core transaction fields
    transaction_id = Column(String, primary_key=True, index=True, doc="Unique transaction identifier")
    user_id = Column(String, index=True, default="demo_user_123", doc="User/team identifier")
    user_type = Column(String, index=True, doc="Type of user: solopreneur, startup, board")
    department = Column(String, index=True, doc="Department or focus area (e.g., HR, Tech, Waste, Planning)")
    project_name = Column(String, index=True, doc="Name of the project/initiative")
    borough = Column(String, index=True, doc="NYC borough (Queens, Bronx, Staten Island, Manhattan, Brooklyn)")
    spending_date = Column(Date, nullable=False, index=True, doc="Date of the transaction")
    vendor = Column(String, index=True, nullable=False, doc="Vendor or service provider")
    category = Column(String, index=True, nullable=False, doc="Type of expense (software, consulting, hardware, logistics, etc)")
    amount = Column(Float, nullable=False, doc="Transaction amount (USD)")
    justification = Column(String, doc="Reason for the expense")
    approval_status = Column(String, index=True, default="pending", doc="Status: pending, approved, rejected")
    
    # Metadata for AI/analysis
    metadata_field = Column("metadata", SQLiteJSON, default=dict, doc="Additional metadata and AI explanations")
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    recommendations = relationship("Recommendation", back_populates="spending", cascade="all, delete-orphan")
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_spending_user_date', 'user_id', 'spending_date'),
        Index('idx_spending_borough_category', 'borough', 'category'),
        Index('idx_spending_project_status', 'project_name', 'approval_status'),
        Index('idx_spending_vendor_category', 'vendor', 'category'),
    )
    
    def __repr__(self):
        return f"<Spending(transaction_id={self.transaction_id}, amount={self.amount}, vendor='{self.vendor}', project='{self.project_name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses."""
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "user_type": self.user_type,
            "department": self.department,
            "project_name": self.project_name,
            "borough": self.borough,
            "spending_date": self.spending_date.isoformat() if self.spending_date else None,
            "vendor": self.vendor,
            "category": self.category,
            "amount": self.amount,
            "justification": self.justification,
            "approval_status": self.approval_status,
            "metadata": dict(self.metadata_field) if self.metadata_field else {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Recommendation(Base):
    """Model representing AI-generated recommendations for spending optimization."""
    __tablename__ = "recommendation"  # Changed from 'recommendations' to match the actual table name
    
    id = Column(String, primary_key=True, index=True, doc="Unique recommendation ID")
    transaction_id = Column(String, ForeignKey('spending.transaction_id', ondelete='CASCADE'), nullable=False)
    
    # Recommendation details
    recommendation_type = Column(String, nullable=False, index=True, doc="Recommendation type (vendor_consolidation, budget_alert, etc.)")
    title = Column(String, nullable=False, doc="Short title for the recommendation")
    description = Column(String, doc="Detailed description of the recommendation")
    
    # Impact and confidence
    potential_savings = Column(Float, default=0.0, doc="Potential savings amount in USD")
    confidence_score = Column(Float, default=0.0, doc="Confidence level (0-1)")
    priority = Column(String, default="medium", doc="Priority level: low, medium, high")
    
    # Explanation and metadata
    explanation = Column(String, doc="Human-readable explanation of the recommendation")
    metadata_field = Column("metadata", SQLiteJSON, default=dict, doc="Additional metadata for the recommendation")
    
    # Status tracking
    status = Column(String, default="pending", index=True, doc="Status: pending, applied, dismissed")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    spending = relationship("Spending", back_populates="recommendations")
    
    # Indexes
    __table_args__ = (
        Index('idx_recommendation_type_status', 'recommendation_type', 'status'),
        Index('idx_recommendation_priority', 'priority'),
    )
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, type='{self.type}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses."""
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "recommendation_type": self.recommendation_type,
            "title": self.title,
            "description": self.description,
            "potential_savings": self.potential_savings,
            "confidence_score": self.confidence_score,
            "priority": self.priority,
            "explanation": self.explanation,
            "metadata": dict(self.metadata_field) if self.metadata_field else {},
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
