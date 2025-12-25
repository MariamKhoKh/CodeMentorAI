from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
from app.utils.enums import SubmissionStatus, ProgrammingLanguage, TestCaseStatus


class TestCaseResult(BaseModel):
    test_case_id: int
    status: TestCaseStatus
    runtime_ms: Optional[float] = None
    memory_kb: Optional[float] = None
    input: Any
    expected_output: Any
    actual_output: Optional[Any] = None
    error_message: Optional[str] = None
    is_hidden: bool = False


class SubmissionCreate(BaseModel):
    problem_id: int
    code: str
    language: ProgrammingLanguage


class SubmissionResponse(BaseModel):
    id: int
    user_id: int
    problem_id: int
    code: str
    language: ProgrammingLanguage
    status: SubmissionStatus
    test_results: Optional[List[TestCaseResult]] = None
    all_tests_passed: bool
    total_tests: int
    passed_tests: int
    runtime_ms: Optional[float] = None
    memory_kb: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubmissionListItem(BaseModel):
    id: int
    problem_id: int
    language: ProgrammingLanguage
    status: SubmissionStatus
    all_tests_passed: bool
    passed_tests: int
    total_tests: int
    created_at: datetime
    
    class Config:
        from_attributes = True