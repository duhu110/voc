--1 产品标签
insert into complaint_tag (group_id, code, name, description, sort_order)
select g.id, v.code, v.name, v.description, v.sort_order
from complaint_tag_group g
join (
    values
    ('MOBILE', '移动业务', '手机号、语音、流量等移动业务', 10),
    ('BROADBAND', '宽带业务', '家庭宽带业务', 20),
    ('IPTV', 'IPTV业务', '电视业务', 30),
    ('FUSION_PACKAGE', '融合套餐', '移动+宽带+电视等融合产品', 40),
    ('VALUE_ADDED', '增值业务', '铃音、会员、订阅等', 50),
    ('WINGPAY', '翼支付', '翼支付、权益金等金融支付类', 60),
    ('DEVICE', '终端设备', '手机、光猫、机顶盒等设备', 70)
) as v(code, name, description, sort_order)
on g.code = 'PRODUCT'
on conflict (group_id, code) do nothing;
--2 渠道标签
insert into complaint_tag (group_id, code, name, description, sort_order)
select g.id, v.code, v.name, v.description, v.sort_order
from complaint_tag_group g
join (
    values
    ('HALL', '营业厅', '自有营业厅或线下门店', 10),
    ('AGENT', '代理渠道', '社会代理点、合作渠道', 20),
    ('CALL_CENTER', '客服热线', '10000号等热线渠道', 30),
    ('APP', 'APP', '手机APP办理或查询', 40),
    ('WEB', '网上营业厅', '网页端办理渠道', 50),
    ('OUTBOUND', '外呼营销', '电话营销、主动外呼', 60),
    ('DOOR_SERVICE', '上门服务', '装维、客户经理上门', 70)
) as v(code, name, description, sort_order)
on g.code = 'CHANNEL'
on conflict (group_id, code) do nothing;
--3 根因标签
insert into complaint_tag (group_id, code, name, description, sort_order)
select g.id, v.code, v.name, v.description, v.sort_order
from complaint_tag_group g
join (
    values
    ('MISLEADING', '营销误导', '承诺与实际不符、夸大宣传', 10),
    ('UNCLEAR_EXPLANATION', '解释不清', '规则、资费、流程说明不清楚', 20),
    ('NOT_INFORMED', '未充分告知', '关键收费或规则未明确告知', 30),
    ('DENY_ORDER', '用户否认订购', '用户否认主动办理或订购', 40),
    ('PROCESS_ERROR', '办理差错', '办理错误、办错套餐、办错产品', 50),
    ('MISS_ACCEPT', '漏受理', '应受理未受理、遗漏处理', 60),
    ('SYSTEM_ERROR', '系统异常', '系统状态、同步、接口异常', 70),
    ('RULE_DISPUTE', '规则不认可', '不接受现有业务规则或资费规则', 80),
    ('DELAYED_FULFILLMENT', '履约不及时', '上门、安装、拆机、开通处理慢', 90),
    ('SERVICE_ATTITUDE', '服务态度问题', '沟通态度差、服务体验差', 100)
) as v(code, name, description, sort_order)
on g.code = 'ROOT_CAUSE'
on conflict (group_id, code) do nothing;
--4 责任条线标签
insert into complaint_tag (group_id, code, name, description, sort_order)
select g.id, v.code, v.name, v.description, v.sort_order
from complaint_tag_group g
join (
    values
    ('MARKET', '市场条线', '产品、资费、活动、销售政策相关', 10),
    ('CUSTOMER_SERVICE', '客服条线', '热线、解释、回访、工单处理相关', 20),
    ('CHANNEL_MGMT', '渠道管理', '营业厅、代理点、销售人员相关', 30),
    ('NETWORK_OP', '网运条线', '网络、宽带、开通、停机相关', 40),
    ('INSTALL_MAINTAIN', '装维条线', '安装维护、上门服务相关', 50),
    ('IT', 'IT系统', '系统、平台、数据同步相关', 60),
    ('FINANCE', '财务条线', '账务、退款、发票相关', 70),
    ('WINGPAY_TEAM', '支付金融条线', '翼支付、权益金等相关', 80)
) as v(code, name, description, sort_order)
on g.code = 'RESPONSIBILITY'
on conflict (group_id, code) do nothing;
--5 诉求标签
insert into complaint_tag (group_id, code, name, description, sort_order)
select g.id, v.code, v.name, v.description, v.sort_order
from complaint_tag_group g
join (
    values
    ('EXPLAIN', '解释说明', '要求解释清楚原因或规则', 10),
    ('REFUND', '退费', '要求退回费用', 20),
    ('CANCEL', '取消业务', '要求退订、取消、拆机、销户', 30),
    ('RESTORE', '恢复服务', '要求复机、恢复正常使用', 40),
    ('COMPENSATE', '赔偿补偿', '要求额外补偿、赔付', 50),
    ('APOLOGIZE', '道歉', '要求道歉', 60),
    ('FAST_PROCESS', '加快处理', '要求尽快处理', 70),
    ('PUNISH', '追责处罚', '要求追责相关人员或渠道', 80)
) as v(code, name, description, sort_order)
on g.code = 'REQUEST'
on conflict (group_id, code) do nothing;
--6 风险标签
insert into complaint_tag (group_id, code, name, description, sort_order)
select g.id, v.code, v.name, v.description, v.sort_order
from complaint_tag_group g
join (
    values
    ('REPEATED', '重复投诉', '同一问题多次投诉', 10),
    ('ESCALATED', '升级投诉', '有升级趋势或已升级', 20),
    ('REGULATORY', '监管风险', '涉及监管转办或工信部', 30),
    ('PUBLIC_OPINION', '舆情风险', '可能引发媒体或网络舆情', 40),
    ('HIGH_VALUE', '高价值客户', '重要客户、高价值客户', 50),
    ('BATCH_ISSUE', '批量问题', '批量相似问题', 60),
    ('COMPLIANCE', '合规风险', '涉及资费、告知、营销合规', 70)
) as v(code, name, description, sort_order)
on g.code = 'RISK'
on conflict (group_id, code) do nothing;
--7 情绪标签
insert into complaint_tag (group_id, code, name, description, sort_order)
select g.id, v.code, v.name, v.description, v.sort_order
from complaint_tag_group g
join (
    values
    ('CALM', '平稳', '客户情绪平稳', 10),
    ('UNSATISFIED', '不满', '客户表达明显不满意', 20),
    ('AGITATED', '激动', '客户情绪激动', 30),
    ('ANGRY', '强烈投诉', '客户强烈不满并可能升级', 40)
) as v(code, name, description, sort_order)
on g.code = 'EMOTION'
on conflict (group_id, code) do nothing;
--8 处理结果标签
insert into complaint_tag (group_id, code, name, description, sort_order)
select g.id, v.code, v.name, v.description, v.sort_order
from complaint_tag_group g
join (
    values
    ('ACCEPTED_AFTER_EXPLAIN', '解释后接受', '已解释，客户接受', 10),
    ('REFUNDED', '已退费', '已完成退费', 20),
    ('COMPENSATED', '已补偿', '已给予补偿', 30),
    ('RESTORED', '已恢复', '业务或服务已恢复', 40),
    ('COMPLETED_CANCEL', '已取消/已销户', '取消、退订、销户已完成', 50),
    ('USER_WITHDRAWN', '用户撤诉', '客户主动撤销投诉', 60),
    ('NOT_ACCEPTED', '用户不认可', '处理后用户仍不认可', 70),
    ('PENDING', '继续处理', '尚未完结，需要继续跟进', 80)
) as v(code, name, description, sort_order)
on g.code = 'RESULT'
on conflict (group_id, code) do nothing;