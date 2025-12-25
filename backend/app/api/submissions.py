from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.analysis import AnalysisResult
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionResponse,
    SubmissionListItem
)
from app.services.execution import execution_service
from app.services.ast_analyzer import ast_analyzer
from app.services.complexity import complexity_analyzer
from app.services.feedback import feedback_generator
from app.api.deps import get_current_user
from app.utils.enums import SubmissionStatus, ProgrammingLanguage

router = APIRouter(tags=["submissions"])


# @router.post("/", response_model=SubmissionResponse, status_code=201)
# async def submit_code(
#     submission: SubmissionCreate,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Submit code for a problem.
#     Full pipeline: Execute → Analyze → Generate AI Feedback
#     """
    
#     # Get problem
#     result = await db.execute(
#         select(Problem).where(Problem.id == submission.problem_id)
#     )
#     problem = result.scalar_one_or_none()
    
#     if not problem:
#         raise HTTPException(status_code=404, detail="Problem not found")
    
#     # Create submission record
#     db_submission = Submission(
#         user_id=current_user.id,
#         problem_id=submission.problem_id,
#         code=submission.code,
#         language=submission.language,
#         status=SubmissionStatus.RUNNING
#     )
    
#     db.add(db_submission)
#     await db.commit()
#     await db.refresh(db_submission)
    
#     try:
#         # Step 1: Execute code
#         if submission.language == ProgrammingLanguage.PYTHON:
#             execution_result = execution_service.execute_python(
#                 submission.code,
#                 problem.test_cases
#             )
#         else:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Language {submission.language} not supported yet"
#             )
        
#         # Update submission with execution results
#         db_submission.status = SubmissionStatus.COMPLETED
#         db_submission.test_results = execution_result["test_results"]
#         db_submission.total_tests = execution_result["total_tests"]
#         db_submission.passed_tests = execution_result["passed_tests"]
#         db_submission.all_tests_passed = execution_result["all_tests_passed"]
#         db_submission.runtime_ms = execution_result["avg_runtime_ms"]
#         db_submission.memory_kb = execution_result["avg_memory_kb"]
        
#         await db.commit()
        
#         # Step 2: Analyze code structure (AST)
#         ast_features = ast_analyzer.analyze(submission.code)
        
#         # Step 3: Estimate complexity
#         complexity_result = complexity_analyzer.estimate_complexity(
#             ast_features,
#             problem.optimal_patterns
#         )
        
#         # Step 4: Generate AI feedback
#         feedback_result = feedback_generator.generate_feedback(
#             problem_description=problem.description,
#             user_code=submission.code,
#             test_results=execution_result["test_results"],
#             ast_features=ast_features,
#             complexity_analysis=complexity_result,
#             all_tests_passed=execution_result["all_tests_passed"]
#         )
        
#         # Step 5: Create analysis record with feedback
#         analysis = AnalysisResult(
#             submission_id=db_submission.id,
#             ast_features=ast_features,
#             estimated_time_complexity=complexity_result["estimated_time_complexity"],
#             estimated_space_complexity=complexity_result["estimated_space_complexity"],
#             optimal_time_complexity=complexity_result.get("optimal_time_complexity"),
#             optimal_space_complexity=complexity_result.get("optimal_space_complexity"),
#             complexity_match=complexity_result.get("complexity_match"),
#             feedback_text=feedback_result.get("feedback_text"),
#             improvement_suggestions=feedback_result.get("improvement_suggestions")
#         )
        
#         db.add(analysis)
#         await db.commit()
#         await db.refresh(db_submission)
        
#         return db_submission
        
#     except Exception as e:
#         # Update submission as failed
#         db_submission.status = SubmissionStatus.FAILED
#         db_submission.error_message = str(e)
#         await db.commit()
#         await db.refresh(db_submission)
        
#         raise HTTPException(
#             status_code=500,
#             detail=f"Execution failed: {str(e)}"
#         )


@router.post("/", response_model=SubmissionResponse, status_code=201)
async def submit_code(
    submission: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit code for a problem.
    Full pipeline: Execute → Analyze → Generate AI Feedback → Update Weakness Profile
    """
    
    # Get problem
    result = await db.execute(
        select(Problem).where(Problem.id == submission.problem_id)
    )
    problem = result.scalar_one_or_none()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Create submission record
    db_submission = Submission(
        user_id=current_user.id,
        problem_id=submission.problem_id,
        code=submission.code,
        language=submission.language,
        status=SubmissionStatus.RUNNING
    )
    
    db.add(db_submission)
    await db.commit()
    await db.refresh(db_submission)
    
    try:
        # Step 1: Execute code
        if submission.language == ProgrammingLanguage.PYTHON:
            execution_result = execution_service.execute_python(
                submission.code,
                problem.test_cases
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Language {submission.language} not supported yet"
            )
        
        # Update submission with execution results
        db_submission.status = SubmissionStatus.COMPLETED
        db_submission.test_results = execution_result["test_results"]
        db_submission.total_tests = execution_result["total_tests"]
        db_submission.passed_tests = execution_result["passed_tests"]
        db_submission.all_tests_passed = execution_result["all_tests_passed"]
        db_submission.runtime_ms = execution_result["avg_runtime_ms"]
        db_submission.memory_kb = execution_result["avg_memory_kb"]
        
        await db.commit()
        
        # Step 2: Analyze code structure (AST)
        ast_features = ast_analyzer.analyze(submission.code)
        
        # Step 3: Estimate complexity
        complexity_result = complexity_analyzer.estimate_complexity(
            ast_features,
            problem.optimal_patterns
        )
        
        # Step 4: Generate AI feedback
        feedback_result = feedback_generator.generate_feedback(
            problem_description=problem.description,
            user_code=submission.code,
            test_results=execution_result["test_results"],
            ast_features=ast_features,
            complexity_analysis=complexity_result,
            all_tests_passed=execution_result["all_tests_passed"]
        )
        
        # Step 5: Create analysis record with feedback
        analysis = AnalysisResult(
            submission_id=db_submission.id,
            ast_features=ast_features,
            estimated_time_complexity=complexity_result["estimated_time_complexity"],
            estimated_space_complexity=complexity_result["estimated_space_complexity"],
            optimal_time_complexity=complexity_result.get("optimal_time_complexity"),
            optimal_space_complexity=complexity_result.get("optimal_space_complexity"),
            complexity_match=complexity_result.get("complexity_match"),
            feedback_text=feedback_result.get("feedback_text"),
            improvement_suggestions=feedback_result.get("improvement_suggestions")
        )
        
        db.add(analysis)
        await db.commit()
        
        # Step 6: Update weakness profile (NEW!)
        from app.services.weakness_analyzer import weakness_analyzer
        try:
            await weakness_analyzer.update_weakness_profile(
                user_id=current_user.id,
                db=db
            )
        except Exception as e:
            # Don't fail submission if weakness analysis fails
            print(f"Warning: Failed to update weakness profile: {str(e)}")
        
        await db.refresh(db_submission)
        return db_submission
        
    except Exception as e:
        # Update submission as failed
        db_submission.status = SubmissionStatus.FAILED
        db_submission.error_message = str(e)
        await db.commit()
        await db.refresh(db_submission)
        
        raise HTTPException(
            status_code=500,
            detail=f"Execution failed: {str(e)}"
        )

@router.get("/", response_model=List[SubmissionListItem])
async def list_submissions(
    problem_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's submissions with optional filtering by problem."""
    
    query = select(Submission).where(Submission.user_id == current_user.id)
    
    if problem_id:
        query = query.where(Submission.problem_id == problem_id)
    
    query = query.order_by(desc(Submission.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    submissions = result.scalars().all()
    
    return submissions


@router.get("/me", response_model=List[SubmissionListItem])
async def get_my_submissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all submissions for the current user."""
    query = select(Submission).where(Submission.user_id == current_user.id)
    query = query.order_by(desc(Submission.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    submissions = result.scalars().all()
    return submissions

@router.get("/{submission_id:int}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific submission by ID."""
    result = await db.execute(
        select(Submission).where(
            Submission.id == submission_id,
            Submission.user_id == current_user.id
        )
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )
    return submission