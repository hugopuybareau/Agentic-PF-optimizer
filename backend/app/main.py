# backend/app/main.py

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.digest import digest_router
from logs.config import setup_logging

setup_logging()

app = FastAPI(
    title="Agentic Portfolio Optimizer",
    description="AI-powered portfolio analysis and optimization using LangGraph agents",
    version="0.1",
    debug=True
)

# cors
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(digest_router, prefix="/api", tags=["portfolio"])

@app.get("/")
async def root():
    return {
        "message": "Agentic Portfolio Optimizer API",
        "version": "0.1",
        "status": "running",
        "endpoints": {
            "digest": "/api/digest",
            "analyze": "/api/analyze", 
            "alerts": "/api/alerts",
            "health": "/api/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "portfolio-optimizer-backend"
    }

@app.on_event("startup")
def startup():
    logger = logging.getLogger(__name__)
    logger.info("App startup ok")