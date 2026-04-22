from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from voc_agent.core.config import get_settings


MODEL_TEST_DIR = Path(__file__).resolve().parent
SAMPLE_PROMPT_PATH = MODEL_TEST_DIR.parent / "prompt_sample_2024121013451359982515.txt"
MODEL_LIST_PATH = MODEL_TEST_DIR / "model_list.text"
OUTPUT_DIR = MODEL_TEST_DIR / "output"
TARGET_MODEL_NAMES = [
    "Qwen3-Coder-480B-A35B",
    "Qwen3-235B-A22B",
    "DeepSeek-V3.2",
    "Qwen3-Max",
    "Doubao-Seed-2.0-pro",
]

SYSTEM_PROMPT_MARKER = "===== SYSTEM PROMPT ====="
USER_PROMPT_MARKER = "===== USER PROMPT ====="
ORIGINAL_TICKET_MARKER = "【原始工单】"
CATEGORY_MARKER = "【可选分类清单】"


@dataclass(frozen=True)
class PromptCase:
    name: str
    system_prompt: str
    user_prompt: str


def parse_model_ids(raw_text: str) -> list[str]:
    return re.findall(r"id='([^']+)'", raw_text)


def build_prompt_cases(sample_path: Path) -> list[PromptCase]:
    sample_text = sample_path.read_text(encoding="utf-8")
    system_prompt, user_prompt = extract_prompt_sections(sample_text)
    base_ticket = extract_ticket_json(user_prompt)

    cases: list[PromptCase] = []
    for case_name, ticket in build_ticket_variants(base_ticket):
        cases.append(
            PromptCase(
                name=case_name,
                system_prompt=system_prompt,
                user_prompt=replace_ticket_json(user_prompt, ticket),
            )
        )
    return cases


def write_result_artifact(output_dir: Path, payload: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_name = "__".join(
        [
            sanitize_filename(str(payload.get("case_name", "case"))),
            sanitize_filename(str(payload.get("model_name", "model"))),
            sanitize_filename(str(payload.get("status", "result"))),
            sanitize_filename(str(payload.get("timestamp", "time")).replace(":", "-")),
        ]
    )
    artifact_path = output_dir / f"{artifact_name}.json"
    artifact_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return artifact_path


def run_model_suite(
    model_list_path: Path = MODEL_LIST_PATH,
    sample_path: Path = SAMPLE_PROMPT_PATH,
    output_dir: Path = OUTPUT_DIR,
    timeout_seconds: float = 90.0,
) -> dict[str, Any]:
    from openai import OpenAI

    settings = get_settings()
    client = OpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        timeout=timeout_seconds,
    )

    model_ids = select_target_models(
        parse_model_ids(model_list_path.read_text(encoding="utf-8")),
        TARGET_MODEL_NAMES,
    )
    prompt_cases = build_prompt_cases(sample_path)
    prompt_paths = {
        case.name: write_prompt_artifact(output_dir, case)
        for case in prompt_cases
    }

    summary: dict[str, Any] = {
        "timestamp": current_timestamp(),
        "model_list_path": str(model_list_path),
        "sample_path": str(sample_path),
        "output_dir": str(output_dir),
        "total_models": len(model_ids),
        "total_cases": len(prompt_cases),
        "total_requests": len(model_ids) * len(prompt_cases),
        "success_count": 0,
        "failure_count": 0,
        "json_valid_count": 0,
        "schema_valid_count": 0,
        "failures": [],
        "artifacts": [],
        "models": model_ids,
        "per_model": {},
    }

    for model_name in model_ids:
        summary["per_model"][model_name] = {
            "total_requests": 0,
            "success_count": 0,
            "failure_count": 0,
            "json_valid_count": 0,
            "schema_valid_count": 0,
            "durations_ms": [],
        }
        for case in prompt_cases:
            started_at = time.perf_counter()
            timestamp = current_timestamp()
            prompt_path = str(prompt_paths[case.name])
            summary["per_model"][model_name]["total_requests"] += 1
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": case.system_prompt},
                        {"role": "user", "content": case.user_prompt},
                    ],
                )
                duration_ms = int((time.perf_counter() - started_at) * 1000)
                response_text = extract_response_text(response)
                validation = validate_json_response(response_text)
                payload = {
                    "case_name": case.name,
                    "model_name": model_name,
                    "prompt_path": prompt_path,
                    "status": "success",
                    "error_type": None,
                    "error_message": None,
                    "duration_ms": duration_ms,
                    "timestamp": timestamp,
                    "response_id": getattr(response, "id", None),
                    "response_text": response_text,
                    "finish_reason": extract_finish_reason(response),
                    "usage": extract_usage(response),
                    "json_validation": validation,
                }
                artifact_path = write_result_artifact(output_dir, payload)
                summary["success_count"] += 1
                summary["per_model"][model_name]["success_count"] += 1
                summary["per_model"][model_name]["durations_ms"].append(duration_ms)
                if validation["is_json_object"]:
                    summary["json_valid_count"] += 1
                    summary["per_model"][model_name]["json_valid_count"] += 1
                if validation["schema_valid"]:
                    summary["schema_valid_count"] += 1
                    summary["per_model"][model_name]["schema_valid_count"] += 1
                summary["artifacts"].append(str(artifact_path))
            except Exception as exc:  # noqa: BLE001
                duration_ms = int((time.perf_counter() - started_at) * 1000)
                payload = {
                    "case_name": case.name,
                    "model_name": model_name,
                    "prompt_path": prompt_path,
                    "status": classify_failure_status(exc),
                    "error_type": exc.__class__.__name__,
                    "error_message": str(exc),
                    "duration_ms": duration_ms,
                    "timestamp": timestamp,
                }
                artifact_path = write_result_artifact(output_dir, payload)
                summary["failure_count"] += 1
                summary["per_model"][model_name]["failure_count"] += 1
                summary["per_model"][model_name]["durations_ms"].append(duration_ms)
                summary["failures"].append(payload)
                summary["artifacts"].append(str(artifact_path))

    for model_name, model_summary in summary["per_model"].items():
        durations = model_summary.pop("durations_ms")
        model_summary["avg_duration_ms"] = (
            int(sum(durations) / len(durations)) if durations else None
        )

    summary_path = write_summary_artifact(output_dir, summary)
    summary["summary_path"] = str(summary_path)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def extract_prompt_sections(sample_text: str) -> tuple[str, str]:
    system_start = sample_text.index(SYSTEM_PROMPT_MARKER) + len(SYSTEM_PROMPT_MARKER)
    user_start = sample_text.index(USER_PROMPT_MARKER)

    system_prompt = sample_text[system_start:user_start].strip()
    user_prompt = sample_text[user_start + len(USER_PROMPT_MARKER) :].strip()
    return system_prompt, user_prompt


def extract_ticket_json(user_prompt: str) -> dict[str, Any]:
    pattern = re.compile(
        rf"{re.escape(ORIGINAL_TICKET_MARKER)}\s*(\{{.*?\}})\s*{re.escape(CATEGORY_MARKER)}",
        re.DOTALL,
    )
    match = pattern.search(user_prompt)
    if match is None:
        raise ValueError("Unable to find original ticket JSON in sample prompt")
    return json.loads(match.group(1))


def replace_ticket_json(user_prompt: str, ticket: dict[str, Any]) -> str:
    ticket_json = json.dumps(ticket, ensure_ascii=False, indent=2)
    pattern = re.compile(
        rf"({re.escape(ORIGINAL_TICKET_MARKER)}\s*)(\{{.*?\}})(\s*{re.escape(CATEGORY_MARKER)})",
        re.DOTALL,
    )
    updated_prompt, replacements = pattern.subn(rf"\1{ticket_json}\3", user_prompt, count=1)
    if replacements != 1:
        raise ValueError("Unable to replace original ticket JSON in sample prompt")
    return updated_prompt


def build_ticket_variants(base_ticket: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    base_case = dict(base_ticket)

    channel_case = dict(base_ticket)
    channel_case.update(
        {
            "ticket_id": "CASE_CHANNEL_DENY_001",
            "accept_channel": "城东合作营业厅",
            "biz_content": (
                "客户表示在合作营业厅办理宽带时被顺带办理天翼云盘黄金会员合约包，"
                "本人未明确同意，要求立即取消业务、退回已扣费用，并追查渠道办理责任。"
            ),
            "return_reason": "留单原因->业务规则->业务办理规则->渠道办理争议->",
        }
    )

    renew_case = dict(base_ticket)
    renew_case.update(
        {
            "ticket_id": "CASE_AUTO_RENEW_001",
            "biz_category": "自动续订争议",
            "appeal_biz_type": "11.要求取消业务",
            "dispute_product_name": "视频会员连续包月",
            "complaint_phenomenon": "服务请求->投诉单->营销服务类->自动续订争议",
            "biz_content": (
                "客户反映视频会员试用到期后自动转为连续包月，未收到明确提醒，"
                "已连续扣费3个月，每月19元，要求立即取消并退回相关费用。"
            ),
            "return_reason": "留单原因->业务规则->自动续订规则->客户不认可->",
        }
    )

    billing_case = dict(base_ticket)
    billing_case.update(
        {
            "ticket_id": "CASE_BILLING_REFUND_001",
            "biz_category": "账单争议",
            "appeal_biz_type": "09.要求退费",
            "dispute_product_name": "天翼云盘黄金会员",
            "complaint_phenomenon": "服务请求->投诉单->账务服务类->账单争议",
            "biz_content": (
                "客户称本月账单出现两笔会员扣费，其中一笔为历史已取消业务，"
                "认为存在重复计费，要求核查账单明细并退回多收费用。"
            ),
            "return_reason": "留单原因->账务规则->账单金额异常->",
        }
    )

    network_case = dict(base_ticket)
    network_case.update(
        {
            "ticket_id": "CASE_NETWORK_QUALITY_001",
            "biz_category": "网络质量问题",
            "appeal_biz_type": "07.要求尽快处理",
            "dispute_product_name": "5G移动业务",
            "accept_channel": "10000号",
            "complaint_phenomenon": "服务请求->投诉单->网络通信类->网速质量问题",
            "biz_content": (
                "客户反映家庭住宅内近一周5G网络持续无信号或网速极慢，"
                "影响工作视频会议，已多次反馈未解决，要求尽快处理并给出解释。"
            ),
            "return_reason": "留单原因->网络服务->信号覆盖问题->",
        }
    )

    return [
        ("base_deny_order", base_case),
        ("channel_deny_order", channel_case),
        ("auto_renew_dispute", renew_case),
        ("billing_refund_dispute", billing_case),
        ("network_quality_escalation", network_case),
    ]


def sanitize_filename(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
    return sanitized or "artifact"


def select_target_models(available_models: list[str], requested_models: list[str]) -> list[str]:
    selected: list[str] = []
    for requested in requested_models:
        if requested in available_models:
            selected.append(requested)
            continue

        prefix_matches = [model for model in available_models if model.startswith(requested)]
        if len(prefix_matches) == 1:
            selected.append(prefix_matches[0])
            continue

        raise ValueError(f"Unable to resolve requested model '{requested}' from model list")

    return selected


def validate_json_response(response_text: str) -> dict[str, Any]:
    required_keys = {
        "summary",
        "primary_category",
        "candidate_categories",
        "candidate_tags",
        "category_keywords",
        "tag_keywords",
        "risks",
    }
    primary_category_keys = {"code", "full_name", "confidence", "reason"}

    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError as exc:
        return {
            "is_json_object": False,
            "required_keys_valid": False,
            "primary_category_valid": False,
            "schema_valid": False,
            "parse_error": str(exc),
        }

    is_json_object = isinstance(parsed, dict)
    required_keys_valid = is_json_object and required_keys.issubset(parsed.keys())
    primary_category = parsed.get("primary_category") if is_json_object else None
    primary_category_valid = (
        isinstance(primary_category, dict)
        and primary_category_keys.issubset(primary_category.keys())
    )
    return {
        "is_json_object": is_json_object,
        "required_keys_valid": required_keys_valid,
        "primary_category_valid": primary_category_valid,
        "schema_valid": bool(required_keys_valid and primary_category_valid),
        "parse_error": None,
    }


def write_prompt_artifact(output_dir: Path, prompt_case: PromptCase) -> Path:
    prompt_dir = output_dir / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = prompt_dir / f"{sanitize_filename(prompt_case.name)}.txt"
    content = (
        "===== SYSTEM PROMPT =====\n"
        f"{prompt_case.system_prompt}\n\n"
        "===== USER PROMPT =====\n"
        f"{prompt_case.user_prompt}\n"
    )
    prompt_path.write_text(content, encoding="utf-8")
    return prompt_path


def write_summary_artifact(output_dir: Path, summary: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = sanitize_filename(str(summary["timestamp"]).replace(":", "-"))
    return output_dir / f"summary__{timestamp}.json"


def current_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def classify_failure_status(exc: Exception) -> str:
    text = f"{exc.__class__.__name__} {exc}".lower()
    if "timeout" in text:
        return "timeout"
    return "failed"


def extract_response_text(response: Any) -> str:
    choices = getattr(response, "choices", None) or []
    if not choices:
        return ""

    message = getattr(choices[0], "message", None)
    if message is None:
        return ""

    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else getattr(part, "text", "")
            for part in content
        )
    return str(content)


def extract_finish_reason(response: Any) -> str | None:
    choices = getattr(response, "choices", None) or []
    if not choices:
        return None
    return getattr(choices[0], "finish_reason", None)


def extract_usage(response: Any) -> dict[str, Any] | None:
    usage = getattr(response, "usage", None)
    if usage is None:
        return None
    if hasattr(usage, "model_dump"):
        return usage.model_dump(mode="json")
    if isinstance(usage, dict):
        return usage
    return {
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }
