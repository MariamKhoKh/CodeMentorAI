from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.utils.enums import ErrorCategory


class ASTFeatures(BaseModel):
    loops: int = 0
    nested_loops: bool = False
    max_loop_depth: int = 0
    recursion: bool = False
    uses_hashmap: bool = False
    uses_set: bool = False
    uses_list: bool = False
    uses_dict: bool = False
    conditionals: int = 0
    early_exits: int = 0
    function_calls: List[str] = []
    data_structures: List[str] = []
    sorting_used: bool = False
    list_comprehension: bool = False
    guards: bool = False


class ComplexityAnalysis(BaseModel):
    estimated_time_complexity: str
    estimated_space_complexity: str
    optimal_time_complexity: Optional[str] = None
    optimal_space_complexity: Optional[str] = None
    complexity_match: Optional[float] = None


class AnalysisResultResponse(BaseModel):
    id: int
    submission_id: int
    ast_features: Optional[Dict[str, Any]] = None
    estimated_time_complexity: Optional[str] = None
    estimated_space_complexity: Optional[str] = None
    optimal_time_complexity: Optional[str] = None
    optimal_space_complexity: Optional[str] = None
    complexity_match: Optional[float] = None
    error_category: Optional[ErrorCategory] = None
    error_confidence: Optional[float] = None
    feedback_text: Optional[str] = None
    improvement_suggestions: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True