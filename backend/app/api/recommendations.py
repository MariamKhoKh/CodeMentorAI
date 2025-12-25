from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.analysis import AnalysisResult
from app.models.weakness_profile import WeaknessProfile
from app.api.deps import get_current_user
from app.services.problem_generator import problem_generator
from app.services.weakness_analyzer import weakness_analyzer
from app.schemas.problem import ProblemCreate, ProblemResponse
from pydantic import BaseModel

router = APIRouter(tags=["recommendations"])


# New endpoint: AI-generated problem based on weaknesses
from fastapi import Body
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import uuid

@router.post("/ai-problem", response_model=ProblemResponse)
async def generate_ai_problem(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a new coding problem using AI based on user's weaknesses.
    Saves the problem to the database and returns it.
    """
    # Fetch user's weakness profile
    result = await db.execute(
        select(WeaknessProfile).where(WeaknessProfile.user_id == current_user.id)
    )
    weakness_profile = result.scalar_one_or_none()
    if not weakness_profile or not weakness_profile.top_weaknesses:
        raise HTTPException(status_code=404, detail="No weakness profile or weaknesses found for user.")

    weaknesses = weakness_profile.top_weaknesses
    ai_problem = problem_generator.generate_problem(weaknesses)
    if "error" in ai_problem:
        raise HTTPException(status_code=500, detail=ai_problem["error"])

    # Prepare ProblemCreate schema
    slug = ai_problem.get("title", str(uuid.uuid4())).lower().replace(" ", "-")[:50]
    # Ensure difficulty is lowercase and valid
    raw_difficulty = ai_problem.get("difficulty", "easy")
    if isinstance(raw_difficulty, str):
        difficulty = raw_difficulty.lower()
    else:
        difficulty = "easy"
    if difficulty not in ["easy", "medium", "hard"]:
        difficulty = "easy"

    # Fix test_cases: ensure input is a dict, not a string
    raw_test_cases = ai_problem.get("test_cases", [])
    fixed_test_cases = []
    for tc in raw_test_cases:
        tc_copy = dict(tc)
        # If input is a string, try to parse as JSON/list and wrap in dict
        if isinstance(tc_copy.get("input"), str):
            import json
            try:
                parsed = json.loads(tc_copy["input"])
                # If parsed is not a dict, wrap in {"nums": parsed}
                if not isinstance(parsed, dict):
                    tc_copy["input"] = {"nums": parsed}
                else:
                    tc_copy["input"] = parsed
            except Exception:
                tc_copy["input"] = {"raw": tc_copy["input"]}
        fixed_test_cases.append(tc_copy)

    problem_in = ProblemCreate(
        title=ai_problem.get("title", "AI Generated Problem"),
        slug=slug,
        description=ai_problem.get("description", ""),
        difficulty=difficulty,
        constraints=ai_problem.get("constraints", {}),
        tags=ai_problem.get("tags", []),
        test_cases=fixed_test_cases,
        optimal_patterns=None,
        starter_code=ai_problem.get("starter_code", None),
        reference_solution=ai_problem.get("reference_solution", None)
    )

    # Save to DB
    try:
        db_problem = Problem(**problem_in.dict())
        db.add(db_problem)
        await db.commit()
        await db.refresh(db_problem)
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

    return db_problem


class RecommendationResponse(BaseModel):
    problem_id: int
    problem_title: str
    reason: str
    confidence_score: float
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[RecommendationResponse])
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-powered problem recommendations based on user's submission history.
    Analyzes patterns in solved problems and suggests next challenges.
    """
    
    # Get user's submissions with analysis
    result = await db.execute(
        select(Submission, AnalysisResult, Problem)
        .join(AnalysisResult, Submission.id == AnalysisResult.submission_id)
        .join(Problem, Submission.problem_id == Problem.id)
        .where(Submission.user_id == current_user.id)
        .where(Submission.all_tests_passed == True)
    )
    
    user_data = result.all()
    
    if len(user_data) == 0:
        # No submissions yet - recommend easy problems
        result = await db.execute(
            select(Problem)
            .where(Problem.difficulty == "Easy")
            .limit(3)
        )
        problems = result.scalars().all()
        
        return [
            RecommendationResponse(
                problem_id=p.id,
                problem_title=p.title,
                reason="Great starting problem for beginners",
                confidence_score=0.9
            )
            for p in problems
        ]
    
    # Analyze user's performance
    solved_problem_ids = {sub.problem_id for sub, _, _ in user_data}
    
    # Calculate average complexity match
    complexity_matches = [
        analysis.complexity_match 
        for _, analysis, _ in user_data 
        if analysis.complexity_match is not None
    ]
    avg_complexity_match = sum(complexity_matches) / len(complexity_matches) if complexity_matches else 0.5
    
    # Determine user skill level
    if avg_complexity_match >= 0.8:
        skill_level = "Advanced"
        target_difficulties = ["medium", "hard"]
    elif avg_complexity_match >= 0.5:
        skill_level = "Intermediate"
        target_difficulties = ["easy", "medium"]
    else:
        skill_level = "Beginner"
        target_difficulties = ["easy"]
    
    # Get problems user hasn't solved yet
    result = await db.execute(
        select(Problem)
        .where(
            and_(
                Problem.id.notin_(solved_problem_ids),
                Problem.difficulty.in_(target_difficulties)
            )
        )
        .limit(5)
    )
    
    unsolved_problems = result.scalars().all()
    
    if len(unsolved_problems) == 0:
        # User solved everything at their level
        return [
            RecommendationResponse(
                problem_id=0,
                problem_title="No recommendations",
                reason="You've solved all problems at your level! Great job!",
                confidence_score=1.0
            )
        ]
    
    # Build recommendations
    recommendations = []
    
    for problem in unsolved_problems:
        # Calculate confidence based on difficulty match
        if problem.difficulty == "Easy":
            confidence = 0.9 if skill_level == "Beginner" else 0.7
            reason = "Good foundational problem to strengthen your basics"
        elif problem.difficulty == "Medium":
            confidence = 0.85 if skill_level == "Intermediate" else 0.6
            reason = "Challenge yourself with this intermediate problem"
        else:  # Hard
            confidence = 0.9 if skill_level == "Advanced" else 0.5
            reason = "Advanced problem to push your limits"
        
        # Boost confidence if tags match previously solved problems
        solved_tags = set()
        for _, _, prob in user_data:
            if prob.tags:
                solved_tags.update(prob.tags)
        
        if problem.tags and solved_tags:
            matching_tags = set(problem.tags) & solved_tags
            if matching_tags:
                confidence = min(confidence + 0.1, 1.0)
                reason = f"Similar to problems you've solved ({', '.join(list(matching_tags)[:2])})"
        
        recommendations.append(
            RecommendationResponse(
                problem_id=problem.id,
                problem_title=problem.title,
                reason=reason,
                confidence_score=round(confidence, 2)
            )
        )
    
    # Sort by confidence score
    recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
    
    return recommendations[:5]  # Return top 5


@router.post("/update-weaknesses")
async def update_weaknesses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger weakness profile update based on submission history.
    Useful for testing or if automatic update fails.
    """
    try:
        profile = await weakness_analyzer.update_weakness_profile(
            user_id=current_user.id,
            db=db
        )
        return {
            "message": "Weakness profile updated successfully",
            "top_weaknesses": profile.top_weaknesses,
            "weak_tags": profile.weak_tags,
            "weak_patterns": profile.weak_patterns,
            "metadata": profile.analysis_metadata
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update weakness profile: {str(e)}"
        )


@router.get("/weaknesses")
async def get_weaknesses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's weakness profile."""
    result = await db.execute(
        select(WeaknessProfile).where(WeaknessProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="No weakness profile found. Submit some problems first!"
        )
    
    return {
        "top_weaknesses": profile.top_weaknesses,
        "weak_tags": profile.weak_tags,
        "weak_patterns": profile.weak_patterns,
        "metadata": profile.analysis_metadata,
        "updated_at": profile.last_updated
    }