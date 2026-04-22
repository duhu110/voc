from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from voc_agent.converger_agent.persistence import run_converger_and_persist  # noqa: E402

SAMPLE_TICKET_ID = "WeComQH20240601125916780935"


def main() -> None:
    result = run_converger_and_persist(SAMPLE_TICKET_ID)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
