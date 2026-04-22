# category_v2.json 第六轮真实样本验证报告

- 模型：`Qwen3-Max`
- 分类源：`D:\project\FullStack\voc\voc_agent\converger_agent\data\category_v2.json`
- 样本数：`10`
- 一级命中：`9/10`
- 二级命中：`9/10`
- 叶子命中：`8/10`

## 样本结果

### WeComQH20240802101714527035

- 人工判断：`INSTALL_DELIVERY / INSTALL_STANDARD_AND_RESULT / ONSITE_SERVICE_IRREGULAR`
- AI 判断：`INSTALL_DELIVERY / INSTALL_STANDARD_AND_RESULT / ONSITE_SERVICE_IRREGULAR / 上门服务不规范`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：装维已上门，但没有解释清楚“没有资源无法安装”，核心是上门服务不规范。
- AI 理由：装维人员已上门，但未对‘无资源’情况进行清晰解释，属于服务过程中的解释不规范，符合‘上门服务不规范’的定义。根据歧义规则R06，优先按用户感知的服务结果归类，而非后台施工原因；且问题核心并非履约延迟或开通失败，而是服务过程中的沟通不规范。

### WeComQH20240728095528188566

- 人工判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / PROMISE_NOT_FULFILLED`
- AI 判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / BENEFIT_NOT_DELIVERED / 赠品/权益未兑现`
- 命中情况：一级=`True`，二级=`True`，叶子=`False`
- 人工理由：工作人员承诺免费赠送监控但最终未兑现，按已确认规则优先归承诺未兑现。
- AI 理由：根据歧义规则 R02，用户感知是权益（免费监控）没有兑现；同时工单内容明确提到‘承诺免费赠送监控’但未安装，符合‘赠品/权益未兑现’的定义。虽然涉及承诺，但核心争议点在于具体权益未交付，优先归入 BENEFIT_NOT_DELIVERED 而非 PROMISE_NOT_FULFILLED。

### WeComQH20240714184406787934

- 人工判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / BENEFIT_NOT_DELIVERED`
- AI 判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / BENEFIT_NOT_DELIVERED / 赠品/权益未兑现`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户感知是礼包里的腾讯视频会员权益拿不到、不能用，按已确认规则优先归赠品/权益未兑现。
- AI 理由：根据歧义规则 R02，用户感知是权益没有兑现，应优先归入赠品/权益未兑现。工单明确描述用户已办理礼包但腾讯视频会员权益无法使用，属于权益未到账或不能使用的情形。

### WeComQH20240713102056192380

- 人工判断：`SUBSCRIBE_CANCEL / CANCEL_AND_UNSUBSCRIBE / CANCEL_FAILURE`
- AI 判断：`SUBSCRIBE_CANCEL / CANCEL_AND_UNSUBSCRIBE / CANCEL_FAILURE / 业务退订/取消失败`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户明确要求取消连续包月业务，但系统异常导致取消不成功，核心是退订失败。
- AI 理由：用户明确要求取消指定增值业务（芒果TV会员+流量包），但因系统问题导致取消操作未能完成，符合‘业务退订/取消失败’的定义。

### WeComQH20240712180131851489

- 人工判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / ORDER_DENIAL`
- AI 判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / ORDER_DENIAL / 用户否认订购`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户对芒果TV会员权益费用不认可并明确否认订购，核心是订购关系不认可。
- AI 理由：根据歧义规则 R03，用户明确否认订购芒果TV会员权益，核心争议点在于否认订购关系本身，而非费用金额或权益未到账，因此应归入“用户否认订购”分类。

### WeComQH20240604105832012251

- 人工判断：`FEE_BILLING / ACCOUNT_AND_PAYMENT / PAYMENT_RECHARGE_ISSUE`
- AI 判断：`FEE_BILLING / ACCOUNT_AND_PAYMENT / PAYMENT_RECHARGE_ISSUE / 充值缴费异常`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：缴费后部分金额被冲正并导致欠费停机，核心是充值缴费异常。
- AI 理由：工单核心问题是缴费后部分金额被冲正，导致服务停机，属于充值缴费到账结果异常，符合‘充值缴费异常’叶子分类定义。

### WeComQH20240531105149107161

- 人工判断：`OPEN_RECOVERY_CONTROL / RECOVERY_AND_UNBLOCK / RECOVERY_DELAY_OR_FAILURE`
- AI 判断：`OPEN_RECOVERY_CONTROL / RECOVERY_AND_UNBLOCK / RECOVERY_DELAY_OR_FAILURE / 复机/恢复失败或不及时`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：已到营业厅申请复机，但仍未恢复，核心是复机/恢复失败或不及时。
- AI 理由：用户明确表示已到营业厅申请复机但至今未恢复，核心问题是复机申请后未能及时或成功恢复通信服务，符合‘复机/恢复失败或不及时’的定义。

### WeComQH20240602101810654310

- 人工判断：`FEE_BILLING / REFUND_PENALTY_RIGHTS / REFUND_NOT_ARRIVED`
- AI 判断：`FEE_BILLING / REFUND_PENALTY_RIGHTS / REFUND_NOT_ARRIVED / 返费/赠费/退款未到账`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：拆机后承诺退设备调测费但一直未退，核心是退款未到账。
- AI 理由：根据歧义规则R00，只要最终争议点是退款未到账，应优先归入'返费/赠费/退款未到账'。虽然涉及工作人员承诺，但核心诉求是已承诺的退款未实际到账，符合该叶子分类定义。

### WeComQH20240601125916780935

- 人工判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / MISLEADING_EXPLANATION`
- AI 判断：`RULE_POLICY / USAGE_AND_LIMIT_RULE / CONTRACT_LIMIT_RULE_DISPUTE / 合约限制争议`
- 命中情况：一级=`False`，二级=`False`，叶子=`False`
- 人工理由：业务是办过的，但办理时未告知合约，按已确认规则优先归宣传/解释不清或误导。
- AI 理由：用户核心争议点在于办理业务时未被告知存在合约限制，且要求取消受合约约束的业务，符合‘对合约期、限制条件、提前取消限制存在争议’的定义。虽然涉及权益金，但用户主要诉求是取消带合约的礼包，而非权益未到账或费用金额问题，因此优先归入合约限制争议。

### WeComQH20240525115416670531

- 人工判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / ORDER_DENIAL`
- AI 判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / ORDER_DENIAL / 用户否认订购`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户称自己没有订购过彩铃费用相关业务，核心是用户否认订购。
- AI 理由：用户明确表示未订购彩铃业务，符合歧义规则R03中‘只有明确否认订购关系本身时，才归用户否认订购’的条件。

## 失配观察

- `WeComQH20240728095528188566`: 人工=`PROMISE_NOT_FULFILLED`，AI=`BENEFIT_NOT_DELIVERED`
- `WeComQH20240601125916780935`: 人工=`MISLEADING_EXPLANATION`，AI=`CONTRACT_LIMIT_RULE_DISPUTE`
