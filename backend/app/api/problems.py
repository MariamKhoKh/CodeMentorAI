from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.database import get_db
from app.models.problem import Problem
from app.schemas.problem import (
    ProblemCreate,
    ProblemUpdate,
    ProblemResponse,
    ProblemListItem,
    ProblemStats
)
from app.utils.enums import DifficultyLevel

router = APIRouter(prefix="/problems", tags=["problems"])


@router.post("/", response_model=ProblemResponse, status_code=201)
async def create_problem(
    problem: ProblemCreate,
    db: AsyncSession = Depends(get_db)
):
    # check if slug already exists
    result = await db.execute(
        select(Problem).where(Problem.slug == problem.slug)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Problem with this slug already exists")
    
    # convert test_cases to dict format
    test_cases_dict = [tc.model_dump() for tc in problem.test_cases]
    optimal_patterns_dict = problem.optimal_patterns.model_dump() if problem.optimal_patterns else None
    
    db_problem = Problem(
        title=problem.title,
        slug=problem.slug,
        description=problem.description,
        difficulty=problem.difficulty,
        constraints=problem.constraints,
        tags=problem.tags,
        test_cases=test_cases_dict,
        optimal_patterns=optimal_patterns_dict,
        starter_code=problem.starter_code,
        reference_solution=problem.reference_solution
    )
    
    db.add(db_problem)
    await db.commit()
    await db.refresh(db_problem)
    
    return db_problem


@router.get("/", response_model=List[ProblemListItem])
async def list_problems(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    difficulty: Optional[DifficultyLevel] = None,
    tag: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Problem)
    
    if difficulty:
        query = query.where(Problem.difficulty == difficulty)
    
    if tag:
        query = query.where(Problem.tags.contains([tag]))
    
    query = query.offset(skip).limit(limit).order_by(Problem.created_at.desc())
    
    result = await db.execute(query)
    problems = result.scalars().all()
    
    return problems


@router.get("/stats", response_model=ProblemStats)
async def get_problem_stats(db: AsyncSession = Depends(get_db)):
    # total problems
    total_result = await db.execute(select(func.count(Problem.id)))
    total = total_result.scalar()
    
    # by difficulty
    difficulty_result = await db.execute(
        select(Problem.difficulty, func.count(Problem.id))
        .group_by(Problem.difficulty)
    )
    by_difficulty = {str(diff): count for diff, count in difficulty_result.all()}
    
    # by tags (simplified - just get all problems and count tags)
    all_problems = await db.execute(select(Problem.tags))
    by_tags = {}
    for (tags,) in all_problems.all():
        for tag in tags:
            by_tags[tag] = by_tags.get(tag, 0) + 1
    
    return ProblemStats(
        total_problems=total,
        by_difficulty=by_difficulty,
        by_tags=by_tags
    )


@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(
    problem_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Problem).where(Problem.id == problem_id)
    )
    problem = result.scalar_one_or_none()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    return problem


@router.get("/slug/{slug}", response_model=ProblemResponse)
async def get_problem_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Problem).where(Problem.slug == slug)
    )
    problem = result.scalar_one_or_none()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    return problem


@router.put("/{problem_id}", response_model=ProblemResponse)
async def update_problem(
    problem_id: int,
    problem_update: ProblemUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Problem).where(Problem.id == problem_id)
    )
    db_problem = result.scalar_one_or_none()
    
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    update_data = problem_update.model_dump(exclude_unset=True)
    
    # convert test_cases if provided
    if "test_cases" in update_data and update_data["test_cases"]:
        update_data["test_cases"] = [tc.model_dump() for tc in problem_update.test_cases]
    
    # convert optimal_patterns if provided
    if "optimal_patterns" in update_data and update_data["optimal_patterns"]:
        update_data["optimal_patterns"] = problem_update.optimal_patterns.model_dump()
    
    for field, value in update_data.items():
        setattr(db_problem, field, value)
    
    await db.commit()
    await db.refresh(db_problem)
    
    return db_problem


@router.delete("/{problem_id}", status_code=204)
async def delete_problem(
    problem_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Problem).where(Problem.id == problem_id)
    )
    problem = result.scalar_one_or_none()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    await db.delete(problem)
    await db.commit()
    
    return None