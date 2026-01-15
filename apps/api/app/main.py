"""
JobPulse API - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import engine, Base
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.applications.router import router as applications_router
from app.companies.router import router as companies_router
from app.jobs.router import router as jobs_router
from app.resumes.router import router as resumes_router
from app.connections.router import router as connections_router
from app.notifications.router import router as notifications_router
from app.crawlers.router import router as crawlers_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Cleanup if needed
    await engine.dispose()


app = FastAPI(
    title="JobPulse API",
    description="취업 지원 현황 통합 관리 및 AI 분석 플랫폼",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(applications_router, prefix="/api/applications", tags=["Applications"])
app.include_router(companies_router, prefix="/api/companies", tags=["Companies"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(resumes_router, prefix="/api/resumes", tags=["Resumes"])
app.include_router(connections_router, prefix="/api/connections", tags=["Connections"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(crawlers_router, prefix="/api/crawlers", tags=["Job Crawlers"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "JobPulse API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }
