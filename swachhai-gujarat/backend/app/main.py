"""
SwachhAI Gujarat — Backend Entry Point
FastAPI application factory with all routers, middleware, and CORS.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import auth, complaints, agents, analytics, segregation, routes as route_router, admin
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create all tables on startup
Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="SwachhAI Gujarat API",
    description="Agentic AI platform for Municipal Solid Waste Management",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(complaints.router, prefix="/api/complaints", tags=["Complaints"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(segregation.router, prefix="/api/segregation", tags=["Segregation"])
app.include_router(route_router.router, prefix="/api/routes", tags=["Routes"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "app": "SwachhAI Gujarat",
        "version": "1.0.0",
        "demo_mode": settings.demo_mode,
    }


@app.on_event("startup")
async def startup_event():
    logger.info("SwachhAI Gujarat API starting up")
    logger.info(f"Demo mode: {settings.demo_mode}")
    logger.info(f"Primary LLM provider: {settings.primary_llm_provider}")
