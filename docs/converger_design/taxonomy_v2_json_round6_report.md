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
- AI 理由：用户的核心不满在于装维人员上门后未对“无资源”情况进行清晰解释，属于上门服务过程中解释不规范的问题，符合‘上门服务不规范’的定义。虽然涉及安装失败，但争议焦点不在开通结果本身，而在服务过程中的沟通与解释不到位，因此不归入开通失败类，而应归入服务不规范类。

### WeComQH20240728095528188566

- 人工判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / PROMISE_NOT_FULFILLED`
- AI 判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / BENEFIT_NOT_DELIVERED / 赠品/权益未兑现`
- 命中情况：一级=`True`，二级=`True`，叶子=`False`
- 人工理由：工作人员承诺免费赠送监控但最终未兑现，按已确认规则优先归承诺未兑现。
- AI 理由：根据歧义规则 R02，用户感知是承诺的监控（作为赠品或权益）未兑现，且未涉及退款未到账（R00 不适用），因此优先归入赠品/权益未兑现。

### WeComQH20240714184406787934

- 人工判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / BENEFIT_NOT_DELIVERED`
- AI 判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / BENEFIT_NOT_DELIVERED / 赠品/权益未兑现`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户感知是礼包里的腾讯视频会员权益拿不到、不能用，按已确认规则优先归赠品/权益未兑现。
- AI 理由：根据歧义规则 R02，用户感知是权益没有兑现（腾讯视频会员无法使用），应优先归入赠品/权益未兑现。

### WeComQH20240713102056192380

- 人工判断：`SUBSCRIBE_CANCEL / CANCEL_AND_UNSUBSCRIBE / CANCEL_FAILURE`
- AI 判断：`SUBSCRIBE_CANCEL / CANCEL_AND_UNSUBSCRIBE / CANCEL_FAILURE / 业务退订/取消失败`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户明确要求取消连续包月业务，但系统异常导致取消不成功，核心是退订失败。
- AI 理由：用户明确要求取消某项增值业务（芒果TV会员流量包），但由于系统问题（带出无关操作）导致取消未成功，符合‘业务退订/取消失败’的定义。争议重心在于取消动作未能完成，而非费用、权益或规则本身。

### WeComQH20240712180131851489

- 人工判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / ORDER_DENIAL`
- AI 判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / ORDER_DENIAL / 用户否认订购`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户对芒果TV会员权益费用不认可并明确否认订购，核心是订购关系不认可。
- AI 理由：根据工单内容，用户明确否认订购芒果TV会员权益，符合歧义规则R03中‘只有明确否认订购关系本身时，才归用户否认订购’的条件，因此应归入该叶子分类。

### WeComQH20240604105832012251

- 人工判断：`FEE_BILLING / ACCOUNT_AND_PAYMENT / PAYMENT_RECHARGE_ISSUE`
- AI 判断：`FEE_BILLING / ACCOUNT_AND_PAYMENT / PAYMENT_RECHARGE_ISSUE / 充值缴费异常`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：缴费后部分金额被冲正并导致欠费停机，核心是充值缴费异常。
- AI 理由：工单核心问题是缴费后部分金额被冲正，导致到账异常并引发停机，属于充值缴费到账结果异常，符合‘充值缴费异常’叶子分类定义。根据歧义规则R05（以最终是否完成履约为优先判断），用户缴费未完全履约到账，应归入此分类，而非返费未到账或费用争议类。

### WeComQH20240531105149107161

- 人工判断：`OPEN_RECOVERY_CONTROL / RECOVERY_AND_UNBLOCK / RECOVERY_DELAY_OR_FAILURE`
- AI 判断：`OPEN_RECOVERY_CONTROL / RECOVERY_AND_UNBLOCK / RECOVERY_DELAY_OR_FAILURE / 复机/恢复失败或不及时`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：已到营业厅申请复机，但仍未恢复，核心是复机/恢复失败或不及时。
- AI 理由：用户已申请复机但未及时恢复，核心问题是复机处理延迟或失败，符合‘复机/恢复失败或不及时’分类。

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
- AI 理由：用户核心争议点在于办理业务时未被告知存在合约限制，且要求取消受合约约束的业务，符合‘对合约期、限制条件、提前取消限制存在争议’的定义。虽然涉及权益金，但用户主要诉求是取消带合约的礼包，而非权益未到账或费用金额本身，因此优先归入合约限制争议。

### WeComQH20240525115416670531

- 人工判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / ORDER_DENIAL`
- AI 判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / ORDER_DENIAL / 用户否认订购`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户称自己没有订购过彩铃费用相关业务，核心是用户否认订购。
- AI 理由：用户明确表示未订购彩铃业务，符合歧义规则R03中‘只有明确否认订购关系本身时，才归用户否认订购’的条件。

## 失配观察

- `WeComQH20240728095528188566`: 人工=`PROMISE_NOT_FULFILLED`，AI=`BENEFIT_NOT_DELIVERED`
- `WeComQH20240601125916780935`: 人工=`MISLEADING_EXPLANATION`，AI=`CONTRACT_LIMIT_RULE_DISPUTE`
