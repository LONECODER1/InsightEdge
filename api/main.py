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

# Bulletproof CORS: Catch-all middleware guarantees CORS headers on all requests,
# instant responses to preflight OPTIONS, and CORS headers even on 500 exceptions.
@app.middleware("http")
async def add_cors_headers(request, call_next):
    if request.method == "OPTIONS":
        from fastapi.responses import Response
        response = Response(status_code=200)
    else:
        try:
            response = await call_next(request)
        except Exception as e:
            from fastapi.responses import JSONResponse
            response = JSONResponse({"error": str(e)}, status_code=500)

    origin = request.headers.get("origin") or "*"
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r".*",
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
