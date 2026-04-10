/* =========================================================
   四级分类初始化（高频精细场景）
   ========================================================= */

-- FEE_PACKAGE_MONTHLY
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_PACKAGE_MONTHLY_BASE', '套餐月费不认可', id, 4, '用户认为套餐基础月费不合理或与承诺不符', 10
from complaint_category where code = 'FEE_PACKAGE_MONTHLY'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_PACKAGE_MONTHLY_PROMISE', '套餐资费与承诺不符', id, 4, '实际资费与营销承诺不一致', 20
from complaint_category where code = 'FEE_PACKAGE_MONTHLY'
on conflict (code) do nothing;


-- FEE_PACKAGE_CHANGE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_PACKAGE_CHANGE_UPGRADE', '升档后资费不符', id, 4, '升级套餐后费用争议', 10
from complaint_category where code = 'FEE_PACKAGE_CHANGE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_PACKAGE_CHANGE_DOWNGRADE', '降档后资费不符', id, 4, '降档套餐后费用争议', 20
from complaint_category where code = 'FEE_PACKAGE_CHANGE'
on conflict (code) do nothing;


-- FEE_EXTRA_FLOW
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_EXTRA_FLOW_DOMESTIC', '国内流量超套收费争议', id, 4, '国内通用流量超套收费争议', 10
from complaint_category where code = 'FEE_EXTRA_FLOW'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_EXTRA_FLOW_PROVINCIAL', '省内流量超套收费争议', id, 4, '省内流量使用范围/收费争议', 20
from complaint_category where code = 'FEE_EXTRA_FLOW'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_EXTRA_FLOW_DIRECTIONAL', '定向流量超套收费争议', id, 4, '定向流量识别与收费争议', 30
from complaint_category where code = 'FEE_EXTRA_FLOW'
on conflict (code) do nothing;


-- FEE_EXTRA_CALL
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_EXTRA_CALL_DOMESTIC', '国内通话超套收费争议', id, 4, '国内语音超套费用争议', 10
from complaint_category where code = 'FEE_EXTRA_CALL'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_EXTRA_CALL_SPECIAL', '特殊号码通话收费争议', id, 4, '特殊号段、特殊通话收费争议', 20
from complaint_category where code = 'FEE_EXTRA_CALL'
on conflict (code) do nothing;


-- FEE_EXTRA_ROAMING
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_EXTRA_ROAMING_DOMESTIC', '国内漫游收费争议', id, 4, '国内跨区域通信费用争议', 10
from complaint_category where code = 'FEE_EXTRA_ROAMING'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_EXTRA_ROAMING_INTL', '国际港澳台漫游收费争议', id, 4, '国际及港澳台漫游资费争议', 20
from complaint_category where code = 'FEE_EXTRA_ROAMING'
on conflict (code) do nothing;


-- FEE_VALUE_DENY_ORDER
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_VALUE_DENY_ORDER_SMS', '短信订购争议', id, 4, '用户否认通过短信订购业务', 10
from complaint_category where code = 'FEE_VALUE_DENY_ORDER'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_VALUE_DENY_ORDER_CHANNEL', '渠道代订购争议', id, 4, '用户否认由营业厅/代理点代订购', 20
from complaint_category where code = 'FEE_VALUE_DENY_ORDER'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_VALUE_DENY_ORDER_TOUCH', '误触订购争议', id, 4, '用户认为因误触页面导致订购', 30
from complaint_category where code = 'FEE_VALUE_DENY_ORDER'
on conflict (code) do nothing;


-- FEE_WINGPAY_RIGHTS
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_WINGPAY_RIGHTS_UNCLEAR', '权益金收费未充分说明', id, 4, '权益金收费规则解释不清', 10
from complaint_category where code = 'FEE_WINGPAY_RIGHTS'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_WINGPAY_RIGHTS_CONTINUE', '权益包退订后仍收费', id, 4, '权益包退订后持续计费争议', 20
from complaint_category where code = 'FEE_WINGPAY_RIGHTS'
on conflict (code) do nothing;


-- FEE_PENALTY_BREACH
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_PENALTY_BREACH_PACKAGE', '合约套餐违约金争议', id, 4, '套餐合约期内解约违约金争议', 10
from complaint_category where code = 'FEE_PENALTY_BREACH'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_PENALTY_BREACH_BROADBAND', '宽带协议违约金争议', id, 4, '宽带协议期违约金争议', 20
from complaint_category where code = 'FEE_PENALTY_BREACH'
on conflict (code) do nothing;


-- FEE_REFUND_REBATE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_REFUND_REBATE_ACTIVITY', '活动返费未到账', id, 4, '活动返费未按规则发放', 10
from complaint_category where code = 'FEE_REFUND_REBATE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_REFUND_REBATE_GIFT', '赠费未到账', id, 4, '承诺赠费未到账', 20
from complaint_category where code = 'FEE_REFUND_REBATE'
on conflict (code) do nothing;


-- FEE_UNKNOWN_UNUSED
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_UNKNOWN_UNUSED_DATA', '未使用流量却计费', id, 4, '用户称未使用流量却产生流量费', 10
from complaint_category where code = 'FEE_UNKNOWN_UNUSED'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_UNKNOWN_UNUSED_VAS', '未使用增值服务却计费', id, 4, '用户称未使用增值业务却收费', 20
from complaint_category where code = 'FEE_UNKNOWN_UNUSED'
on conflict (code) do nothing;


-- SUBSCRIBE_ORDER_NO_CONSENT
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_ORDER_NO_CONSENT_HALL', '营业厅未明确同意订购', id, 4, '营业厅办理时未明确确认订购', 10
from complaint_category where code = 'SUBSCRIBE_ORDER_NO_CONSENT'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_ORDER_NO_CONSENT_CALL', '电话营销未明确同意订购', id, 4, '外呼营销中未明确确认订购', 20
from complaint_category where code = 'SUBSCRIBE_ORDER_NO_CONSENT'
on conflict (code) do nothing;


-- SUBSCRIBE_CANCEL_FAIL
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_CANCEL_FAIL_USER', '用户端无法退订', id, 4, 'APP、网厅、小程序无法操作退订', 10
from complaint_category where code = 'SUBSCRIBE_CANCEL_FAIL'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_CANCEL_FAIL_CHANNEL', '渠道不受理退订', id, 4, '营业厅或渠道不予受理退订', 20
from complaint_category where code = 'SUBSCRIBE_CANCEL_FAIL'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_CANCEL_FAIL_SYSTEM', '系统报错导致退订失败', id, 4, '系统异常导致退订无法完成', 30
from complaint_category where code = 'SUBSCRIBE_CANCEL_FAIL'
on conflict (code) do nothing;


-- SUBSCRIBE_CANCEL_CONTINUE_FEE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_CANCEL_CONTINUE_FEE_NEXT', '次月继续收费', id, 4, '退订后次月仍继续收费', 10
from complaint_category where code = 'SUBSCRIBE_CANCEL_CONTINUE_FEE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_CANCEL_CONTINUE_FEE_NOT_EFFECT', '退订未生效仍收费', id, 4, '退订提交成功但未生效', 20
from complaint_category where code = 'SUBSCRIBE_CANCEL_CONTINUE_FEE'
on conflict (code) do nothing;


-- SUBSCRIBE_RENEW_FREE_TO_PAID
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_RENEW_FREE_TO_PAID_TRIAL', '试用到期转收费争议', id, 4, '试用服务到期后自动转收费', 10
from complaint_category where code = 'SUBSCRIBE_RENEW_FREE_TO_PAID'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_RENEW_FREE_TO_PAID_PROMO', '优惠到期转原价争议', id, 4, '优惠价到期转原价引发争议', 20
from complaint_category where code = 'SUBSCRIBE_RENEW_FREE_TO_PAID'
on conflict (code) do nothing;


-- OPEN_CLOSE_SHUTDOWN_RISK
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_SHUTDOWN_RISK_FRAUD', '反诈治理关停争议', id, 4, '因反诈治理措施导致关停', 10
from complaint_category where code = 'OPEN_CLOSE_SHUTDOWN_RISK'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_SHUTDOWN_RISK_SAFE', '安全风控关停争议', id, 4, '因安全风控导致限制通信', 20
from complaint_category where code = 'OPEN_CLOSE_SHUTDOWN_RISK'
on conflict (code) do nothing;


-- OPEN_CLOSE_CANCEL_DISMANTLE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_CANCEL_DISMANTLE_BROADBAND', '宽带拆机不及时', id, 4, '宽带拆机预约后长期未完成', 10
from complaint_category where code = 'OPEN_CLOSE_CANCEL_DISMANTLE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_CANCEL_DISMANTLE_IPTV', 'IPTV拆机不及时', id, 4, '电视业务拆机长期未完成', 20
from complaint_category where code = 'OPEN_CLOSE_CANCEL_DISMANTLE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_CANCEL_DISMANTLE_FUSION', '融合业务拆机不及时', id, 4, '融合业务整体拆机处理慢', 30
from complaint_category where code = 'OPEN_CLOSE_CANCEL_DISMANTLE'
on conflict (code) do nothing;


-- OPEN_CLOSE_CANCEL_RULE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_CANCEL_RULE_RETURN', '设备归还规则争议', id, 4, '销户要求归还设备引发争议', 10
from complaint_category where code = 'OPEN_CLOSE_CANCEL_RULE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_CANCEL_RULE_LOCAL', '必须本地销户规则争议', id, 4, '要求到归属地销户引发争议', 20
from complaint_category where code = 'OPEN_CLOSE_CANCEL_RULE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_CANCEL_RULE_CLEAR', '销户前必须结清规则争议', id, 4, '要求结清欠费、违约金等后才能销户', 30
from complaint_category where code = 'OPEN_CLOSE_CANCEL_RULE'
on conflict (code) do nothing;


-- OPEN_CLOSE_CANCEL_CONTINUE_FEE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_CANCEL_CONTINUE_FEE_STATE', '销户状态未同步仍计费', id, 4, '销户完成但状态未同步导致计费', 10
from complaint_category where code = 'OPEN_CLOSE_CANCEL_CONTINUE_FEE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_CANCEL_CONTINUE_FEE_PROCESS', '销户流程中断仍计费', id, 4, '销户中途失败导致持续收费', 20
from complaint_category where code = 'OPEN_CLOSE_CANCEL_CONTINUE_FEE'
on conflict (code) do nothing;


-- OPEN_CLOSE_ACTIVATION_CARD
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_ACTIVATION_CARD_NEW', '新卡激活失败', id, 4, '新开号卡首次激活失败', 10
from complaint_category where code = 'OPEN_CLOSE_ACTIVATION_CARD'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_ACTIVATION_CARD_REISSUE', '补卡激活异常', id, 4, '补卡后激活异常', 20
from complaint_category where code = 'OPEN_CLOSE_ACTIVATION_CARD'
on conflict (code) do nothing;


-- MARKETING_EXPLAIN_UNCLEAR
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_EXPLAIN_UNCLEAR_FEE', '资费解释不清', id, 4, '套餐、收费项目说明不清', 10
from complaint_category where code = 'MARKETING_EXPLAIN_UNCLEAR'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_EXPLAIN_UNCLEAR_ACTIVITY', '活动规则解释不清', id, 4, '活动参与条件、返费方式解释不清', 20
from complaint_category where code = 'MARKETING_EXPLAIN_UNCLEAR'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_EXPLAIN_UNCLEAR_RIGHTS', '权益内容解释不清', id, 4, '会员、礼包、权益内容说明不清', 30
from complaint_category where code = 'MARKETING_EXPLAIN_UNCLEAR'
on conflict (code) do nothing;


-- MARKETING_EXPLAIN_MISLEADING
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_EXPLAIN_MISLEADING_PROMISE', '承诺与实际不符', id, 4, '销售承诺与最终实际不一致', 10
from complaint_category where code = 'MARKETING_EXPLAIN_MISLEADING'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_EXPLAIN_MISLEADING_HIDDEN', '隐瞒限制条件', id, 4, '未告知关键前提、资格、期限、收费条件', 20
from complaint_category where code = 'MARKETING_EXPLAIN_MISLEADING'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_EXPLAIN_MISLEADING_EXAGGERATE', '夸大宣传', id, 4, '宣传内容存在明显夸大', 30
from complaint_category where code = 'MARKETING_EXPLAIN_MISLEADING'
on conflict (code) do nothing;


-- MARKETING_PROCESS_ERROR
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_PROCESS_ERROR_PRODUCT', '办错产品', id, 4, '办理了错误产品类型', 10
from complaint_category where code = 'MARKETING_PROCESS_ERROR'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_PROCESS_ERROR_PACKAGE', '办错套餐', id, 4, '办理了错误套餐档位', 20
from complaint_category where code = 'MARKETING_PROCESS_ERROR'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_PROCESS_ERROR_INFO', '录入信息错误', id, 4, '号码、身份、地址等录入错误', 30
from complaint_category where code = 'MARKETING_PROCESS_ERROR'
on conflict (code) do nothing;


-- MARKETING_PROMISE_REBATE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_PROMISE_REBATE_MONTHLY', '月返费未兑现', id, 4, '承诺月返费未兑现', 10
from complaint_category where code = 'MARKETING_PROMISE_REBATE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_PROMISE_REBATE_ONCE', '一次性返费未兑现', id, 4, '承诺一次性返费未到账', 20
from complaint_category where code = 'MARKETING_PROMISE_REBATE'
on conflict (code) do nothing;


-- RULE_ACTIVITY_PARTICIPATION
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_ACTIVITY_PARTICIPATION_OLD', '老用户不能参与争议', id, 4, '老用户不可参加活动引发争议', 10
from complaint_category where code = 'RULE_ACTIVITY_PARTICIPATION'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_ACTIVITY_PARTICIPATION_CHANNEL', '指定渠道参与争议', id, 4, '仅指定渠道参与活动引发争议', 20
from complaint_category where code = 'RULE_ACTIVITY_PARTICIPATION'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_ACTIVITY_PARTICIPATION_PACKAGE', '指定套餐参与争议', id, 4, '仅指定套餐可参与活动引发争议', 30
from complaint_category where code = 'RULE_ACTIVITY_PARTICIPATION'
on conflict (code) do nothing;


-- RULE_EFFECTIVE_PACKAGE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_EFFECTIVE_PACKAGE_IMMEDIATE', '未即时生效争议', id, 4, '用户认为套餐应立即生效', 10
from complaint_category where code = 'RULE_EFFECTIVE_PACKAGE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_EFFECTIVE_PACKAGE_NEXT', '次月生效争议', id, 4, '套餐按次月生效引发争议', 20
from complaint_category where code = 'RULE_EFFECTIVE_PACKAGE'
on conflict (code) do nothing;


-- RULE_PROCESS_PROXY
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_PROCESS_PROXY_FAMILY', '家属代办规则争议', id, 4, '家属能否代办引发争议', 10
from complaint_category where code = 'RULE_PROCESS_PROXY'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_PROCESS_PROXY_ENTERPRISE', '企业经办人代办争议', id, 4, '企业客户代办权限争议', 20
from complaint_category where code = 'RULE_PROCESS_PROXY'
on conflict (code) do nothing;


-- PRODUCT_PLATFORM_APP_ERROR
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_APP_ERROR_APP', 'APP页面报错', id, 4, '中国电信APP页面异常', 10
from complaint_category where code = 'PRODUCT_PLATFORM_APP_ERROR'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_APP_ERROR_WEB', '网厅页面报错', id, 4, '网上营业厅页面异常', 20
from complaint_category where code = 'PRODUCT_PLATFORM_APP_ERROR'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_APP_ERROR_MINI', '小程序页面报错', id, 4, '小程序页面异常', 30
from complaint_category where code = 'PRODUCT_PLATFORM_APP_ERROR'
on conflict (code) do nothing;


-- PRODUCT_PLATFORM_QUERY_ORDER
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_QUERY_ORDER_PROGRESS', '进度显示错误', id, 4, '订单进度展示不正确', 10
from complaint_category where code = 'PRODUCT_PLATFORM_QUERY_ORDER'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_QUERY_ORDER_RESULT', '结果显示错误', id, 4, '订单结果与实际不符', 20
from complaint_category where code = 'PRODUCT_PLATFORM_QUERY_ORDER'
on conflict (code) do nothing;


-- INSTALL_TIMELINESS_NOT_VISIT
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_TIMELINESS_NOT_VISIT_FIRST', '首次安装未上门', id, 4, '首次安装预约未上门', 10
from complaint_category where code = 'INSTALL_TIMELINESS_NOT_VISIT'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_TIMELINESS_NOT_VISIT_MOVE', '移机未上门', id, 4, '移机预约未上门', 20
from complaint_category where code = 'INSTALL_TIMELINESS_NOT_VISIT'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_TIMELINESS_NOT_VISIT_REMOVE', '拆机未上门', id, 4, '拆机预约未上门', 30
from complaint_category where code = 'INSTALL_TIMELINESS_NOT_VISIT'
on conflict (code) do nothing;


-- INSTALL_TIMELINESS_OVERTIME
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_TIMELINESS_OVERTIME_INSTALL', '安装超时未完成', id, 4, '安装工单超时未完成', 10
from complaint_category where code = 'INSTALL_TIMELINESS_OVERTIME'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_TIMELINESS_OVERTIME_REMOVE', '拆机超时未完成', id, 4, '拆机工单超时未完成', 20
from complaint_category where code = 'INSTALL_TIMELINESS_OVERTIME'
on conflict (code) do nothing;


-- INSTALL_RESULT_SPEED
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_RESULT_SPEED_BANDWIDTH', '带宽实测速率不达标', id, 4, '宽带实测速率不达承诺标准', 10
from complaint_category where code = 'INSTALL_RESULT_SPEED'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_RESULT_SPEED_WIFI', 'WiFi体验速率不达预期', id, 4, '用户体验速率低于预期', 20
from complaint_category where code = 'INSTALL_RESULT_SPEED'
on conflict (code) do nothing;


-- NETWORK_SIGNAL_AREA
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_SIGNAL_AREA_HOME', '家庭室内信号差', id, 4, '家庭住宅室内信号差', 10
from complaint_category where code = 'NETWORK_SIGNAL_AREA'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_SIGNAL_AREA_COMMUNITY', '小区区域信号差', id, 4, '小区公共区域或整体覆盖差', 20
from complaint_category where code = 'NETWORK_SIGNAL_AREA'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_SIGNAL_AREA_BUILDING', '楼宇办公区信号差', id, 4, '楼宇、写字楼等区域覆盖差', 30
from complaint_category where code = 'NETWORK_SIGNAL_AREA'
on conflict (code) do nothing;


-- NETWORK_SPEED_MOBILE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_SPEED_MOBILE_INDOOR', '室内上网慢', id, 4, '室内移动数据速度慢', 10
from complaint_category where code = 'NETWORK_SPEED_MOBILE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_SPEED_MOBILE_PERIOD', '特定时段上网慢', id, 4, '高峰期或特定时段上网慢', 20
from complaint_category where code = 'NETWORK_SPEED_MOBILE'
on conflict (code) do nothing;


-- NETWORK_CALL_DROP
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_CALL_DROP_VOLTE', 'VoLTE掉话', id, 4, 'VoLTE通话中掉话', 10
from complaint_category where code = 'NETWORK_CALL_DROP'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_CALL_DROP_FALLBACK', '回落导致掉话', id, 4, '网络制式回落导致掉话', 20
from complaint_category where code = 'NETWORK_CALL_DROP'
on conflict (code) do nothing;


-- NETWORK_CALL_CONNECT
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_CALL_CONNECT_OUT', '拨出困难', id, 4, '呼出困难、长时间无响应', 10
from complaint_category where code = 'NETWORK_CALL_CONNECT'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_CALL_CONNECT_IN', '呼入困难', id, 4, '别人打不进来、无法接入', 20
from complaint_category where code = 'NETWORK_CALL_CONNECT'
on conflict (code) do nothing;


-- BILLING_BILL_AMOUNT
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_BILL_AMOUNT_HIGH', '账单金额偏高争议', id, 4, '本期账单金额高于用户预期', 10
from complaint_category where code = 'BILLING_BILL_AMOUNT'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_BILL_AMOUNT_ABNORMAL', '账单突增争议', id, 4, '账单金额突然异常升高', 20
from complaint_category where code = 'BILLING_BILL_AMOUNT'
on conflict (code) do nothing;


-- BILLING_PAYMENT_NOT_ARRIVE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_PAYMENT_NOT_ARRIVE_ONLINE', '线上充值未到账', id, 4, '通过APP/网厅充值未到账', 10
from complaint_category where code = 'BILLING_PAYMENT_NOT_ARRIVE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_PAYMENT_NOT_ARRIVE_CHANNEL', '渠道缴费未到账', id, 4, '通过营业厅/代理点缴费未到账', 20
from complaint_category where code = 'BILLING_PAYMENT_NOT_ARRIVE'
on conflict (code) do nothing;


-- BILLING_INVOICE_ERROR
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_INVOICE_ERROR_TITLE', '发票抬头错误', id, 4, '开票抬头与要求不一致', 10
from complaint_category where code = 'BILLING_INVOICE_ERROR'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_INVOICE_ERROR_AMOUNT', '发票金额错误', id, 4, '发票金额与实际不一致', 20
from complaint_category where code = 'BILLING_INVOICE_ERROR'
on conflict (code) do nothing;


-- SERVICE_OTHER_PROCESS_REPEAT
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_PROCESS_REPEAT_SECOND', '二次投诉', id, 4, '同一事项再次投诉', 10
from complaint_category where code = 'SERVICE_OTHER_PROCESS_REPEAT'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_PROCESS_REPEAT_MULTI', '多次重复投诉', id, 4, '同一事项多次重复投诉', 20
from complaint_category where code = 'SERVICE_OTHER_PROCESS_REPEAT'
on conflict (code) do nothing;


-- SERVICE_OTHER_FLOW_TIMEOUT
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_FLOW_TIMEOUT_FIRST', '首次超时未处理', id, 4, '首次流转即超时', 10
from complaint_category where code = 'SERVICE_OTHER_FLOW_TIMEOUT'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_FLOW_TIMEOUT_MULTI', '多轮流转超时', id, 4, '多轮流转后仍超时', 20
from complaint_category where code = 'SERVICE_OTHER_FLOW_TIMEOUT'
on conflict (code) do nothing;