from __future__ import annotations

from voc_agent.converger_agent.state import ConvergerState


def finalize_result(state: ConvergerState) -> ConvergerState:
    status = state.get("status", "")
    if status == "skipped_no_category":
        return {
            "result": {
                "ticket_id": state["ticket_id"],
                "status": "skipped_no_category",
                "stop_reason": state.get("stop_reason", ""),
            }
        }

    return {
        "result": {
            "ticket_id": state["ticket_id"],
            "status": "completed",
            "summary": state.get("category_summary", ""),
            "primary_category": state["primary_category"],
            "request_tag": state["request_tag"],
            "emotion_tag": state["emotion_tag"],
            "risk_tag": state["risk_tag"],
            "product_tag": state["product_tag"],
            "line_category": state["line_category"],
            "resolution_summary": state.get("resolution_summary"),
        }
    }
