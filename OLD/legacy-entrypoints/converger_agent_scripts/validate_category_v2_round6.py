from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from openai import OpenAI

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from voc_agent.core.config import get_settings
from voc_agent.share.tools import fetch_ticket
from voc_agent.share.utils import parse_json_payload_once


DATA_DIR = REPO_ROOT / "voc_agent" / "converger_agent" / "data"
CATEGORY_FILE = DATA_DIR / "category_v2.json"

SAMPLES = [
    {
        "ticket_id": "WeComQH20240802101714527035",
        "expected_level1_code": "INSTALL_DELIVERY",
        "expected_level2_code": "INSTALL_STANDARD_AND_RESULT",
        "expected_leaf_code": "ONSITE_SERVICE_IRREGULAR",
        "manual_reason": "装维已上门，但没有解释清楚“没有资源无法安装”，核心是上门服务不规范。",
    },
    {
        "ticket_id": "WeComQH20240728095528188566",
        "expected_level1_code": "MARKETING_SALES",
        "expected_level2_code": "EXPLAIN_AND_COMMITMENT",
        "expected_leaf_code": "PROMISE_NOT_FULFILLED",
        "manual_reason": "工作人员承诺免费赠送监控但最终未兑现，按已确认规则优先归承诺未兑现。",
    },
    {
        "ticket_id": "WeComQH20240714184406787934",
        "expected_level1_code": "MARKETING_SALES",
        "expected_level2_code": "EXPLAIN_AND_COMMITMENT",
        "expected_leaf_code": "BENEFIT_NOT_DELIVERED",
        "manual_reason": "用户感知是礼包里的腾讯视频会员权益拿不到、不能用，按已确认规则优先归赠品/权益未兑现。",
    },
    {
        "ticket_id": "WeComQH20240713102056192380",
        "expected_level1_code": "SUBSCRIBE_CANCEL",
        "expected_level2_code": "CANCEL_AND_UNSUBSCRIBE",
        "expected_leaf_code": "CANCEL_FAILURE",
        "manual_reason": "用户明确要求取消连续包月业务，但系统异常导致取消不成功，核心是退订失败。",
    },
    {
        "ticket_id": "WeComQH20240712180131851489",
        "expected_level1_code": "SUBSCRIBE_CANCEL",
        "expected_level2_code": "ORDER_AND_DENY",
        "expected_leaf_code": "ORDER_DENIAL",
        "manual_reason": "用户对芒果TV会员权益费用不认可并明确否认订购，核心是订购关系不认可。",
    },
    {
        "ticket_id": "WeComQH20240604105832012251",
        "expected_level1_code": "FEE_BILLING",
        "expected_level2_code": "ACCOUNT_AND_PAYMENT",
        "expected_leaf_code": "PAYMENT_RECHARGE_ISSUE",
        "manual_reason": "缴费后部分金额被冲正并导致欠费停机，核心是充值缴费异常。",
    },
    {
        "ticket_id": "WeComQH20240531105149107161",
        "expected_level1_code": "OPEN_RECOVERY_CONTROL",
        "expected_level2_code": "RECOVERY_AND_UNBLOCK",
        "expected_leaf_code": "RECOVERY_DELAY_OR_FAILURE",
        "manual_reason": "已到营业厅申请复机，但仍未恢复，核心是复机/恢复失败或不及时。",
    },
    {
        "ticket_id": "WeComQH20240602101810654310",
        "expected_level1_code": "FEE_BILLING",
        "expected_level2_code": "REFUND_PENALTY_RIGHTS",
        "expected_leaf_code": "REFUND_NOT_ARRIVED",
        "manual_reason": "拆机后承诺退设备调测费但一直未退，核心是退款未到账。",
    },
    {
        "ticket_id": "WeComQH20240601125916780935",
        "expected_level1_code": "MARKETING_SALES",
        "expected_level2_code": "EXPLAIN_AND_COMMITMENT",
        "expected_leaf_code": "MISLEADING_EXPLANATION",
        "manual_reason": "业务是办过的，但办理时未告知合约，按已确认规则优先归宣传/解释不清或误导。",
    },
    {
        "ticket_id": "WeComQH20240525115416670531",
        "expected_level1_code": "SUBSCRIBE_CANCEL",
        "expected_level2_code": "ORDER_AND_DENY",
        "expected_leaf_code": "ORDER_DENIAL",
        "manual_reason": "用户称自己没有订购过彩铃费用相关业务，核心是用户否认订购。",
    },
]

TICKET_KEYS = [
    "ticket_id",
    "ticket_type",
    "complaint_source",
    "biz_category",
    "line_category",
    "appeal_biz_type",
    "dispute_product_name",
    "customer_star",
    "repeat_count",
    "urge_count",
    "oscillation_count",
    "satisfaction_score",
    "complaint_phenomenon",
    "biz_content",
    "return_reason",
    "prov_dispatch_desc",
    "prov_process_desc",
    "city_process_desc",
    "process_dept",
    "flow_depts",
]


def load_category_data() -> dict:
    return json.loads(CATEGORY_FILE.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate converger_agent category_v2.json on 10 real tickets.")
    parser.add_argument(
        "--output-markdown",
        default=str(REPO_ROOT / "docs" / "converger_design" / "taxonomy_v2_json_round6_report.md"),
        help="Markdown report output path.",
    )
    parser.add_argument(
        "--output-json",
        default=str(REPO_ROOT / "docs" / "converger_design" / "taxonomy_v2_json_round6_report.json"),
        help="JSON report output path.",
    )
    return parser


def compact_ticket(ticket: dict) -> dict:
    return {key: ticket.get(key) for key in TICKET_KEYS if ticket.get(key) not in (None, "", [])}


def build_leaf_catalog(category_data: dict) -> list[dict]:
    rows: list[dict] = []
    for leaf_code, leaf in category_data["leaves"].items():
        rows.append(
            {
                "leaf_code": leaf_code,
                "level1_code": leaf["parent_level1_code"],
                "level2_code": leaf["parent_level2_code"],
                "leaf_name": leaf["name"],
                "leaf_desc": leaf["desc"],
            }
        )
    rows.sort(key=lambda row: (row["level1_code"], row["level2_code"], row["leaf_code"]))
    return rows


def build_prompt(ticket: dict, category_data: dict) -> str:
    lines = []
    for row in build_leaf_catalog(category_data):
        lines.append(
            f"- [{row['level1_code']}] / [{row['level2_code']}] / [{row['leaf_code']}] / {row['leaf_name']}：{row['leaf_desc']}"
        )

    rule_lines = []
    for rule in category_data["disambiguation_rules"]:
        note = rule.get("note")
        if note:
            rule_lines.append(f"- {rule['rule_id']}: {note}")

    ticket_payload = json.dumps(compact_ticket(ticket), ensure_ascii=False, indent=2)
    return f"""请根据下面工单内容，从给定的 category_v2.json 分类体系中只选择 1 个最合适的叶子分类。

要求：
1. 只能从给定叶子分类中选择。
2. 输出必须严格参考 leaf_code、level1_code、level2_code。
3. 不要参考旧分类编码或旧分类名称。
4. 优先遵守给定的歧义规则。
5. 输出必须是纯 JSON。

返回结构：
{{
  "summary": "...",
  "level1_code": "...",
  "level2_code": "...",
  "leaf_code": "...",
  "leaf_name": "...",
  "reason": "..."
}}

【工单】
{ticket_payload}

【歧义规则】
{chr(10).join(rule_lines)}

【可选叶子分类】
{chr(10).join(lines)}
"""


def classify_ticket(client: OpenAI, model: str, ticket: dict, category_data: dict) -> dict:
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": "你是运营商投诉分类专家。你只能在给定的 JSON 分类体系中选 1 个最合适的主分类。"},
            {"role": "user", "content": build_prompt(ticket, category_data)},
        ],
    )
    content = response.choices[0].message.content or "{}"
    return parse_json_payload_once(content)


def compare_result(sample: dict, actual: dict) -> dict:
    return {
        "level1_match": sample["expected_level1_code"] == actual.get("level1_code"),
        "level2_match": sample["expected_level2_code"] == actual.get("level2_code"),
        "leaf_match": sample["expected_leaf_code"] == actual.get("leaf_code"),
    }


def build_markdown(results: list[dict], model_name: str, category_path: str) -> str:
    total = len(results)
    level1_hits = sum(1 for item in results if item["comparison"]["level1_match"])
    level2_hits = sum(1 for item in results if item["comparison"]["level2_match"])
    leaf_hits = sum(1 for item in results if item["comparison"]["leaf_match"])
    lines = [
        "# category_v2.json 第六轮真实样本验证报告",
        "",
        f"- 模型：`{model_name}`",
        f"- 分类源：`{category_path}`",
        f"- 样本数：`{total}`",
        f"- 一级命中：`{level1_hits}/{total}`",
        f"- 二级命中：`{level2_hits}/{total}`",
        f"- 叶子命中：`{leaf_hits}/{total}`",
        "",
        "## 样本结果",
        "",
    ]
    for item in results:
        expected = item["expected"]
        actual = item["actual"]
        cmp = item["comparison"]
        lines.extend(
            [
                f"### {item['ticket_id']}",
                "",
                f"- 人工判断：`{expected['expected_level1_code']} / {expected['expected_level2_code']} / {expected['expected_leaf_code']}`",
                f"- AI 判断：`{actual.get('level1_code')} / {actual.get('level2_code')} / {actual.get('leaf_code')} / {actual.get('leaf_name')}`",
                f"- 命中情况：一级=`{cmp['level1_match']}`，二级=`{cmp['level2_match']}`，叶子=`{cmp['leaf_match']}`",
                f"- 人工理由：{expected['manual_reason']}",
                f"- AI 理由：{actual.get('reason', '')}",
                "",
            ]
        )
    mismatches = [item for item in results if not item["comparison"]["leaf_match"]]
    lines.extend(["## 失配观察", ""])
    if not mismatches:
        lines.append("- 当前样本未出现叶子失配。")
    else:
        for item in mismatches:
            lines.append(
                f"- `{item['ticket_id']}`: 人工=`{item['expected']['expected_leaf_code']}`，AI=`{item['actual'].get('leaf_code')}`"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = build_parser().parse_args()
    settings = get_settings()
    category_data = load_category_data()
    client = OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)

    results = []
    for sample in SAMPLES:
        ticket = fetch_ticket(sample["ticket_id"])
        actual = classify_ticket(client, settings.llm_model_name, ticket, category_data)
        results.append(
            {
                "ticket_id": sample["ticket_id"],
                "expected": sample,
                "actual": actual,
                "comparison": compare_result(sample, actual),
                "ticket": compact_ticket(ticket),
            }
        )

    summary = {
        "model_name": settings.llm_model_name,
        "category_source": str(CATEGORY_FILE),
        "sample_count": len(results),
        "level1_match_count": sum(1 for item in results if item["comparison"]["level1_match"]),
        "level2_match_count": sum(1 for item in results if item["comparison"]["level2_match"]),
        "leaf_match_count": sum(1 for item in results if item["comparison"]["leaf_match"]),
        "results": results,
    }

    output_json = Path(args.output_json)
    output_md = Path(args.output_markdown)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    output_md.write_text(build_markdown(results, settings.llm_model_name, str(CATEGORY_FILE)), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
