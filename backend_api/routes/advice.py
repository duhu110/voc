from __future__ import annotations

from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from backend_api.schemas import AdviceRequest
from voc_agent.advice_provider_agent import (
    run_advice_provider,
    run_advice_provider_for_ticket_payload,
)

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/advice")
async def create_advice(request: AdviceRequest) -> dict:
    try:
        if request.ticket_payload is not None:
            result = await run_in_threadpool(
                run_advice_provider_for_ticket_payload,
                request.ticket_payload,
                hide_processing_context=not request.include_processing_context,
                advice_limit=request.advice_limit,
                sample_limit=request.sample_limit,
            )
        else:
            result = await run_in_threadpool(
                run_advice_provider,
                request.ticket_id,
                use_existing_classification=request.use_existing_classification,
                hide_processing_context=not request.include_processing_context,
                advice_limit=request.advice_limit,
                sample_limit=request.sample_limit,
            )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "success", "result": result}

