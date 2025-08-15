import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .logs.config import setup_logging
from contextlib import asynccontextmanager

from .db import models  # noqa: F401
from .db.base import Base, engine
from .routers import auth_router, chat_router, digest_router, portfolio_router

setup_logging()

app = FastAPI(
    title="Agentic Portfolio Optimizer",
    description="AI-powered portfolio analysis and optimization using LangGraph agents",
    version="0.1",
    debug=True,
)

# cors
origins = [
    "http://localhost:8080",
    # "http://localhost:3000",
    # "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(digest_router, prefix="/api", tags=["digest"])
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(portfolio_router, prefix="/api", tags=["portfolio"])


@app.get("/")
async def root():
    return {
        "message": "Agentic Portfolio Optimizer API",
        "version": "0.1",
        "status": "running",
        "endpoints": {
            "chat": "/api/chat/message",
            "digest": "/api/digest",
            "analyze": "/api/analyze",
            "alerts": "/api/alerts",
            "health": "/api/health",
        },
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "portfolio-optimizer-backend"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    logger = logging.getLogger(__name__)
    logger.info("App startup ok")

    yield  # The app will run while paused here

    # Shutdown (optional)
    # logger.info("App shutdown ok")


app = FastAPI(lifespan=lifespan)
