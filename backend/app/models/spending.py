from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base

class Spending(Base):
    """
    Model representing a spending transaction.
    """
    __tablename__ = "spending"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False, doc="Transaction amount")
    category = Column(String, index=True, nullable=False, doc="Spending category")
    vendor = Column(String, index=True, nullable=False, doc="Vendor name")
    description = Column(String, doc="Transaction description")
    date = Column(Date, index=True, nullable=False, doc="Transaction date")
    department = Column(String, index=True, doc="Department or team")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    recommendations = relationship("Recommendation", back_populates="spending")
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_spending_date_category', 'date', 'category'),
        Index('idx_spending_department', 'department'),
        Index('idx_spending_vendor', 'vendor'),
    )
    
    def __repr__(self):
        return f"<Spending(id={self.id}, amount={self.amount}, category='{self.category}', vendor='{self.vendor}')>"


class Recommendation(Base):
    """
    Model representing a recommendation generated from spending analysis.
    """
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    spending_id = Column(Integer, ForeignKey('spending.id'), nullable=False)
    recommendation_type = Column(String, nullable=False, doc="Type of recommendation")
    title = Column(String, nullable=False, doc="Short title for the recommendation")
    description = Column(String, doc="Detailed description")
    potential_savings = Column(Float, doc="Potential savings amount")
    confidence_score = Column(Float, doc="Confidence level (0-1)")
    explanation = Column(String, doc="Technical explanation of the recommendation")
    suggested_action = Column(String, doc="Recommended action to take")
    status = Column(String, default="pending", doc="Status: pending, implemented, rejected")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    spending = relationship("Spending", back_populates="recommendations")
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, type='{self.recommendation_type}', savings={self.potential_savings})>"
