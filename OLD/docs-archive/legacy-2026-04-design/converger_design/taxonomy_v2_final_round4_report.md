# V2 Final 第四轮真实样本验证报告

- 模型：`Qwen3-Max`
- 样本数：`10`
- 一级命中：`8/10`
- 二级命中：`8/10`
- 叶子命中：`8/10`

## 样本结果

### WeComQH20240730164542981925

- 人工判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / 用户否认订购`
- AI 判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / 用户否认订购`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户明确称从未办理、从未使用该合约业务，违约金只是后续结果，主矛盾是对订购关系本身不认可。
- AI 理由：工单核心是用户明确否认曾订购该权益合约业务，符合‘用户否认订购’分类的核心定义，应优先归入 SUBSCRIBE_CANCEL / ORDER_AND_DENY。虽然涉及违约金争议，但争议根源在于用户否认订购行为本身，而非费用计算规则或金额问题。

### WeComQH20240730102638617626

- 人工判断：`FEE_BILLING / PACKAGE_AND_USAGE_FEE / 增值业务收费争议`
- AI 判断：`FEE_BILLING / PACKAGE_AND_USAGE_FEE / 增值业务收费争议`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：ITV 点播节目收费不认可并要求退费，本质是增值业务收费争议。
- AI 理由：工单核心是用户对已产生的增值业务（IPTV点播节目）费用不认可并要求退款，属于增值业务收费争议，而非否认订购或规则问题。

### WeComQH20240725153319375038

- 人工判断：`FEE_BILLING / REFUND_PENALTY_RIGHTS / 返费/赠费/退款未到账`
- AI 判断：`FEE_BILLING / REFUND_PENALTY_RIGHTS / 返费/赠费/退款未到账`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：宽带无法安装后已做退款，但两个月仍未到账，核心是退款未到账。
- AI 理由：工单核心问题是用户已申请退款但长时间未到账，属于费用类退款未兑现问题，与退款流程和到账时效直接相关，符合 FEE_BILLING / REFUND_PENALTY_RIGHTS / 返费/赠费/退款未到账 分类。

### WeComQH20240719134151511247

- 人工判断：`FEE_BILLING / ACCOUNT_AND_PAYMENT / 充值缴费异常`
- AI 判断：`FEE_BILLING / ACCOUNT_AND_PAYMENT / 充值缴费异常`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：多渠道充值缴费均异常，用户侧无法成功缴费，核心是充值缴费异常。
- AI 理由：工单核心问题是用户无法完成充值缴费操作，涉及中国电信APP、微信、青海电信公众号等多个自营电子渠道的支付功能异常，符合‘充值缴费异常’分类。虽然涉及页面报错，但根本诉求是缴费失败，属于费用缴纳环节的问题，应归入FEE_BILLING/ACCOUNT_AND_PAYMENT下的充值缴费异常。

### WeComQH20240718122914465976

- 人工判断：`FEE_BILLING / ACCOUNT_AND_PAYMENT / 发票问题`
- AI 判断：`SERVICE_PROCESS / SPECIAL_REPORT_AND_MANAGER / 客户经理协调/业务核实`
- 命中情况：一级=`False`，二级=`False`，叶子=`False`
- 人工理由：用户核心诉求是开具单位发票，客户经理关机只是处理过程噪音。
- AI 理由：工单核心问题是用户无法联系到客户经理以完成发票开具事宜，属于对客户经理协调或业务核实流程的投诉，符合 SERVICE_PROCESS / SPECIAL_REPORT_AND_MANAGER 下的“客户经理协调/业务核实”分类。

### WeComQH20240718115433116433

- 人工判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / 宣传/解释不清或误导`
- AI 判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / 宣传/解释不清或误导`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：办理时承诺 500M 宽带和 100G 流量，实际只有 300M，核心是销售承诺与实际不符。
- AI 理由：工单核心问题是用户认为办理人员在营销过程中对宽带速率的宣传（500M）与实际交付速率（300M）不符，属于营销宣传内容不清晰或误导，符合 MARKETING_SALES / EXPLAIN_AND_COMMITMENT / 宣传/解释不清或误导 分类。虽然涉及速率问题，但争议根源在于销售承诺与实际不符，而非网络本身质量问题或安装交付过程问题。

### WeComQH20240617164801224634

- 人工判断：`RULE_POLICY / USAGE_AND_LIMIT_RULE / 达量降速/限速规则争议`
- AI 判断：`RULE_POLICY / USAGE_AND_LIMIT_RULE / 达量降速/限速规则争议`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：工单直接指向达量降速规则不合理，属于规则争议而不是费用争议。
- AI 理由：工单核心问题是客户对达量降速规则本身的合理性存在异议，属于规则政策类中的使用与限制规则争议，符合 RULE_POLICY / USAGE_AND_LIMIT_RULE / 达量降速/限速规则争议 的定义。

### WeComQH20240612182244390872

- 人工判断：`OPEN_RECOVERY_CONTROL / RECOVERY_AND_UNBLOCK / 复机/恢复失败或不及时`
- AI 判断：`OPEN_RECOVERY_CONTROL / RECOVERY_AND_UNBLOCK / 复机/恢复失败或不及时`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户称已经办理复机但仍无法拨出，核心是恢复失败或不及时。
- AI 理由：工单核心问题是用户已办理复机但通信功能未恢复，属于复机操作失败或未及时生效，符合 OPEN_RECOVERY_CONTROL / RECOVERY_AND_UNBLOCK / 复机/恢复失败或不及时 分类。

### WeComQH20240614200057363003

- 人工判断：`INSTALL_DELIVERY / INSTALL_TIMELINESS / 履约不及时/未履约`
- AI 判断：`INSTALL_DELIVERY / INSTALL_TIMELINESS / 履约不及时/未履约`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：预约拆机时限内师傅未上门，核心是履约未兑现。
- AI 理由：工单核心问题是装维人员未按预约时间上门拆机，属于履约不及时或未履约的情形，符合 INSTALL_DELIVERY / INSTALL_TIMELINESS 下的 '履约不及时/未履约' 分类。

### WeComQH20240617171844443001

- 人工判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / 宣传/解释不清或误导`
- AI 判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / 用户否认订购`
- 命中情况：一级=`False`，二级=`False`，叶子=`False`
- 人工理由：用户主张办理时未被告知两年合约期，导致现在取消要付违约金，核心是合约说明不清。
- AI 理由：工单核心是用户否认曾被告知合约期，属于对订购过程不知情的否认订购情形，符合 SUBSCRIBE_CANCEL / ORDER_AND_DENY / 用户否认订购 的定义。

## 失配观察

- `WeComQH20240718122914465976`: 人工=`发票问题`，AI=`客户经理协调/业务核实`
- `WeComQH20240617171844443001`: 人工=`宣传/解释不清或误导`，AI=`用户否认订购`
