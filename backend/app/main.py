from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import problems, auth, submissions, analysis, recommendations

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Technical Interview Prep with Personalized AI Feedback"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(problems.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(submissions.router, prefix="/api/submissions")
app.include_router(analysis.router, prefix="/api/analysis")
app.include_router(recommendations.router, prefix="/api/recommendations")


@app.get("/")
async def root():
    return {
        "message": "Welcome to CodeMentor AI",
        "version": settings.VERSION,
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)