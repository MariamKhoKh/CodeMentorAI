from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.utils.enums import ErrorCategory


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # AST features
    ast_features = Column(JSON, nullable=True)  # {loops, nested_loops, recursion, uses_hashmap, etc.}
    
    # complexity analysis
    estimated_time_complexity = Column(String, nullable=True)
    estimated_space_complexity = Column(String, nullable=True)
    optimal_time_complexity = Column(String, nullable=True)
    optimal_space_complexity = Column(String, nullable=True)
    complexity_match = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # error classification
    error_category = Column(SQLEnum(ErrorCategory), nullable=True, index=True)
    error_confidence = Column(Float, nullable=True)
    
    # LLM feedback
    feedback_text = Column(Text, nullable=True)
    improvement_suggestions = Column(JSON, nullable=True)  # [suggestion1, suggestion2, ...]
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # relationships
    submission = relationship("Submission", back_populates="analysis")