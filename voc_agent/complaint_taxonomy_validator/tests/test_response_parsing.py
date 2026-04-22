from __future__ import annotations

from voc_agent.share.utils import parse_json_payload_once


def test_parse_json_payload_once_recovers_json_wrapped_in_extra_text() -> None:
    raw_text = """
说明如下
```json
{
  "summary": "ok",
  "primary_category": {
    "code": "A",
    "full_name": "B",
    "confidence": 0.9,
    "reason": "x"
  },
  "candidate_categories": [],
  "candidate_tags": [],
  "category_keywords": [],
  "tag_keywords": [],
  "risks": []
}
```
后续说明
"""

    parsed = parse_json_payload_once(raw_text)

    assert parsed["summary"] == "ok"
