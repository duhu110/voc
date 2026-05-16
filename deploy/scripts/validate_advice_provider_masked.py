#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import text


def find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for path in [current.parent, *current.parents]:
        if (path / "pyproject.toml").exists() and (path / "voc_agent").exists():
            return path
    raise RuntimeError("Could not find project root containing pyproject.toml and voc_agent")


REPO_ROOT = find_repo_root()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from voc_agent.advice_provider_agent.provider import run_advice_provider  # noqa: E402
from voc_agent.core.db import get_engine  # noqa: E402


VALIDATION_CANDIDATES_SQL = text(
    """
    select
      s.source_ticket_id,
      s.primary_leaf_code,
      s.primary_leaf_name,
      s.product_tag_code,
      s.product_tag_name,
      s.request_tag_code,
      s.request_tag_name,
      s.resolution_summary,
      count(a.id) as advice_count,
      max(a.source_summary_count) as source_summary_count
    from converger_resolution_summary_atomic s
    join converger_handling_advice a
      on a.status = 'active'
     and a.primary_leaf_code = s.primary_leaf_code
     and coalesce(a.product_tag_code, '') = coalesce(s.product_tag_code, '')
     and coalesce(a.request_tag_code, '') = coalesce(s.request_tag_code, '')
    where s.status = 'active'
      and s.resolution_summary is not null
      and btrim(s.resolution_summary) <> ''
    group by
      s.source_ticket_id,
      s.primary_leaf_code,
      s.primary_leaf_name,
      s.product_tag_code,
      s.product_tag_name,
      s.request_tag_code,
      s.request_tag_name,
      s.resolution_summary
    order by max(a.source_summary_count) desc, random()
    limit :sample_size
    """
)


def fetch_candidates(sample_size: int) -> list[dict[str, Any]]:
    with get_engine().connect() as conn:
        rows = conn.execute(VALIDATION_CANDIDATES_SQL, {"sample_size": sample_size}).mappings().all()
    return [dict(row) for row in rows]


def validate_one(candidate: dict[str, Any]) -> dict[str, Any]:
    result = run_advice_provider(
        candidate["source_ticket_id"],
        use_existing_classification=False,
        hide_processing_context=True,
        advice_limit=5,
        sample_limit=3,
    )
    classification = result["classification"]
    matched_advices = result["matched_advices"]
    checks = {
        "leaf_match": classification["primary_leaf_code"] == candidate["primary_leaf_code"],
        "product_match": classification["product_tag_code"] == candidate["product_tag_code"],
        "request_match": classification["request_tag_code"] == candidate["request_tag_code"],
        "has_exact_advice": bool(matched_advices) and matched_advices[0]["match_level"] == "exact",
    }
    checks["passes_basic_validation"] = (
        sum(
            [
                bool(checks["leaf_match"]),
                bool(checks["product_match"]),
                bool(checks["request_match"]),
            ]
        )
        >= 2
        and bool(checks["has_exact_advice"])
    )
    return {
        "ticket_id": candidate["source_ticket_id"],
        "expected": {
            "primary_leaf_code": candidate["primary_leaf_code"],
            "primary_leaf_name": candidate["primary_leaf_name"],
            "product_tag_code": candidate["product_tag_code"],
            "product_tag_name": candidate["product_tag_name"],
            "request_tag_code": candidate["request_tag_code"],
            "request_tag_name": candidate["request_tag_name"],
            "resolution_summary": candidate["resolution_summary"],
            "advice_count": candidate["advice_count"],
            "source_summary_count": candidate["source_summary_count"],
        },
        "actual": {
            "classification": classification,
            "confidence": result["confidence"],
            "needs_human_review": result["needs_human_review"],
            "matched_advice_titles": [item["advice_title"] for item in matched_advices],
            "first_match_level": matched_advices[0]["match_level"] if matched_advices else None,
        },
        "checks": checks,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate advice_provider_agent by hiding historical processing fields."
    )
    parser.add_argument("--sample-size", type=int, default=3)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    candidates = fetch_candidates(args.sample_size)
    if not candidates:
        raise SystemExit("No validation candidates found.")

    results = [validate_one(candidate) for candidate in candidates]
    passed = sum(1 for item in results if item["checks"]["passes_basic_validation"])
    print(json.dumps({"passed": passed, "total": len(results), "results": results}, ensure_ascii=False, indent=2, default=str))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
