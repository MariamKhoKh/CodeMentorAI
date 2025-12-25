from enum import Enum


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ProgrammingLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"


class ErrorCategory(str, Enum):
    INEFFICIENT_ALGORITHM = "INEFFICIENT_ALGORITHM"
    EDGE_CASE_MISSED = "EDGE_CASE_MISSED"
    INCORRECT_DATA_STRUCTURE = "INCORRECT_DATA_STRUCTURE"
    OFF_BY_ONE = "OFF_BY_ONE"
    OVERFITTING_TO_EXAMPLES = "OVERFITTING_TO_EXAMPLES"
    POOR_ABSTRACTION = "POOR_ABSTRACTION"
    INCORRECT_LOGIC = "INCORRECT_LOGIC"
    MISSING_GUARD_CLAUSES = "MISSING_GUARD_CLAUSES"
    INEFFICIENT_SPACE_USAGE = "INEFFICIENT_SPACE_USAGE"
    INCORRECT_COMPLEXITY = "INCORRECT_COMPLEXITY"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    TIMEOUT = "TIMEOUT"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class TestCaseStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"