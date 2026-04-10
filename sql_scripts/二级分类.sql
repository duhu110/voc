/* =========================================================
   二级分类初始化
   ========================================================= */

-- FEE 资费与收费争议
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_PACKAGE', '套餐收费争议', id, 2, '套餐月费、升降档、融合套餐等收费争议', 10
from complaint_category where code = 'FEE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_EXTRA', '套外费用争议', id, 2, '流量、语音、短信、漫游等超套餐收费争议', 20
from complaint_category where code = 'FEE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_VALUE_ADDED', '增值业务收费争议', id, 2, '会员、订阅、铃音、自动续订等收费争议', 30
from complaint_category where code = 'FEE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_WINGPAY', '翼支付及权益争议', id, 2, '翼支付、权益金、支付类收费争议', 40
from complaint_category where code = 'FEE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_PENALTY', '违约金及滞纳金争议', id, 2, '违约金、滞纳金相关收费争议', 50
from complaint_category where code = 'FEE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_BROADBAND_TV', '宽带电视收费争议', id, 2, '宽带、IPTV等收费争议', 60
from complaint_category where code = 'FEE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_REFUND', '返费退款争议', id, 2, '返费、赠费、退款未到账等问题', 70
from complaint_category where code = 'FEE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'FEE_UNKNOWN', '不明收费争议', id, 2, '账单中不明扣费、未使用收费等问题', 80
from complaint_category where code = 'FEE'
on conflict (code) do nothing;


-- SUBSCRIBE 订购与退订争议
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_ORDER', '业务订购争议', id, 2, '未明确同意即订购、搭售、误办等', 10
from complaint_category where code = 'SUBSCRIBE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_CANCEL', '业务退订争议', id, 2, '退订失败、退订不及时、退订后仍收费等', 20
from complaint_category where code = 'SUBSCRIBE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_RENEW', '自动续订争议', id, 2, '自动续费、免费到期转收费等', 30
from complaint_category where code = 'SUBSCRIBE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SUBSCRIBE_DENY', '用户否认订购', id, 2, '用户否认主动订购某业务', 40
from complaint_category where code = 'SUBSCRIBE'
on conflict (code) do nothing;


-- OPEN_CLOSE 开通、停用与销户
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_OPENING', '开通失败', id, 2, '业务、宽带、号卡、套餐等开通失败', 10
from complaint_category where code = 'OPEN_CLOSE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_SHUTDOWN', '停机关停争议', id, 2, '欠费停机、风险关停、模型关停等争议', 20
from complaint_category where code = 'OPEN_CLOSE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_RECOVERY', '复机恢复争议', id, 2, '复机慢、恢复不及时、恢复失败等', 30
from complaint_category where code = 'OPEN_CLOSE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_CANCEL', '拆机销户', id, 2, '拆机、销户、销户后仍计费等问题', 40
from complaint_category where code = 'OPEN_CLOSE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'OPEN_CLOSE_ACTIVATION', '激活异常', id, 2, '号卡激活、实名认证、首登激活等异常', 50
from complaint_category where code = 'OPEN_CLOSE'
on conflict (code) do nothing;


-- MARKETING 营销宣传与销售服务
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_EXPLAIN', '宣传解释与营销误导', id, 2, '资费、活动、权益、规则等解释不清或误导', 10
from complaint_category where code = 'MARKETING'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_PROCESS', '办理差错与漏受理', id, 2, '办错、漏办、状态异常、受理错误', 20
from complaint_category where code = 'MARKETING'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_ATTITUDE', '服务态度问题', id, 2, '营业厅、客服、客户经理等服务态度问题', 30
from complaint_category where code = 'MARKETING'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'MARKETING_PROMISE', '承诺未兑现', id, 2, '承诺赠费、赠品、速率、权益未兑现', 40
from complaint_category where code = 'MARKETING'
on conflict (code) do nothing;


-- RULE 规则政策争议
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_ACTIVITY', '营销活动规则争议', id, 2, '活动参与条件、奖励发放、返费规则争议', 10
from complaint_category where code = 'RULE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_EFFECTIVE', '生效失效规则争议', id, 2, '套餐、业务生效/失效时间争议', 20
from complaint_category where code = 'RULE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_PROCESS', '办理规则争议', id, 2, '代办、异地办理、销户前置条件等规则争议', 30
from complaint_category where code = 'RULE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_USAGE', '使用规则争议', id, 2, '套餐使用范围、限速、封顶、定向流量等争议', 40
from complaint_category where code = 'RULE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'RULE_QUALIFICATION', '资格条件争议', id, 2, '老用户、新用户、特定渠道、特定套餐资格争议', 50
from complaint_category where code = 'RULE'
on conflict (code) do nothing;


-- PRODUCT_PLATFORM 产品功能与平台使用
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_BASIC', '基础功能异常', id, 2, '语音、短信、流量等基础功能异常', 10
from complaint_category where code = 'PRODUCT_PLATFORM'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_APP', 'APP网厅异常', id, 2, 'APP、网厅、小程序功能异常', 20
from complaint_category where code = 'PRODUCT_PLATFORM'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_ACCOUNT', '账号登录问题', id, 2, '账号登录失败、实名校验、权限异常', 30
from complaint_category where code = 'PRODUCT_PLATFORM'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'PRODUCT_PLATFORM_QUERY', '查询展示异常', id, 2, '套餐、余额、订单、账单展示异常', 40
from complaint_category where code = 'PRODUCT_PLATFORM'
on conflict (code) do nothing;


-- INSTALL_SERVICE 装维与交付服务
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_TIMELINESS', '履约时效问题', id, 2, '预约未上门、超时未处理、安装慢、拆机慢', 10
from complaint_category where code = 'INSTALL_SERVICE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_STANDARD', '上门服务不规范', id, 2, '服务流程、沟通、施工不规范', 20
from complaint_category where code = 'INSTALL_SERVICE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_QUALITY', '安装施工质量问题', id, 2, '安装质量、布线质量、设备安装质量问题', 30
from complaint_category where code = 'INSTALL_SERVICE'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'INSTALL_RESULT', '交付结果不符', id, 2, '交付结果与承诺不一致', 40
from complaint_category where code = 'INSTALL_SERVICE'
on conflict (code) do nothing;


-- NETWORK 网络与通信质量
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_SIGNAL', '信号覆盖问题', id, 2, '无信号、弱覆盖、特定区域信号差', 10
from complaint_category where code = 'NETWORK'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_SPEED', '网速质量问题', id, 2, '移动网速慢、宽带速率不达标', 20
from complaint_category where code = 'NETWORK'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_CALL', '通话质量问题', id, 2, '掉话、杂音、接通困难、通话中断', 30
from complaint_category where code = 'NETWORK'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_ROAMING', '漫游通信问题', id, 2, '省际、港澳台、国际漫游异常', 40
from complaint_category where code = 'NETWORK'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'NETWORK_BROADBAND', '宽带网络质量问题', id, 2, '宽带不稳定、频繁掉线、延迟高', 50
from complaint_category where code = 'NETWORK'
on conflict (code) do nothing;


-- BILLING 账单、缴费与发票
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_BILL', '账单争议', id, 2, '账单明细、账期、金额异常', 10
from complaint_category where code = 'BILLING'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_PAYMENT', '缴费充值问题', id, 2, '缴费失败、充值未到账、代扣失败', 20
from complaint_category where code = 'BILLING'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'BILLING_INVOICE', '发票问题', id, 2, '开票失败、发票信息错误、开票慢', 30
from complaint_category where code = 'BILLING'
on conflict (code) do nothing;


-- SERVICE_OTHER 服务投诉与其他
insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_PROCESS', '投诉处理不满意', id, 2, '处理结果不认可、久拖未决、重复投诉', 10
from complaint_category where code = 'SERVICE_OTHER'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_FLOW', '工单流转问题', id, 2, '转派错误、超时未处理、多部门扯皮', 20
from complaint_category where code = 'SERVICE_OTHER'
on conflict (code) do nothing;

insert into complaint_category (code, name, parent_id, level, description, sort_order)
select 'SERVICE_OTHER_REPORT', '举报建议表扬', id, 2, '举报、建议、表扬类事项', 30
from complaint_category where code = 'SERVICE_OTHER'
on conflict (code) do nothing;