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


TAXONOMY = {
    "FEE_BILLING": {
        "PACKAGE_AND_USAGE_FEE": [
            "套餐收费争议",
            "套外使用费用争议",
            "增值业务收费争议",
            "异常扣费/不明收费",
            "宽带/电视收费争议",
        ],
        "ACCOUNT_AND_PAYMENT": [
            "账单金额/展示异常",
            "充值缴费异常",
            "发票问题",
        ],
        "REFUND_PENALTY_RIGHTS": [
            "返费/赠费/退款未到账",
            "翼支付权益/费用争议",
            "违约金/滞纳金争议",
        ],
    },
    "SUBSCRIBE_CANCEL": {
        "ORDER_AND_DENY": [
            "用户否认订购",
            "订购办理争议",
            "自动续订争议",
        ],
        "CANCEL_AND_UNSUBSCRIBE": [
            "业务退订/取消争议",
            "业务退订/取消失败",
            "退订后仍收费",
        ],
        "PLAN_CHANGE_AND_ACCOUNT_CLOSE": [
            "套餐变更争议",
            "拆机销户争议",
            "销户后仍计费/销户规则争议",
        ],
    },
    "OPEN_RECOVERY_CONTROL": {
        "OPEN_AND_ACTIVATION": [
            "业务开通失败",
            "号卡开通失败",
            "宽带开通失败",
            "激活/实名认证异常",
        ],
        "SHUTDOWN_AND_CONTROL": [
            "欠费停机不认可",
            "风险/模型关停不认可",
            "屏蔽/解限问题",
        ],
        "RECOVERY_AND_UNBLOCK": [
            "复机/恢复失败或不及时",
        ],
    },
    "MARKETING_SALES": {
        "EXPLAIN_AND_COMMITMENT": [
            "宣传/解释不清或误导",
            "承诺未兑现",
            "赠品/权益未兑现",
        ],
        "SALES_PROCESS_AND_ATTITUDE": [
            "业务办理差错/漏受理",
            "业务办理不畅",
            "服务态度问题",
        ],
    },
    "RULE_POLICY": {
        "ACTIVITY_AND_EFFECTIVE_RULE": [
            "营销活动规则争议",
            "生效/失效规则争议",
        ],
        "USAGE_AND_LIMIT_RULE": [
            "达量降速/限速规则争议",
            "权益/流量使用范围争议",
            "合约限制争议",
        ],
        "QUALIFICATION_AND_PROCESS_RULE": [
            "资格条件/实名规则争议",
            "代办/流程规则争议",
        ],
    },
    "PRODUCT_PLATFORM": {
        "BASIC_FUNCTION": [
            "语音功能异常",
            "短信功能异常",
            "流量功能异常",
            "产品功能缺失/不稳定",
        ],
        "APP_AND_ACCOUNT": [
            "APP/网厅报错或线上办理失败",
            "账号登录/身份校验异常",
        ],
        "QUERY_AND_DISPLAY": [
            "订单/套餐/信息查询展示异常",
            "网站/平台/客户端软件问题",
        ],
    },
    "NETWORK_QUALITY": {
        "NETWORK_QUALITY": [
            "无信号/信号弱",
            "移动上网慢",
            "宽带网速慢",
            "宽带掉线/网络不稳定",
            "通话质量异常",
            "漫游通信异常",
        ]
    },
    "INSTALL_DELIVERY": {
        "INSTALL_TIMELINESS": [
            "履约不及时/未履约",
            "催装移机",
        ],
        "INSTALL_STANDARD_AND_RESULT": [
            "上门服务不规范",
            "安装施工质量问题",
            "施工损坏问题",
            "交付结果不符/实测速率不达标",
        ],
    },
    "SERVICE_PROCESS": {
        "COMPLAINT_HANDLING": [
            "久拖未决/重复投诉处理不满意",
            "处理结果不认可",
        ],
        "WORK_ORDER_FLOW": [
            "工单流转/转派错误/多部门扯皮",
        ],
        "SPECIAL_REPORT_AND_MANAGER": [
            "客户经理协调/业务核实",
            "查询申请代理资料",
            "举报骚扰/诈骗电话",
            "举报不良信息/第三方平台标记错误",
            "建议表扬",
        ],
    },
}

SAMPLES = [
    {
        "ticket_id": "WeComQH20240802101714527035",
        "expected_level1_code": "INSTALL_DELIVERY",
        "expected_level2_code": "INSTALL_STANDARD_AND_RESULT",
        "expected_leaf_name": "上门服务不规范",
        "manual_reason": "装维已上门，但只给出“没有资源无法安装”的模糊解释，核心是上门交付解释与服务规范问题。",
    },
    {
        "ticket_id": "WeComQH20240728095528188566",
        "expected_level1_code": "MARKETING_SALES",
        "expected_level2_code": "EXPLAIN_AND_COMMITMENT",
        "expected_leaf_name": "赠品/权益未兑现",
        "manual_reason": "办理套餐时承诺免费赠送监控，但一直未安装，核心是承诺赠品未兑现。",
    },
    {
        "ticket_id": "WeComQH20240714184406787934",
        "expected_level1_code": "RULE_POLICY",
        "expected_level2_code": "ACTIVITY_AND_EFFECTIVE_RULE",
        "expected_leaf_name": "营销活动规则争议",
        "manual_reason": "用户办理礼包后会员权益无法使用，主问题更像活动权益兑现规则争议。",
    },
    {
        "ticket_id": "WeComQH20240713102056192380",
        "expected_level1_code": "SUBSCRIBE_CANCEL",
        "expected_level2_code": "CANCEL_AND_UNSUBSCRIBE",
        "expected_leaf_name": "业务退订/取消失败",
        "manual_reason": "用户明确要求取消连续包月业务，但系统带出异常属性导致取消不成功，核心是退订失败。",
    },
    {
        "ticket_id": "WeComQH20240712180131851489",
        "expected_level1_code": "SUBSCRIBE_CANCEL",
        "expected_level2_code": "ORDER_AND_DENY",
        "expected_leaf_name": "用户否认订购",
        "manual_reason": "用户对芒果TV会员权益费用不认可并明确否认订购，核心是订购关系不认可。",
    },
    {
        "ticket_id": "WeComQH20240604105832012251",
        "expected_level1_code": "FEE_BILLING",
        "expected_level2_code": "ACCOUNT_AND_PAYMENT",
        "expected_leaf_name": "充值缴费异常",
        "manual_reason": "用户缴费 200 元中有 100 元被冲正并导致宽带欠费停机，核心是缴费结果异常。",
    },
    {
        "ticket_id": "WeComQH20240531105149107161",
        "expected_level1_code": "OPEN_RECOVERY_CONTROL",
        "expected_level2_code": "RECOVERY_AND_UNBLOCK",
        "expected_leaf_name": "复机/恢复失败或不及时",
        "manual_reason": "用户已到营业厅申请复机，但公安双停后仍未恢复，核心是恢复失败或不及时。",
    },
    {
        "ticket_id": "WeComQH20240521091329931527",
        "expected_level1_code": "MARKETING_SALES",
        "expected_level2_code": "SALES_PROCESS_AND_ATTITUDE",
        "expected_leaf_name": "业务办理差错/漏受理",
        "manual_reason": "办理入网时承诺将旧号携转进套餐但迟迟没办成，核心是办理差错或漏受理。",
    },
    {
        "ticket_id": "WeComQH20240524112207679068",
        "expected_level1_code": "FEE_BILLING",
        "expected_level2_code": "REFUND_PENALTY_RIGHTS",
        "expected_leaf_name": "返费/赠费/退款未到账",
        "manual_reason": "拆机后一直未退费，核心是退款未到账。",
    },
    {
        "ticket_id": "WeComQH20240524185814517932",
        "expected_level1_code": "MARKETING_SALES",
        "expected_level2_code": "EXPLAIN_AND_COMMITMENT",
        "expected_leaf_name": "宣传/解释不清或误导",
        "manual_reason": "办理融合套餐时未解释清楚携号转网副卡加入方式，导致后续上网费产生，核心是解释不清。",
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate final v2 taxonomy on another 10 real tickets.")
    parser.add_argument(
        "--output-markdown",
        default=str(REPO_ROOT / "docs" / "converger_design" / "taxonomy_v2_final_round5_report.md"),
        help="Markdown report output path.",
    )
    parser.add_argument(
        "--output-json",
        default=str(REPO_ROOT / "docs" / "converger_design" / "taxonomy_v2_final_round5_report.json"),
        help="JSON report output path.",
    )
    return parser


def compact_ticket(ticket: dict) -> dict:
    return {key: ticket.get(key) for key in TICKET_KEYS if ticket.get(key) not in (None, "", [])}


def build_leaf_catalog() -> list[dict]:
    rows: list[dict] = []
    for level1_code, level2_map in TAXONOMY.items():
        for level2_code, leaves in level2_map.items():
            for leaf_name in leaves:
                rows.append(
                    {
                        "level1_code": level1_code,
                        "level2_code": level2_code,
                        "leaf_name": leaf_name,
                    }
                )
    return rows


def build_prompt(ticket: dict) -> str:
    lines = [f"- [{row['level1_code']}] / [{row['level2_code']}] / {row['leaf_name']}" for row in build_leaf_catalog()]
    ticket_payload = json.dumps(compact_ticket(ticket), ensure_ascii=False, indent=2)
    return f"""请根据下面工单内容，从给定的最终版 V2 分类体系中只选择 1 个最合适的叶子分类。

要求：
1. 只能从下面给定的叶子分类中选择。
2. 不要参考旧分类编码或旧分类名称。
3. 重点识别工单的核心问题，不要被诉求标签带偏。
4. 如果工单核心是客户经理联系、核实、举报、资料查询等流程诉求，应优先考虑 SERVICE_PROCESS。
5. 如果工单核心是网络表现问题，归 NETWORK_QUALITY；如果核心是履约、上门、交付过程问题，归 INSTALL_DELIVERY。
6. 如果工单核心是用户否认曾订购某业务，应优先考虑 SUBSCRIBE_CANCEL / ORDER_AND_DENY。
7. 如果工单核心是规则口径、达量降速、是否继续收费，应优先考虑 RULE_POLICY / USAGE_AND_LIMIT_RULE，而不是费用金额本身。
8. 如果工单最终诉求是开具发票、补开发票、发票金额/获取异常，优先归发票问题。
9. 输出必须是纯 JSON。

返回结构：
{{
  "summary": "...",
  "level1_code": "...",
  "level2_code": "...",
  "leaf_name": "...",
  "reason": "..."
}}

【工单】
{ticket_payload}

【可选叶子分类】
{chr(10).join(lines)}
"""


def classify_ticket(client: OpenAI, model: str, ticket: dict) -> dict:
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": "你是运营商投诉分类专家。你只能在给定的 V2 最终版叶子分类中选 1 个最合适的主分类。"},
            {"role": "user", "content": build_prompt(ticket)},
        ],
    )
    content = response.choices[0].message.content or "{}"
    return parse_json_payload_once(content)


def compare_result(sample: dict, actual: dict) -> dict:
    return {
        "level1_match": sample["expected_level1_code"] == actual.get("level1_code"),
        "level2_match": sample["expected_level2_code"] == actual.get("level2_code"),
        "leaf_match": sample["expected_leaf_name"] == actual.get("leaf_name"),
    }


def build_markdown(results: list[dict], model_name: str) -> str:
    total = len(results)
    level1_hits = sum(1 for item in results if item["comparison"]["level1_match"])
    level2_hits = sum(1 for item in results if item["comparison"]["level2_match"])
    leaf_hits = sum(1 for item in results if item["comparison"]["leaf_match"])
    lines = [
        "# V2 Final 第五轮真实样本验证报告",
        "",
        f"- 模型：`{model_name}`",
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
                f"- 人工判断：`{expected['expected_level1_code']} / {expected['expected_level2_code']} / {expected['expected_leaf_name']}`",
                f"- AI 判断：`{actual.get('level1_code')} / {actual.get('level2_code')} / {actual.get('leaf_name')}`",
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
                f"- `{item['ticket_id']}`: 人工=`{item['expected']['expected_leaf_name']}`，AI=`{item['actual'].get('leaf_name')}`"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = build_parser().parse_args()
    settings = get_settings()
    client = OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)

    results = []
    for sample in SAMPLES:
        ticket = fetch_ticket(sample["ticket_id"])
        actual = classify_ticket(client, settings.llm_model_name, ticket)
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
        "sample_count": len(results),
        "level1_match_count": sum(1 for item in results if item["comparison"]["level1_match"]),
        "level2_match_count": sum(1 for item in results if item["comparison"]["level2_match"]),
        "leaf_match_count": sum(1 for item in results if item["comparison"]["leaf_match"]),
        "results": results,
    }

    output_json = Path(args.output_json)
    output_md = Path(args.output_markdown)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    output_md.write_text(build_markdown(results, settings.llm_model_name), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
