"""FastAPI main application."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .routes import api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# Create FastAPI app
app = FastAPI(
    title="Twitter Digest API",
    description="Zero-auth X/Twitter search and digest generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api.router)

# Serve static files (frontend build)
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Twitter Digest API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
