from __future__ import annotations

import re
from typing import Any, Callable, Mapping


PlaybookPredicate = Callable[[str, Mapping[str, Any]], bool]


def build_experience_playbooks(
    ticket: Mapping[str, Any],
    classification: Mapping[str, Any],
) -> list[dict[str, str]]:
    """Build deterministic actions from shared complaint-handling experience."""
    text = _combined_text(ticket, classification)
    actions: list[dict[str, str]] = []

    for predicate, action in _PLAYBOOKS:
        if predicate(text, classification):
            _add(actions, action)

    return actions


def build_general_experience_fallback() -> dict[str, str]:
    return {
        "title": "按证据-规则-方案闭环处理",
        "content": (
            "1. 核实事实：先调取账单、清单、受理记录、系统状态、历史工单和回访记录，确认用户投诉点是否属实。\n"
            "2. 判断规则：把核实结果与资费规则、业务协议、网络/平台能力或合规要求逐项对应，明确企业有责、无责或证据不足。\n"
            "3. 执行动作：能直接修复、退费、取消、变更或补办的，明确责任部门和完成时限；规则不支持的，给出替代方案或升级复核路径。\n"
            "4. 回访确认：向用户解释证据和处理结果，记录是否认可；未达成一致时补充依据并人工复核。"
        ),
        "applicability_note": "适用于处理建议库未命中时的通用闭环，需结合具体工单证据人工落地。",
        "match_level": "experience_fallback",
    }


def _combined_text(ticket: Mapping[str, Any], classification: Mapping[str, Any]) -> str:
    values: list[str] = []
    for source in (ticket, classification):
        for value in source.values():
            if value is not None:
                values.append(str(value))
    return "\n".join(values)


def _add(actions: list[dict[str, str]], action: dict[str, str]) -> None:
    if any(item["title"] == action["title"] for item in actions):
        return
    actions.append({**action, "match_level": "experience_playbook"})


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    lower_text = text.lower()
    return any(term.lower() in lower_text for term in terms)


def _matches(text: str, pattern: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def _leaf_is(classification: Mapping[str, Any], *codes: str) -> bool:
    return str(classification.get("primary_leaf_code") or "") in codes


def _spam_intercept(text: str, classification: Mapping[str, Any]) -> bool:
    return _has_any(
        text,
        (
            "垃圾短信",
            "违规短信",
            "违规内容",
            "商业广告",
            "敏感字",
            "敏感词",
            "41000",
            "短信拦截",
            "承诺书",
            "被举报",
            "网安",
            "解禁",
        ),
    )


def _broadband_quality(text: str, classification: Mapping[str, Any]) -> bool:
    return _leaf_is(classification, "BROADBAND_SLOW", "BROADBAND_UNSTABLE") or _matches(
        text, r"宽带.*(网速慢|不达标|时断时续|掉线|无法连接)|网速.*(慢|不达标)"
    )


def _abnormal_fee(text: str, classification: Mapping[str, Any]) -> bool:
    return _leaf_is(classification, "UNKNOWN_CHARGE", "OUT_OF_BUNDLE_FEE_DISPUTE") and _has_any(
        text,
        ("异常话费", "异常扣费", "不明收费", "话单", "清单", "乱扣费", "超短通话", "声讯", "漫游", "流量费用"),
    )


def _wifi_account(text: str, classification: Mapping[str, Any]) -> bool:
    return _has_any(text, ("wifi密码", "wifi上网", "wifi费用", "账号被盗", "密码被盗"))


def _terminal_repair(text: str, classification: Mapping[str, Any]) -> bool:
    return _has_any(text, ("终端维修", "手机终端", "保修", "厂家检测", "手机质量", "终端质量"))


def _repeat_or_unresolved(text: str, classification: Mapping[str, Any]) -> bool:
    return _leaf_is(classification, "UNRESOLVED_OR_REPEAT_COMPLAINT") or _has_any(
        text,
        ("重复投诉", "多次投诉", "前期反映", "再次来电", "一直未处理", "无人处理", "久拖未决"),
    )


def _appointment_or_delivery_delay(text: str, classification: Mapping[str, Any]) -> bool:
    return _leaf_is(classification, "DELIVERY_DELAY", "INSTALL_MOVE_URGING") or _has_any(
        text,
        (
            "预约拆机",
            "预约装机",
            "预约移机",
            "预约后未办理",
            "未上门",
            "无人上门",
            "上门务必",
            "处理不及时",
            "履约不及时",
            "超时履约",
            "未履约",
        ),
    )


def _agency_or_remote_cancel(text: str, classification: Mapping[str, Any]) -> bool:
    return _leaf_is(classification, "AGENCY_PROCESS_RULE_DISPUTE") or _has_any(
        text,
        ("代办", "异地销户", "异地拆机", "本人办理", "委托书", "委托办理"),
    )


def _second_number(text: str, classification: Mapping[str, Any]) -> bool:
    return _has_any(text, ("二次放号", "被注册", "已被注册", "标记骚扰", "号码被标识", "解绑"))


_PLAYBOOKS: tuple[tuple[PlaybookPredicate, dict[str, str]], ...] = (
    (
        _spam_intercept,
        {
            "title": "垃圾短信拦截/限制通信服务处理",
            "content": (
                "1. 核实事实：查询短信平台、垃圾短信中心或统一接触平台，确认是否因违规内容、商业广告、被举报或失败码41000触发短信发送限制。\n"
                "2. 判断规则：向用户说明涉短信息治理、隐私限制和处理权限边界；不能直接泄露具体短信内容时，应说明只能核实限制原因和处理路径。\n"
                "3. 执行动作：如需恢复，要求用户提交承诺书、机主有效证件及必要说明，转网安/后端部门复核；告知处理时限，并建议后续避免敏感词或群发商业内容。\n"
                "4. 回访确认：后端处理后回访用户测试短信发送功能，记录用户是否认可。"
            ),
            "applicability_note": "适用于短信因垃圾短信、违规内容、被举报或41000拦截导致无法发送的场景。",
        },
    ),
    (
        _broadband_quality,
        {
            "title": "宽带网速慢/不稳定闭环处理",
            "content": (
                "1. 核实事实：确认套餐速率、装机地址、测速方式、光猫/路由器状态、线路质量、历史报障和上门记录。\n"
                "2. 判断规则：区分局方网络/线路问题、用户终端或路由器问题、无线覆盖问题、测速环境不符合规范、承诺速率与实测速率不一致。\n"
                "3. 执行动作：能远程修复的先处理；需现场的预约装维上门并明确时限；确实长期不达标或无法满足使用需求的，给出降档、优化、拆机或费用协商方案。\n"
                "4. 回访确认：复测后回访用户确认速率和稳定性，重复投诉需指定责任人持续跟踪。"
            ),
            "applicability_note": "适用于宽带网速慢、测速不达标、掉线、时断时续或因体验差要求拆机的场景。",
        },
    ),
    (
        _abnormal_fee,
        {
            "title": "异常费用/清单争议核查处理",
            "content": (
                "1. 核实事实：调取账单、详单、业务订购记录、使用时间、使用地点、对端号码或业务代码，确认费用形成链路。\n"
                "2. 判断规则：区分用户真实使用、账号/密码被他人使用、终端或设备自动触发、系统计费异常、边界漫游或第三方业务扣费。\n"
                "3. 执行动作：有证据证明系统或业务侧异常的，按规则退费并修复；证据不足但首次争议且用户感知强烈的，可申请一次性协商处理并提示后续防范。\n"
                "4. 回访确认：用用户能理解的语言解释费用来源、处理金额和到账时间，提醒用户查询后续账单。"
            ),
            "applicability_note": "适用于异常话费、超短话单、声讯费、漫游费、流量费或其他不明扣费争议。",
        },
    ),
    (
        _wifi_account,
        {
            "title": "WiFi账号/密码疑似被盗用处理",
            "content": (
                "1. 核实事实：查询WiFi登录时间、登录地点、费用清单，并与用户通话地、常住地和使用习惯比对。\n"
                "2. 判断规则：登录地与用户活动地一致时，优先解释可能为本人或亲友使用；明显不一致时，按账号被盗用风险处理。\n"
                "3. 执行动作：指导用户立即修改复杂密码；首次争议且证据支持被盗用或用户意见较大时，按本地规则申请一次性费用协商处理。\n"
                "4. 回访确认：告知退费/减免到账时限，并说明再次因密码保管不善产生费用通常不再特殊处理。"
            ),
            "applicability_note": "适用于WiFi上网费用、WiFi密码被盗、账号被他人使用导致扣费的场景。",
        },
    ),
    (
        _terminal_repair,
        {
            "title": "终端质量/维修争议处理",
            "content": (
                "1. 核实事实：确认购买渠道、保修期、维修记录、检测结论、故障复现情况和用户使用方式。\n"
                "2. 判断规则：区分产品质量问题、人为损坏、超过保修范围、维修周期过长或售后沟通不到位。\n"
                "3. 执行动作：符合保修或质量问题的，协调厂家/售后维修、换机或补偿；不符合的，提供检测依据和可选付费维修方案。\n"
                "4. 回访确认：同步维修进度和预计完成时间，重复投诉需指定售后接口人跟进。"
            ),
            "applicability_note": "适用于手机、终端、智能设备质量或维修时效争议。",
        },
    ),
    (
        _repeat_or_unresolved,
        {
            "title": "重复投诉/久拖未决升级处理",
            "content": (
                "1. 核实事实：串联历史工单、回访记录、承诺事项、责任部门和未解决原因，避免重新按首单处理。\n"
                "2. 判断规则：识别是方案未执行、跨部门卡点、前次解释不充分、用户不认可规则，还是确实无法满足诉求。\n"
                "3. 执行动作：明确一个责任人、一个最终方案和一个完成时限；涉及多部门的同步拉通，不再让用户重复陈述。\n"
                "4. 回访确认：按承诺节点主动回访，未达成一致时补充企业无责依据并升级人工复核。"
            ),
            "applicability_note": "适用于重复投诉、前期处理未闭环、用户称无人处理或问题长期未解决的场景。",
        },
    ),
    (
        _appointment_or_delivery_delay,
        {
            "title": "预约装拆移机/履约不及时处理",
            "content": (
                "1. 核实事实：查询预约单、装拆移机工单、上门联系记录、承诺时间、当前竣工状态，以及是否关联套餐变更、设备安装或费用争议。\n"
                "2. 判断规则：区分用户原因改约、装维资源未履约、系统卡单、资料不全、拆机后套餐未同步变更等原因。\n"
                "3. 执行动作：明确责任装维或渠道部门，重新约定可执行上门时间；涉及拆机后套餐变更、费用不承担等诉求的，同步创建或催办套餐变更/费用核查流程。\n"
                "4. 回访确认：在约定节点前后主动回访，确认是否已上门、是否完成拆机/装机/套餐变更；未完成不得仅解释结单。"
            ),
            "applicability_note": "适用于预约装机、拆机、移机、上门处理不及时或履约未完成的场景。",
        },
    ),
    (
        _agency_or_remote_cancel,
        {
            "title": "代办/异地销户拆机规则争议处理",
            "content": (
                "1. 核实事实：确认用户身份、业务类型、是否欠费/合约/设备未归还，以及用户无法本人到场的原因。\n"
                "2. 判断规则：核对本地代办、线上办理、异地办理和委托材料规则，区分必须本人办理与可授权办理。\n"
                "3. 执行动作：可代办的，明确身份证件、委托书、设备归还和办理渠道；规则不支持的，说明原因并提供最近可行替代路径或升级复核。\n"
                "4. 回访确认：确认用户已收到材料清单和办理路径，避免因材料不全再次派单。"
            ),
            "applicability_note": "适用于代办拆机、异地销户、本人办理限制、委托办理流程争议。",
        },
    ),
    (
        _second_number,
        {
            "title": "二次放号相关账号/标记问题处理",
            "content": (
                "1. 核实事实：确认号码是否二次放号，问题发生在哪个平台或场景，如APP已注册、银行卡绑定、外部平台标记骚扰。\n"
                "2. 判断规则：区分电信侧可处理的信息、第三方平台留存信息和用户自行解绑范围。\n"
                "3. 执行动作：电信侧资料异常先修正；第三方平台问题协助用户提供号码归属/二次放号说明，引导平台解绑或申诉；必要时提供换号等替代方案。\n"
                "4. 回访确认：跟踪第三方处理结果，记录用户是否接受说明或替代方案。"
            ),
            "applicability_note": "适用于二次放号导致APP已注册、号码被标记、第三方账号无法解绑等场景。",
        },
    ),
)
