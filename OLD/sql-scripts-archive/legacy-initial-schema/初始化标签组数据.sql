insert into complaint_tag_group (code, name, description, sort_order)
values
('PRODUCT', '产品标签', '投诉涉及的产品或业务对象', 10),
('CHANNEL', '渠道标签', '投诉发生或办理渠道', 20),
('ROOT_CAUSE', '根因标签', '问题产生的根本原因', 30),
('RESPONSIBILITY', '责任条线标签', '责任归属部门或条线', 40),
('REQUEST', '诉求标签', '客户希望得到的处理结果', 50),
('RISK', '风险标签', '风险等级或特殊风险属性', 60),
('EMOTION', '情绪标签', '客户情绪状态', 70),
('RESULT', '处理结果标签', '最终处理结果', 80)
on conflict (code) do nothing;