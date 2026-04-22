# V2 Final 第二轮真实样本验证报告

- 模型：`Qwen3-Max`
- 样本数：`10`
- 一级命中：`9/10`
- 二级命中：`8/10`
- 叶子命中：`7/10`

## 样本结果

### WeComQH20240705122615333767

- 人工判断：`MARKETING_SALES / SALES_PROCESS_AND_ATTITUDE / 业务办理差错/漏受理`
- AI 判断：`SUBSCRIBE_CANCEL / CANCEL_AND_UNSUBSCRIBE / 业务退订/取消争议`
- 命中情况：一级=`False`，二级=`False`，叶子=`False`
- 人工理由：办理套餐变更时承诺取消业务但未执行，核心是办理差错与漏受理。
- AI 理由：工单核心问题是用户主张工作人员承诺取消某项增值业务（智慧家庭单选月付礼包15元）但实际未取消，属于对业务退订或取消结果的争议，符合“业务退订/取消争议”分类。虽然涉及营销承诺，但根本诉求是取消未执行，而非承诺本身未兑现，因此优先归入退订争议而非营销承诺类。

### WeComQH20240719134927637641

- 人工判断：`SUBSCRIBE_CANCEL / CANCEL_AND_UNSUBSCRIBE / 业务退订/取消失败`
- AI 判断：`SUBSCRIBE_CANCEL / CANCEL_AND_UNSUBSCRIBE / 业务退订/取消争议`
- 命中情况：一级=`True`，二级=`True`，叶子=`False`
- 人工理由：客户持续要求取消合约业务但迟迟未取消，主矛盾是退订失败。
- AI 理由：工单核心问题是用户对业务退订存在争议，认为办理时未告知合约内容，且多次要求取消未果，属于退订过程中的规则与执行争议，符合“业务退订/取消争议”分类。

### 6004052025113093773147

- 人工判断：`OPEN_RECOVERY_CONTROL / SHUTDOWN_AND_CONTROL / 风险/模型关停不认可`
- AI 判断：`OPEN_RECOVERY_CONTROL / SHUTDOWN_AND_CONTROL / 风险/模型关停不认可`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：高风险双停引发的不认可，已将风险关停与模型关停合并。
- AI 理由：工单核心问题是用户不认可因外呼高风险模型触发的‘高风险双停’关停操作，属于对系统模型判定导致的关停行为提出异议，符合‘风险/模型关停不认可’分类。虽涉及复机流程，但根本争议点在于关停本身的合理性，而非复机执行过程。

### WeComQH20240811112847215417

- 人工判断：`PRODUCT_PLATFORM / BASIC_FUNCTION / 短信功能异常`
- AI 判断：`PRODUCT_PLATFORM / BASIC_FUNCTION / 短信功能异常`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：天气预报短信收不到，属于短信功能异常。
- AI 理由：工单核心问题是用户无法接收到天气预报短信，属于短信功能使用异常，与收费、订购、网络质量等无关，应归入产品平台类的基础功能异常中的短信功能异常。

### 6004052025113090000571

- 人工判断：`FEE_BILLING / ACCOUNT_AND_PAYMENT / 充值缴费异常`
- AI 判断：`FEE_BILLING / ACCOUNT_AND_PAYMENT / 充值缴费异常`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：抖音极速版提现充值后费用未到账，本质是充值缴费异常。
- AI 理由：工单核心问题是客户完成充值操作后费用未到账，属于账户充值过程中的异常情况，符合‘充值缴费异常’分类。

### 6004052025113099937256

- 人工判断：`FEE_BILLING / REFUND_PENALTY_RIGHTS / 违约金/滞纳金争议`
- AI 判断：`FEE_BILLING / REFUND_PENALTY_RIGHTS / 违约金/滞纳金争议`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：客户提前取消协议产生违约金并要求减免，属于违约金争议。
- AI 理由：工单核心问题是客户对提前解约产生的违约金存在异议并要求减免，属于费用类争议中的违约金问题，与退订流程或服务过程无直接关联，应归入 FEE_BILLING / REFUND_PENALTY_RIGHTS 下的‘违约金/滞纳金争议’。

### 6004052025113090184061

- 人工判断：`RULE_POLICY / ACTIVITY_AND_EFFECTIVE_RULE / 生效/失效规则争议`
- AI 判断：`RULE_POLICY / USAGE_AND_LIMIT_RULE / 达量降速/限速规则争议`
- 命中情况：一级=`True`，二级=`False`，叶子=`False`
- 人工理由：客户要求套餐内流量用完立即断网，对业务生效规则不认可。
- AI 理由：工单核心是用户对套餐流量用尽后未自动断网、继续产生套外费用的规则不认可，实质是对流量使用上限及后续处理机制（是否断网或限速）的规则争议，符合‘达量降速/限速规则争议’分类。虽然涉及费用，但争议根源在于规则设计而非费用本身，故不归入FEE_BILLING类。

### WeComQH20240825171749823808

- 人工判断：`INSTALL_DELIVERY / INSTALL_TIMELINESS / 履约不及时/未履约`
- AI 判断：`INSTALL_DELIVERY / INSTALL_TIMELINESS / 履约不及时/未履约`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：移机业务长期未安装，上门履约超时。
- AI 理由：工单核心问题是装维人员未按约定完成移机安装，属于履约不及时或未履约，符合 INSTALL_DELIVERY / INSTALL_TIMELINESS 下的 '履约不及时/未履约' 分类。

### WeComQH20240714163202760929

- 人工判断：`NETWORK_QUALITY / NETWORK_QUALITY / 宽带网速慢`
- AI 判断：`NETWORK_QUALITY / NETWORK_QUALITY / 宽带网速慢`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：工单直接描述宽带网速慢。
- AI 理由：工单核心问题是宽带网络速度慢，属于网络表现问题，应归入 NETWORK_QUALITY 下的‘宽带网速慢’分类。

### 2025113014090756459513

- 人工判断：`SERVICE_PROCESS / SPECIAL_REPORT_AND_MANAGER / 客户经理协调/业务核实`
- AI 判断：`SERVICE_PROCESS / SPECIAL_REPORT_AND_MANAGER / 客户经理协调/业务核实`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：工单主诉求是要求客户经理联系核实业务，不应被业务内容带偏。
- AI 理由：工单核心是客户因无法联系客户经理而请求运营商安排其联系以核实IPTV增值包收费情况，属于对客户经理协调与业务核实的流程性诉求，符合 SERVICE_PROCESS / SPECIAL_REPORT_AND_MANAGER / 客户经理协调/业务核实 分类。

## 失配观察

- `WeComQH20240705122615333767`: 人工=`业务办理差错/漏受理`，AI=`业务退订/取消争议`
- `WeComQH20240719134927637641`: 人工=`业务退订/取消失败`，AI=`业务退订/取消争议`
- `6004052025113090184061`: 人工=`生效/失效规则争议`，AI=`达量降速/限速规则争议`
