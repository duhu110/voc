/* =========================================================
   三级分类初始化
   ========================================================= */

-- FEE_PACKAGE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_PACKAGE_MONTHLY', '套餐收费疑议', id, 3, '用户对套餐月费、资费标准不认可', 10
from complaint_category where code = 'FEE_PACKAGE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_PACKAGE_CHANGE', '套餐变更后资费争议', id, 3, '升降档、改套餐后费用与预期不一致', 20
from complaint_category where code = 'FEE_PACKAGE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_PACKAGE_FUSION', '融合套餐资费争议', id, 3, '融合套餐资费、拆分计费、组合收费争议', 30
from complaint_category where code = 'FEE_PACKAGE'
on conflict (code) do nothing;


-- FEE_EXTRA
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_EXTRA_FLOW', '流量超套收费争议', id, 3, '用户对流量超套收费不认可', 10
from complaint_category where code = 'FEE_EXTRA'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_EXTRA_CALL', '通话超套收费争议', id, 3, '用户对通话超套收费不认可', 20
from complaint_category where code = 'FEE_EXTRA'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_EXTRA_SMS', '短信超套收费争议', id, 3, '用户对短信超套收费不认可', 30
from complaint_category where code = 'FEE_EXTRA'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_EXTRA_ROAMING', '漫游费用争议', id, 3, '用户对国内/国际漫游费用不认可', 40
from complaint_category where code = 'FEE_EXTRA'
on conflict (code) do nothing;


-- FEE_VALUE_ADDED
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_VALUE_SUBSCRIBE', '增值业务收费争议', id, 3, '会员、视频、铃音、订阅类收费争议', 10
from complaint_category where code = 'FEE_VALUE_ADDED'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_VALUE_RENEW', '自动续订收费争议', id, 3, '增值业务自动续费争议', 20
from complaint_category where code = 'FEE_VALUE_ADDED'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_VALUE_DENY_ORDER', '用户否认订购收费争议', id, 3, '用户否认主动订购产生收费', 30
from complaint_category where code = 'FEE_VALUE_ADDED'
on conflict (code) do nothing;


-- FEE_WINGPAY
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_WINGPAY_RIGHTS', '翼支付权益金争议', id, 3, '翼支付权益金、权益包收费争议', 10
from complaint_category where code = 'FEE_WINGPAY'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_WINGPAY_PAYMENT', '支付扣款争议', id, 3, '翼支付或支付账户异常扣款争议', 20
from complaint_category where code = 'FEE_WINGPAY'
on conflict (code) do nothing;


-- FEE_PENALTY
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_PENALTY_BREACH', '违约金争议', id, 3, '协议期解约、合约终止违约金争议', 10
from complaint_category where code = 'FEE_PENALTY'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_PENALTY_LATE', '滞纳金争议', id, 3, '欠费滞纳金相关争议', 20
from complaint_category where code = 'FEE_PENALTY'
on conflict (code) do nothing;


-- FEE_BROADBAND_TV
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_BROADBAND_TV_BROADBAND', '宽带收费争议', id, 3, '宽带月费、安装费、移机费等争议', 10
from complaint_category where code = 'FEE_BROADBAND_TV'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_BROADBAND_TV_IPTV', 'IPTV收费争议', id, 3, '电视业务费用争议', 20
from complaint_category where code = 'FEE_BROADBAND_TV'
on conflict (code) do nothing;


-- FEE_REFUND
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_REFUND_REBATE', '返费赠费未到账', id, 3, '返费、赠费、权益到账异常', 10
from complaint_category where code = 'FEE_REFUND'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_REFUND_MONEY', '退款未到账', id, 3, '退款已承诺但未到账', 20
from complaint_category where code = 'FEE_REFUND'
on conflict (code) do nothing;


-- FEE_UNKNOWN
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_UNKNOWN_CHARGE', '不明扣费', id, 3, '账单中出现无法识别收费项目', 10
from complaint_category where code = 'FEE_UNKNOWN'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_UNKNOWN_UNUSED', '未使用收费争议', id, 3, '用户称未使用服务却被收费', 20
from complaint_category where code = 'FEE_UNKNOWN'
on conflict (code) do nothing;


-- SUBSCRIBE_ORDER
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_ORDER_FORCED', '强制搭售争议', id, 3, '用户认为被强制搭售业务', 10
from complaint_category where code = 'SUBSCRIBE_ORDER'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_ORDER_MISTAKE', '误办理争议', id, 3, '办理了错误产品或错误套餐', 20
from complaint_category where code = 'SUBSCRIBE_ORDER'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_ORDER_NO_CONSENT', '未明确同意订购', id, 3, '用户未明确授权订购业务', 30
from complaint_category where code = 'SUBSCRIBE_ORDER'
on conflict (code) do nothing;


-- SUBSCRIBE_CANCEL
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_CANCEL_FAIL', '退订失败', id, 3, '用户申请退订但未成功', 10
from complaint_category where code = 'SUBSCRIBE_CANCEL'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_CANCEL_DELAY', '退订不及时', id, 3, '退订流程过慢或超过承诺时限', 20
from complaint_category where code = 'SUBSCRIBE_CANCEL'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_CANCEL_CONTINUE_FEE', '退订后仍收费', id, 3, '退订完成后仍继续收费', 30
from complaint_category where code = 'SUBSCRIBE_CANCEL'
on conflict (code) do nothing;


-- SUBSCRIBE_RENEW
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_RENEW_AUTO', '自动续订争议', id, 3, '自动续费、续订未感知', 10
from complaint_category where code = 'SUBSCRIBE_RENEW'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_RENEW_FREE_TO_PAID', '免费到期转收费争议', id, 3, '试用到期转收费争议', 20
from complaint_category where code = 'SUBSCRIBE_RENEW'
on conflict (code) do nothing;


-- SUBSCRIBE_DENY
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_DENY_VALUE_ADDED', '否认增值业务订购', id, 3, '否认订购会员、订阅、铃音等', 10
from complaint_category where code = 'SUBSCRIBE_DENY'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_DENY_CHANNEL', '否认渠道代办订购', id, 3, '否认营业厅、代理点、外呼代为订购', 20
from complaint_category where code = 'SUBSCRIBE_DENY'
on conflict (code) do nothing;


-- OPEN_CLOSE_OPENING
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_OPENING_SERVICE', '业务开通失败', id, 3, '产品或业务开通失败', 10
from complaint_category where code = 'OPEN_CLOSE_OPENING'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_OPENING_BROADBAND', '宽带开通失败', id, 3, '宽带预约或安装后未开通成功', 20
from complaint_category where code = 'OPEN_CLOSE_OPENING'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_OPENING_CARD', '号卡开通失败', id, 3, '新卡、补卡、激活卡开通失败', 30
from complaint_category where code = 'OPEN_CLOSE_OPENING'
on conflict (code) do nothing;


-- OPEN_CLOSE_SHUTDOWN
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_SHUTDOWN_ARREARS', '欠费停机不认可', id, 3, '用户对欠费停机处理不认可', 10
from complaint_category where code = 'OPEN_CLOSE_SHUTDOWN'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_SHUTDOWN_RISK', '风险关停不认可', id, 3, '用户对反诈、风控等关停处理不认可', 20
from complaint_category where code = 'OPEN_CLOSE_SHUTDOWN'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_SHUTDOWN_MODEL', '模型关停不认可', id, 3, '用户对系统模型识别后的关停不认可', 30
from complaint_category where code = 'OPEN_CLOSE_SHUTDOWN'
on conflict (code) do nothing;


-- OPEN_CLOSE_RECOVERY
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_RECOVERY_DELAY', '复机不及时', id, 3, '复机申请后恢复过慢', 10
from complaint_category where code = 'OPEN_CLOSE_RECOVERY'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_RECOVERY_FAIL', '复机失败', id, 3, '复机流程失败或无法恢复', 20
from complaint_category where code = 'OPEN_CLOSE_RECOVERY'
on conflict (code) do nothing;


-- OPEN_CLOSE_CANCEL
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_CANCEL_DISMANTLE', '拆机销户', id, 3, '宽带、融合、IPTV等拆机销户问题', 10
from complaint_category where code = 'OPEN_CLOSE_CANCEL'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_CANCEL_RULE', '销户规则争议', id, 3, '销户条件、前置要求、归还设备等规则争议', 20
from complaint_category where code = 'OPEN_CLOSE_CANCEL'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_CANCEL_CONTINUE_FEE', '销户后仍计费', id, 3, '已销户仍持续计费', 30
from complaint_category where code = 'OPEN_CLOSE_CANCEL'
on conflict (code) do nothing;


-- OPEN_CLOSE_ACTIVATION
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_ACTIVATION_CARD', '号卡激活异常', id, 3, '新卡首激活失败', 10
from complaint_category where code = 'OPEN_CLOSE_ACTIVATION'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_ACTIVATION_REALNAME', '实名认证异常', id, 3, '实名校验失败、信息不一致', 20
from complaint_category where code = 'OPEN_CLOSE_ACTIVATION'
on conflict (code) do nothing;


-- MARKETING_EXPLAIN
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_EXPLAIN_UNCLEAR', '解释宣传不清', id, 3, '资费、活动、权益、规则等解释不清', 10
from complaint_category where code = 'MARKETING_EXPLAIN'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_EXPLAIN_MISLEADING', '营销误导', id, 3, '承诺与实际不符、夸大宣传、隐瞒条件', 20
from complaint_category where code = 'MARKETING_EXPLAIN'
on conflict (code) do nothing;


-- MARKETING_PROCESS
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_PROCESS_ERROR', '业务办理差错', id, 3, '办错业务、办错套餐、办错号码信息', 10
from complaint_category where code = 'MARKETING_PROCESS'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_PROCESS_MISS', '漏受理', id, 3, '应受理未受理、遗漏处理', 20
from complaint_category where code = 'MARKETING_PROCESS'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_PROCESS_STATUS', '受理状态异常', id, 3, '订单状态不同步、显示异常、处理中断', 30
from complaint_category where code = 'MARKETING_PROCESS'
on conflict (code) do nothing;


-- MARKETING_ATTITUDE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_ATTITUDE_HALL', '营业厅服务态度问题', id, 3, '营业厅人员服务态度投诉', 10
from complaint_category where code = 'MARKETING_ATTITUDE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_ATTITUDE_CALL', '客服服务态度问题', id, 3, '热线客服服务态度投诉', 20
from complaint_category where code = 'MARKETING_ATTITUDE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_ATTITUDE_MANAGER', '客户经理服务问题', id, 3, '客户经理/销售经理服务态度或跟进问题', 30
from complaint_category where code = 'MARKETING_ATTITUDE'
on conflict (code) do nothing;


-- MARKETING_PROMISE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_PROMISE_REBATE', '赠费返费未兑现', id, 3, '承诺赠费返费未兑现', 10
from complaint_category where code = 'MARKETING_PROMISE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_PROMISE_GIFT', '赠品权益未兑现', id, 3, '赠品、权益、礼包未兑现', 20
from complaint_category where code = 'MARKETING_PROMISE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_PROMISE_SPEED', '速率能力未兑现', id, 3, '承诺带宽、网络能力、千兆能力未兑现', 30
from complaint_category where code = 'MARKETING_PROMISE'
on conflict (code) do nothing;


-- RULE_ACTIVITY
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_ACTIVITY_PARTICIPATION', '活动参与条件争议', id, 3, '活动参加条件不认可', 10
from complaint_category where code = 'RULE_ACTIVITY'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_ACTIVITY_REBATE', '返费奖励规则争议', id, 3, '返费到账条件、奖励发放规则争议', 20
from complaint_category where code = 'RULE_ACTIVITY'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_ACTIVITY_CHANNEL', '渠道限制规则争议', id, 3, '活动仅限特定渠道引发争议', 30
from complaint_category where code = 'RULE_ACTIVITY'
on conflict (code) do nothing;


-- RULE_EFFECTIVE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_EFFECTIVE_PACKAGE', '套餐生效时间争议', id, 3, '套餐生效时间与用户预期不一致', 10
from complaint_category where code = 'RULE_EFFECTIVE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_EFFECTIVE_CANCEL', '退订失效时间争议', id, 3, '退订后失效时间与预期不一致', 20
from complaint_category where code = 'RULE_EFFECTIVE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_EFFECTIVE_CHANGE', '套餐变更生效规则争议', id, 3, '套餐切换、生效折算等规则争议', 30
from complaint_category where code = 'RULE_EFFECTIVE'
on conflict (code) do nothing;


-- RULE_PROCESS
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_PROCESS_PROXY', '代办规则争议', id, 3, '委托代办、家属代办、企业代办规则争议', 10
from complaint_category where code = 'RULE_PROCESS'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_PROCESS_REMOTE', '异地办理规则争议', id, 3, '异地受理、跨地区办理限制争议', 20
from complaint_category where code = 'RULE_PROCESS'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_PROCESS_CANCEL', '销户前置条件争议', id, 3, '销户前要求归还设备、结清费用等争议', 30
from complaint_category where code = 'RULE_PROCESS'
on conflict (code) do nothing;


-- RULE_USAGE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_USAGE_FLOW_SCOPE', '流量使用范围争议', id, 3, '省内、国内、定向流量使用范围争议', 10
from complaint_category where code = 'RULE_USAGE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_USAGE_SPEED_LIMIT', '限速封顶规则争议', id, 3, '达量限速、封顶后处理规则争议', 20
from complaint_category where code = 'RULE_USAGE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_USAGE_RIGHTS_SCOPE', '权益适用范围争议', id, 3, '会员、权益、礼包适用范围争议', 30
from complaint_category where code = 'RULE_USAGE'
on conflict (code) do nothing;


-- RULE_QUALIFICATION
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_QUALIFICATION_NEW_OLD', '新老用户资格争议', id, 3, '新用户、老用户资格限制争议', 10
from complaint_category where code = 'RULE_QUALIFICATION'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_QUALIFICATION_PACKAGE', '套餐资格条件争议', id, 3, '指定套餐才能参与引发争议', 20
from complaint_category where code = 'RULE_QUALIFICATION'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_QUALIFICATION_CHANNEL', '渠道资格条件争议', id, 3, '指定渠道、指定身份才能办理引发争议', 30
from complaint_category where code = 'RULE_QUALIFICATION'
on conflict (code) do nothing;


-- PRODUCT_PLATFORM_BASIC
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_BASIC_VOICE', '语音功能异常', id, 3, '打电话异常、无法通话等', 10
from complaint_category where code = 'PRODUCT_PLATFORM_BASIC'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_BASIC_SMS', '短信功能异常', id, 3, '短信收发异常', 20
from complaint_category where code = 'PRODUCT_PLATFORM_BASIC'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_BASIC_FLOW', '流量功能异常', id, 3, '流量无法使用、断流等', 30
from complaint_category where code = 'PRODUCT_PLATFORM_BASIC'
on conflict (code) do nothing;


-- PRODUCT_PLATFORM_APP
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_APP_ERROR', 'APP网厅报错', id, 3, '页面报错、闪退、无法打开', 10
from complaint_category where code = 'PRODUCT_PLATFORM_APP'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_APP_HANDLE', '线上办理失败', id, 3, 'APP、网厅、小程序无法完成办理', 20
from complaint_category where code = 'PRODUCT_PLATFORM_APP'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_APP_SUBMIT', '提交支付异常', id, 3, '订单提交失败、支付失败、重复提交', 30
from complaint_category where code = 'PRODUCT_PLATFORM_APP'
on conflict (code) do nothing;


-- PRODUCT_PLATFORM_ACCOUNT
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_ACCOUNT_LOGIN', '账号登录失败', id, 3, '无法登录、密码错误、验证码失败', 10
from complaint_category where code = 'PRODUCT_PLATFORM_ACCOUNT'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_ACCOUNT_VERIFY', '身份校验异常', id, 3, '实名校验、身份识别失败', 20
from complaint_category where code = 'PRODUCT_PLATFORM_ACCOUNT'
on conflict (code) do nothing;


-- PRODUCT_PLATFORM_QUERY
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_QUERY_PACKAGE', '套餐信息展示异常', id, 3, '套餐内容展示不正确', 10
from complaint_category where code = 'PRODUCT_PLATFORM_QUERY'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_QUERY_BALANCE', '余额账单展示异常', id, 3, '余额、账单、欠费展示错误', 20
from complaint_category where code = 'PRODUCT_PLATFORM_QUERY'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_QUERY_ORDER', '订单状态展示异常', id, 3, '订单状态、进度、处理结果显示错误', 30
from complaint_category where code = 'PRODUCT_PLATFORM_QUERY'
on conflict (code) do nothing;


-- INSTALL_TIMELINESS
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_TIMELINESS_NOT_VISIT', '预约未上门', id, 3, '已预约但未按时上门', 10
from complaint_category where code = 'INSTALL_TIMELINESS'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_TIMELINESS_OVERTIME', '超时未完成', id, 3, '安装、移机、拆机超时未完成', 20
from complaint_category where code = 'INSTALL_TIMELINESS'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_TIMELINESS_REBOOK', '反复改约', id, 3, '多次改约、爽约', 30
from complaint_category where code = 'INSTALL_TIMELINESS'
on conflict (code) do nothing;


-- INSTALL_STANDARD
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_STANDARD_COMM', '沟通不规范', id, 3, '未按约联系、解释不到位、沟通差', 10
from complaint_category where code = 'INSTALL_STANDARD'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_STANDARD_PROCESS', '作业流程不规范', id, 3, '操作流程、施工流程不规范', 20
from complaint_category where code = 'INSTALL_STANDARD'
on conflict (code) do nothing;


-- INSTALL_QUALITY
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_QUALITY_WIRING', '布线安装质量问题', id, 3, '线路布放、走线、美观等问题', 10
from complaint_category where code = 'INSTALL_QUALITY'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_QUALITY_DEVICE', '设备安装质量问题', id, 3, '光猫、机顶盒、路由器安装质量问题', 20
from complaint_category where code = 'INSTALL_QUALITY'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_QUALITY_DAMAGE', '施工损坏问题', id, 3, '施工导致墙面、家具、环境损坏', 30
from complaint_category where code = 'INSTALL_QUALITY'
on conflict (code) do nothing;


-- INSTALL_RESULT
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_RESULT_SIGNAL', '信号覆盖不达预期', id, 3, '安装后信号覆盖与预期不符', 10
from complaint_category where code = 'INSTALL_RESULT'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_RESULT_SPEED', '实测速率不达标', id, 3, '安装后测速与承诺不一致', 20
from complaint_category where code = 'INSTALL_RESULT'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_RESULT_LAYOUT', '设备摆放不合理', id, 3, '设备位置不合理影响体验', 30
from complaint_category where code = 'INSTALL_RESULT'
on conflict (code) do nothing;


-- NETWORK_SIGNAL
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_SIGNAL_NO', '无信号', id, 3, '完全无信号、无法驻网', 10
from complaint_category where code = 'NETWORK_SIGNAL'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_SIGNAL_WEAK', '弱覆盖', id, 3, '信号弱、不稳定', 20
from complaint_category where code = 'NETWORK_SIGNAL'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_SIGNAL_AREA', '特定区域信号差', id, 3, '小区、楼宇、室内等特定区域信号差', 30
from complaint_category where code = 'NETWORK_SIGNAL'
on conflict (code) do nothing;


-- NETWORK_SPEED
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_SPEED_MOBILE', '移动上网慢', id, 3, '手机上网速度慢', 10
from complaint_category where code = 'NETWORK_SPEED'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_SPEED_BROADBAND', '宽带网速慢', id, 3, '宽带测速低、体验慢', 20
from complaint_category where code = 'NETWORK_SPEED'
on conflict (code) do nothing;


-- NETWORK_CALL
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_CALL_DROP', '掉话', id, 3, '通话中断、掉线', 10
from complaint_category where code = 'NETWORK_CALL'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_CALL_NOISE', '杂音回声', id, 3, '通话杂音、回声、听不清', 20
from complaint_category where code = 'NETWORK_CALL'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_CALL_CONNECT', '接通困难', id, 3, '拨打困难、接通慢、无法接通', 30
from complaint_category where code = 'NETWORK_CALL'
on conflict (code) do nothing;


-- NETWORK_ROAMING
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_ROAMING_DOMESTIC', '国内漫游异常', id, 3, '省际、跨区域通信异常', 10
from complaint_category where code = 'NETWORK_ROAMING'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_ROAMING_INTL', '国际港澳台漫游异常', id, 3, '国际及港澳台漫游异常', 20
from complaint_category where code = 'NETWORK_ROAMING'
on conflict (code) do nothing;


-- NETWORK_BROADBAND
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_BROADBAND_DISCONNECT', '宽带频繁掉线', id, 3, '宽带连接不稳定、频繁中断', 10
from complaint_category where code = 'NETWORK_BROADBAND'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_BROADBAND_DELAY', '宽带时延高卡顿', id, 3, '延迟高、游戏卡、视频卡顿', 20
from complaint_category where code = 'NETWORK_BROADBAND'
on conflict (code) do nothing;


-- BILLING_BILL
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_BILL_AMOUNT', '账单金额异常', id, 3, '账单金额与预期不符', 10
from complaint_category where code = 'BILLING_BILL'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_BILL_DETAIL', '账单明细不清', id, 3, '账单明细无法理解或展示不清', 20
from complaint_category where code = 'BILLING_BILL'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_BILL_PERIOD', '账期争议', id, 3, '出账周期、账期边界争议', 30
from complaint_category where code = 'BILLING_BILL'
on conflict (code) do nothing;


-- BILLING_PAYMENT
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_PAYMENT_FAIL', '缴费失败', id, 3, '缴费无法完成', 10
from complaint_category where code = 'BILLING_PAYMENT'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_PAYMENT_NOT_ARRIVE', '充值未到账', id, 3, '充值或缴费成功但余额未到账', 20
from complaint_category where code = 'BILLING_PAYMENT'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_PAYMENT_DEDUCT', '代扣失败争议', id, 3, '代扣未成功或异常扣款争议', 30
from complaint_category where code = 'BILLING_PAYMENT'
on conflict (code) do nothing;


-- BILLING_INVOICE
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_INVOICE_FAIL', '无法开票', id, 3, '发票申请失败', 10
from complaint_category where code = 'BILLING_INVOICE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_INVOICE_ERROR', '发票信息错误', id, 3, '抬头、金额、项目等开票信息错误', 20
from complaint_category where code = 'BILLING_INVOICE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_INVOICE_DELAY', '开票时效慢', id, 3, '开票流程处理慢', 30
from complaint_category where code = 'BILLING_INVOICE'
on conflict (code) do nothing;


-- SERVICE_OTHER_PROCESS
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_PROCESS_RESULT', '处理结果不认可', id, 3, '对最终处理方案不认可', 10
from complaint_category where code = 'SERVICE_OTHER_PROCESS'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_PROCESS_DELAY', '久拖未决', id, 3, '问题长时间未解决', 20
from complaint_category where code = 'SERVICE_OTHER_PROCESS'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_PROCESS_REPEAT', '重复投诉', id, 3, '同一问题多次投诉', 30
from complaint_category where code = 'SERVICE_OTHER_PROCESS'
on conflict (code) do nothing;


-- SERVICE_OTHER_FLOW
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_FLOW_TRANSFER', '转派错误', id, 3, '工单派错部门、转派错误', 10
from complaint_category where code = 'SERVICE_OTHER_FLOW'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_FLOW_TIMEOUT', '超时未处理', id, 3, '工单超时未处理', 20
from complaint_category where code = 'SERVICE_OTHER_FLOW'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_FLOW_PULL', '多部门扯皮', id, 3, '多部门相互推诿', 30
from complaint_category where code = 'SERVICE_OTHER_FLOW'
on conflict (code) do nothing;


-- SERVICE_OTHER_REPORT
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_REPORT_SPAM', '骚扰电话举报', id, 3, '骚扰电话、不当外呼举报', 10
from complaint_category where code = 'SERVICE_OTHER_REPORT'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_REPORT_CHANNEL', '渠道违规举报', id, 3, '营业厅、代理渠道违规行为举报', 20
from complaint_category where code = 'SERVICE_OTHER_REPORT'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_REPORT_SUGGEST', '建议表扬', id, 3, '建议、优化意见、表扬类事项', 30
from complaint_category where code = 'SERVICE_OTHER_REPORT'
on conflict (code) do nothing;