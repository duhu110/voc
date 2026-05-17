from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend_api.routes import advice, auth, expert_playbooks, handling_advices, health, overview, rag, taxonomy, tickets, users


def create_app() -> FastAPI:
    app = FastAPI(
        title="VOC Operations Backend",
        version="0.1.0",
        description="Unified backend for VOC ticket import, agent advice, and RAG knowledge management.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:3000",
            "http://localhost:3000",
            "http://127.0.0.1:3001",
            "http://localhost:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(overview.router)
    app.include_router(advice.router)
    app.include_router(tickets.router)
    app.include_router(expert_playbooks.router)
    app.include_router(handling_advices.router)
    app.include_router(taxonomy.router)
    app.include_router(users.router)
    app.include_router(rag.router)
    return app


app = create_app()
