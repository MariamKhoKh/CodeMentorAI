from sqlalchemy import Column, Integer, JSON, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class WeaknessProfile(Base):
    __tablename__ = "weakness_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # ეrror frequency tracking
    error_frequency = Column(JSON, nullable=False, default=dict)  # {error_category: count}
    
    # დata structure & algorithm weaknesses
    ds_algo_weaknesses = Column(JSON, nullable=False, default=dict)  # {concept: weakness_score}
    
    # complexity trends
    complexity_trends = Column(JSON, nullable=True)  # [{date, avg_complexity_match}]
    
    # overall metrics
    total_submissions = Column(Integer, default=0)
    total_problems_solved = Column(Integer, default=0)
    avg_attempts_per_problem = Column(Float, nullable=True)
    improvement_velocity = Column(Float, nullable=True)  # რate of improvement
    consistency_score = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Top 3 weaknesses (cached for quick access)
    top_weaknesses = Column(JSON, nullable=True)  # [weakness1, weakness2, weakness3]

    # Additional fields for API compatibility
    weak_tags = Column(JSON, nullable=True)  # e.g., ["recursion", "greedy"]
    weak_patterns = Column(JSON, nullable=True)  # e.g., ["off-by-one", "edge-cases"]
    analysis_metadata = Column(JSON, nullable=True)  # e.g., {"source": "auto", ...}

    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationships
    user = relationship("User", back_populates="weakness_profile")