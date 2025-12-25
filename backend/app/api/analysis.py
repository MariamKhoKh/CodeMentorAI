from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.submission import Submission
from app.models.analysis import AnalysisResult
from app.schemas.analysis import AnalysisResultResponse
from app.api.deps import get_current_user

router = APIRouter(tags=["analysis"])


@router.get("/{submission_id}", response_model=AnalysisResultResponse)
async def get_analysis(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get code analysis for a specific submission."""
    
    # Verify submission belongs to user
    result = await db.execute(
        select(Submission).where(
            Submission.id == submission_id,
            Submission.user_id == current_user.id
        )
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Get analysis
    result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.submission_id == submission_id)
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis