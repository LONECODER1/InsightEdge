"""
FastAPI backend — thin wrapper around LangGraph.
Serves SSE streams + REST endpoints for history and memory.
Run: uvicorn api.main:app --reload --port 8000
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.analyze import router as analyze_router
from api.routes.history import router as history_router
from api.routes.memory import router as memory_router
from api.routes.search import router as search_router

app = FastAPI(title="AI Hedge Fund API", version="1.0.0")

# Robust CORS configuration:
# Using allow_origin_regex matches any http/https origin and dynamically reflects it,
# which allows credentials and avoids browser wildcard (*) rejection.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Support both /api prefix and root paths for maximum compatibility
app.include_router(analyze_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(memory_router, prefix="/api")
app.include_router(search_router, prefix="/api")

app.include_router(analyze_router)
app.include_router(history_router)
app.include_router(memory_router)
app.include_router(search_router)


@app.get("/api/health")
@app.get("/health")
async def health():
    return {"status": "ok"}
