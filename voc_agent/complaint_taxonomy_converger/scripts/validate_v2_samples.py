from __future__ import annotations

import argparse
import json
import os
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
        "收费、账单、缴费与退款争议": {
            "PACKAGE_AND_USAGE_FEE": ["套餐收费争议", "套外流量费用争议", "套外通话费用争议", "漫游费用争议", "增值业务收费争议", "不明收费争议", "宽带/电视收费争议"],
            "ACCOUNT_AND_PAYMENT": ["账单金额异常", "余额/账单展示异常", "充值缴费未到账", "客户错充值缴费", "发票问题"],
            "REFUND_PENALTY_RIGHTS": ["返费/赠费/退款未到账", "翼支付权益金争议", "违约金争议", "滞纳金/历史欠费争议"],
        }
    },
    "SUBSCRIBE_CANCEL": {
        "订购、退订、变更、销户类问题": {
            "ORDER_AND_DENY": ["用户否认订购", "未明确同意订购", "业务办理/订购争议", "自动续订争议"],
            "CANCEL_AND_UNSUBSCRIBE": ["业务退订失败", "退订后仍收费", "业务退订争议"],
            "PLAN_CHANGE_AND_ACCOUNT_CLOSE": ["套餐变更争议", "拆机销户", "销户后仍计费", "销户规则争议"],
        }
    },
    "OPEN_RECOVERY_CONTROL": {
        "开通、停复机、限制与恢复类问题": {
            "OPEN_AND_ACTIVATION": ["业务开通失败", "号卡开通失败", "宽带开通失败", "激活异常", "实名认证异常"],
            "SHUTDOWN_AND_CONTROL": ["欠费停机不认可", "风险关停不认可", "模型关停不认可", "屏蔽/解限问题"],
            "RECOVERY_AND_UNBLOCK": ["复机失败", "复机不及时", "服务恢复失败"],
        }
    },
    "MARKETING_SALES": {
        "宣传、承诺、销售过程与服务态度问题": {
            "EXPLAIN_AND_MISLEADING": ["解释说明不清", "宣传错误/误导", "资费或规则解释不清"],
            "PROMISE_AND_DELIVERY": ["赠品/权益未兑现", "返费承诺未兑现", "速率能力未兑现"],
            "SALES_PROCESS_AND_ATTITUDE": ["业务办理差错", "漏受理", "业务办理不畅", "客服服务态度问题", "客户经理服务态度问题", "营业厅服务态度问题"],
        }
    },
    "RULE_POLICY": {
        "规则、资格、活动、生效使用政策类问题": {
            "ACTIVITY_AND_EFFECTIVE_RULE": ["营销活动规则争议", "套餐生效时间争议", "业务失效规则争议"],
            "USAGE_AND_LIMIT_RULE": ["达量降速/限速规则争议", "权益适用范围争议", "流量使用范围争议", "合约限制争议"],
            "QUALIFICATION_AND_PROCESS_RULE": ["资格条件争议", "实名制/一证五号规则争议", "代办规则争议", "办理流程规则争议"],
        }
    },
    "PRODUCT_PLATFORM": {
        "产品功能、APP/网厅、账号、展示查询类问题": {
            "BASIC_FUNCTION": ["语音功能异常", "短信功能异常", "流量功能异常", "产品基础功能缺失/不稳定"],
            "APP_AND_ACCOUNT": ["APP/网厅报错", "线上办理失败", "账号登录失败", "身份校验异常"],
            "QUERY_AND_DISPLAY": ["订单状态展示异常", "套餐信息展示异常", "查询展示异常", "网站/平台/客户端软件问题"],
        }
    },
    "NETWORK_QUALITY": {
        "信号、网速、通话、漫游、宽带网络质量问题": {
            "NETWORK_QUALITY": ["无信号", "信号弱/不稳定", "移动上网慢", "宽带网速慢", "宽带频繁掉线", "通话掉话/接通困难/杂音回声", "漫游通信异常"],
        }
    },
    "INSTALL_DELIVERY": {
        "装维、施工、交付、履约、催装移机类问题": {
            "INSTALL_TIMELINESS": ["宽带预约拆机处理不及时", "履约不及时/超时履约/未履约", "预约未上门", "超时未完成", "催装移机"],
            "INSTALL_STANDARD_AND_RESULT": ["上门服务不规范", "安装施工质量问题", "施工损坏问题", "交付结果不符", "实测速率不达标"],
        }
    },
    "SERVICE_PROCESS": {
        "投诉处理、工单流转、客户经理协调、举报与特殊服务流程问题": {
            "COMPLAINT_HANDLING": ["久拖未决", "处理结果不认可", "重复投诉处理不满意"],
            "WORK_ORDER_FLOW": ["工单超时未处理", "转派错误", "多部门扯皮", "工单流转问题"],
            "SPECIAL_REPORT_AND_MANAGER": ["要求联系客户经理", "查询申请代理资料", "举报骚扰电话", "举报不良信息", "第三方平台标记错误"],
        }
    },
}

SAMPLES = [
    {
        "ticket_id": "WeComQH20240705122615333767",
        "expected_level1_code": "MARKETING_SALES",
        "expected_level2_code": "SALES_PROCESS_AND_ATTITUDE",
        "expected_leaf_name": "业务办理差错",
        "manual_reason": "核心冲突是办理套餐变更时承诺取消业务但未执行，属于办理差错，不是纯规则争议。",
    },
    {
        "ticket_id": "WeComQH20240719134927637641",
        "expected_level1_code": "SUBSCRIBE_CANCEL",
        "expected_level2_code": "CANCEL_AND_UNSUBSCRIBE",
        "expected_leaf_name": "业务退订争议",
        "manual_reason": "客户核心诉求是取消合约业务，且反复要求退订。",
    },
    {
        "ticket_id": "6004052025113093773147",
        "expected_level1_code": "OPEN_RECOVERY_CONTROL",
        "expected_level2_code": "SHUTDOWN_AND_CONTROL",
        "expected_leaf_name": "风险关停不认可",
        "manual_reason": "业务核心是号码被高风险双停，客户不认可并要求恢复。",
    },
    {
        "ticket_id": "WeComQH20240811112847215417",
        "expected_level1_code": "PRODUCT_PLATFORM",
        "expected_level2_code": "BASIC_FUNCTION",
        "expected_leaf_name": "短信功能异常",
        "manual_reason": "天气预报短信一直收不到，属于短信功能异常。",
    },
    {
        "ticket_id": "WeComQH20240818143949898108",
        "expected_level1_code": "FEE_BILLING",
        "expected_level2_code": "PACKAGE_AND_USAGE_FEE",
        "expected_leaf_name": "不明收费争议",
        "manual_reason": "客户对新办套餐后突然欠费 8.2 元不认可，当前事实不足以判断具体是流量/通话/漫游，先归不明收费。",
    },
    {
        "ticket_id": "WeComQH20240730102638617626",
        "expected_level1_code": "FEE_BILLING",
        "expected_level2_code": "PACKAGE_AND_USAGE_FEE",
        "expected_leaf_name": "增值业务收费争议",
        "manual_reason": "家庭医生点播费用争议，本质是增值业务收费问题，不是套餐本身收费。",
    },
    {
        "ticket_id": "WeComQH20240825171749823808",
        "expected_level1_code": "INSTALL_DELIVERY",
        "expected_level2_code": "INSTALL_TIMELINESS",
        "expected_leaf_name": "履约不及时/超时履约/未履约",
        "manual_reason": "移机已办理但一直未上门安装，核心是履约超时。",
    },
    {
        "ticket_id": "WeComQH20240826150706758197",
        "expected_level1_code": "INSTALL_DELIVERY",
        "expected_level2_code": "INSTALL_TIMELINESS",
        "expected_leaf_name": "预约未上门",
        "manual_reason": "用户已预约拆机时间但无人上门，核心是预约未上门，而不是单纯销户。",
    },
    {
        "ticket_id": "WeComQH20240714163202760929",
        "expected_level1_code": "NETWORK_QUALITY",
        "expected_level2_code": "NETWORK_QUALITY",
        "expected_leaf_name": "宽带网速慢",
        "manual_reason": "工单直接描述宽带网速慢。",
    },
    {
        "ticket_id": "WeComQH20240714184406787934",
        "expected_level1_code": "MARKETING_SALES",
        "expected_level2_code": "PROMISE_AND_DELIVERY",
        "expected_leaf_name": "赠品/权益未兑现",
        "manual_reason": "礼包承诺的腾讯视频会员权益无法使用，更像权益未兑现，不是纯规则解释问题。",
    },
    {
        "ticket_id": "2025113014090756459513",
        "expected_level1_code": "SERVICE_PROCESS",
        "expected_level2_code": "SPECIAL_REPORT_AND_MANAGER",
        "expected_leaf_name": "要求联系客户经理",
        "manual_reason": "客户诉求就是要求客户经理联系核实业务。",
    },
    {
        "ticket_id": "WeComQH20240728095528188566",
        "expected_level1_code": "MARKETING_SALES",
        "expected_level2_code": "EXPLAIN_AND_MISLEADING",
        "expected_leaf_name": "宣传错误/误导",
        "manual_reason": "办理套餐时承诺赠送监控但系统无此业务，属于宣传/承诺误导。",
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
    parser = argparse.ArgumentParser(description="Validate v2 taxonomy with real tickets using configured OpenAI-compatible model.")
    parser.add_argument(
        "--output-markdown",
        default=str(REPO_ROOT / "docs" / "converger_design" / "taxonomy_v2_validation_report.md"),
        help="Markdown report output path.",
    )
    parser.add_argument(
        "--output-json",
        default=str(REPO_ROOT / "docs" / "converger_design" / "taxonomy_v2_validation_report.json"),
        help="JSON report output path.",
    )
    return parser


def compact_ticket(ticket: dict) -> dict:
    return {key: ticket.get(key) for key in TICKET_KEYS if ticket.get(key) not in (None, "", [])}


def build_leaf_catalog() -> list[dict]:
    rows: list[dict] = []
    for level1_code, level1_body in TAXONOMY.items():
        for level1_name, level2_map in level1_body.items():
            for level2_code, leaves in level2_map.items():
                for leaf_name in leaves:
                    rows.append(
                        {
                            "level1_code": level1_code,
                            "level1_name": level1_name,
                            "level2_code": level2_code,
                            "leaf_name": leaf_name,
                        }
                    )
    return rows


def build_prompt(ticket: dict) -> str:
    leaf_rows = build_leaf_catalog()
    lines = []
    for row in leaf_rows:
        lines.append(f"- [{row['level1_code']}] / [{row['level2_code']}] / {row['leaf_name']}")
    ticket_payload = json.dumps(compact_ticket(ticket), ensure_ascii=False, indent=2)
    return f"""请根据下面工单内容，从给定的 V2 分类体系中只选择 1 个最合适的叶子分类。

要求：
1. 只能从下面给定的叶子分类中选择。
2. 不要参考旧分类编码。
3. 只判断工单的核心问题，不要把诉求标签当成主分类。
4. 如果工单表现为履约、上门、交付不及时，不要误判成销户或套餐变更。
5. 如果工单表现为宣传承诺与实际不符，优先考虑营销解释/误导或承诺未兑现。
6. 输出必须是纯 JSON。

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
            {
                "role": "system",
                "content": "你是运营商投诉分类专家。你只能在给定的 V2 分类叶子里选一个最合适的主分类。",
            },
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
        "# V2 分类样本验证报告",
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
                f"- AI 摘要：{actual.get('summary', '')}",
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
