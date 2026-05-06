--一级分类
insert into complaint_category (code, name, parent_id, level, path, full_name, description, sort_order)
values
('FEE', '资费与收费争议', null, 1, null, '资费与收费争议', '套餐、套外、增值业务、权益金、违约金等收费问题', 10),
('SUBSCRIBE', '订购与退订争议', null, 1, null, '订购与退订争议', '业务订购、退订、自动续订、否认订购等问题', 20),
('OPEN_CLOSE', '开通、停用与销户', null, 1, null, '开通、停用与销户', '开通失败、关停争议、复机、拆机销户等问题', 30),
('MARKETING', '营销宣传与销售服务', null, 1, null, '营销宣传与销售服务', '宣传解释、营销误导、办理差错、漏受理等问题', 40),
('RULE', '规则政策争议', null, 1, null, '规则政策争议', '活动规则、生失效规则、办理规则、资格条件争议', 50),
('PRODUCT_PLATFORM', '产品功能与平台使用', null, 1, null, '产品功能与平台使用', 'APP、网厅、平台、产品功能使用异常', 60),
('INSTALL_SERVICE', '装维与交付服务', null, 1, null, '装维与交付服务', '安装、履约、上门、施工质量等问题', 70),
('NETWORK', '网络与通信质量', null, 1, null, '网络与通信质量', '无信号、网速慢、掉话、宽带质量等问题', 80),
('BILLING', '账单、缴费与发票', null, 1, null, '账单、缴费与发票', '账单争议、缴费失败、充值未到账、发票问题', 90),
('SERVICE_OTHER', '服务投诉与其他', null, 1, null, '服务投诉与其他', '投诉处理不满意、工单流转、举报建议等', 100)
on conflict (code) do nothing;