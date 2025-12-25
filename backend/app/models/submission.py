from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Float, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.utils.enums import SubmissionStatus, ProgrammingLanguage


class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)
    
    code = Column(Text, nullable=False)
    language = Column(SQLEnum(ProgrammingLanguage), nullable=False)
    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.PENDING, index=True)
    
    # Execution results
    test_results = Column(JSON, nullable=True)  # [{test_case_id, status, runtime, memory}]
    all_tests_passed = Column(Boolean, default=False)
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    
    runtime_ms = Column(Float, nullable=True)
    memory_kb = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # relationships
    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
    analysis = relationship("AnalysisResult", back_populates="submission", uselist=False, cascade="all, delete-orphan")