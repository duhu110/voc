from __future__ import annotations

from fastapi import FastAPI

from backend_api.routes import advice, health, rag


def create_app() -> FastAPI:
    app = FastAPI(
        title="VOC Operations Backend",
        version="0.1.0",
        description="Unified backend for VOC ticket import, agent advice, and RAG knowledge management.",
    )
    app.include_router(health.router)
    app.include_router(advice.router)
    app.include_router(rag.router)
    return app


app = create_app()

