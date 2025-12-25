from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.utils.enums import DifficultyLevel


class TestCase(BaseModel):
    input: Dict[str, Any]
    expected_output: Any
    is_hidden: bool = False
    explanation: Optional[str] = None


class OptimalPatterns(BaseModel):
    time_complexity: str
    space_complexity: str
    key_patterns: List[str]
    key_data_structures: List[str]


class ProblemBase(BaseModel):
    title: str
    slug: str
    description: str
    difficulty: DifficultyLevel
    constraints: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)
    test_cases: List[TestCase]
    optimal_patterns: Optional[OptimalPatterns] = None
    starter_code: Optional[Dict[str, str]] = None
    reference_solution: Optional[Dict[str, str]] = None


class ProblemCreate(ProblemBase):
    pass


class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    constraints: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    test_cases: Optional[List[TestCase]] = None
    optimal_patterns: Optional[OptimalPatterns] = None
    starter_code: Optional[Dict[str, str]] = None
    reference_solution: Optional[Dict[str, str]] = None


class ProblemResponse(ProblemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProblemListItem(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    difficulty: DifficultyLevel
    tags: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProblemStats(BaseModel):
    total_problems: int
    by_difficulty: Dict[str, int]
    by_tags: Dict[str, int]