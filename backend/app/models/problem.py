from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.utils.enums import DifficultyLevel


class Problem(Base):
    __tablename__ = "problems"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), nullable=False, index=True)
    
    # JSON fields
    constraints = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=False, default=list)  # ["Array", "HashMap", "TwoPointers"]
    test_cases = Column(JSON, nullable=False)  # [{input, expected_output, is_hidden}]
    optimal_patterns = Column(JSON, nullable=True)  # {time_complexity, space_complexity, key_patterns}
    starter_code = Column(JSON, nullable=True)  # {python: "...", javascript: "..."}
    reference_solution = Column(JSON, nullable=True)  # {python: "...", javascript: "..."}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # relationships
    submissions = relationship("Submission", back_populates="problem", cascade="all, delete-orphan")