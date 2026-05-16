# V2 Final 第五轮真实样本验证报告

- 模型：`Qwen3-Max`
- 样本数：`10`
- 一级命中：`9/10`
- 二级命中：`9/10`
- 叶子命中：`8/10`

## 样本结果

### WeComQH20240802101714527035

- 人工判断：`INSTALL_DELIVERY / INSTALL_STANDARD_AND_RESULT / 上门服务不规范`
- AI 判断：`INSTALL_DELIVERY / INSTALL_STANDARD_AND_RESULT / 上门服务不规范`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：装维已上门，但只给出“没有资源无法安装”的模糊解释，核心是上门交付解释与服务规范问题。
- AI 理由：工单核心问题是装维人员上门服务过程中未对‘无资源’情况进行清晰解释，属于上门服务过程中的沟通与操作不规范，符合 INSTALL_DELIVERY / INSTALL_STANDARD_AND_RESULT / 上门服务不规范 的定义。

### WeComQH20240728095528188566

- 人工判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / 赠品/权益未兑现`
- AI 判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / 承诺未兑现`
- 命中情况：一级=`True`，二级=`True`，叶子=`False`
- 人工理由：办理套餐时承诺免费赠送监控，但一直未安装，核心是承诺赠品未兑现。
- AI 理由：工单核心是营销过程中承诺赠送监控但未履行，且用户套餐中无该业务，符合‘承诺未兑现’分类，而非安装履约或订购否认问题。

### WeComQH20240714184406787934

- 人工判断：`RULE_POLICY / ACTIVITY_AND_EFFECTIVE_RULE / 营销活动规则争议`
- AI 判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / 赠品/权益未兑现`
- 命中情况：一级=`False`，二级=`False`，叶子=`False`
- 人工理由：用户办理礼包后会员权益无法使用，主问题更像活动权益兑现规则争议。
- AI 理由：工单核心问题是用户已参与营销活动并成功办理礼包，但所承诺的腾讯视频会员权益无法使用，属于营销活动中赠品或权益未按规则兑现的情形，应归入 MARKETING_SALES / EXPLAIN_AND_COMMITMENT / 赠品/权益未兑现。

### WeComQH20240713102056192380

- 人工判断：`SUBSCRIBE_CANCEL / CANCEL_AND_UNSUBSCRIBE / 业务退订/取消失败`
- AI 判断：`SUBSCRIBE_CANCEL / CANCEL_AND_UNSUBSCRIBE / 业务退订/取消失败`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户明确要求取消连续包月业务，但系统带出异常属性导致取消不成功，核心是退订失败。
- AI 理由：工单核心问题是用户在尝试取消已订购的增值业务（芒果TV会员流量包）时因系统异常导致退订操作失败，符合‘业务退订/取消失败’分类。

### WeComQH20240712180131851489

- 人工判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / 用户否认订购`
- AI 判断：`SUBSCRIBE_CANCEL / ORDER_AND_DENY / 用户否认订购`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户对芒果TV会员权益费用不认可并明确否认订购，核心是订购关系不认可。
- AI 理由：工单核心问题是用户明确否认曾订购芒果TV会员权益，并对因此产生的费用不认可，符合‘用户否认订购’这一叶子分类的定义。

### WeComQH20240604105832012251

- 人工判断：`FEE_BILLING / ACCOUNT_AND_PAYMENT / 充值缴费异常`
- AI 判断：`FEE_BILLING / ACCOUNT_AND_PAYMENT / 充值缴费异常`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户缴费 200 元中有 100 元被冲正并导致宽带欠费停机，核心是缴费结果异常。
- AI 理由：工单核心问题是用户已缴费但部分金额被冲正，导致欠费停机，属于缴费到账异常问题，应归入充值缴费异常。

### WeComQH20240531105149107161

- 人工判断：`OPEN_RECOVERY_CONTROL / RECOVERY_AND_UNBLOCK / 复机/恢复失败或不及时`
- AI 判断：`OPEN_RECOVERY_CONTROL / RECOVERY_AND_UNBLOCK / 复机/恢复失败或不及时`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：用户已到营业厅申请复机，但公安双停后仍未恢复，核心是恢复失败或不及时。
- AI 理由：工单核心问题是用户已申请复机但未及时恢复服务，属于复机失败或不及时的范畴，应归入 OPEN_RECOVERY_CONTROL / RECOVERY_AND_UNBLOCK。

### WeComQH20240521091329931527

- 人工判断：`MARKETING_SALES / SALES_PROCESS_AND_ATTITUDE / 业务办理差错/漏受理`
- AI 判断：`MARKETING_SALES / SALES_PROCESS_AND_ATTITUDE / 业务办理差错/漏受理`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：办理入网时承诺将旧号携转进套餐但迟迟没办成，核心是办理差错或漏受理。
- AI 理由：工单核心问题是工作人员在用户入网时承诺办理携号转网但实际未受理，属于营销销售环节的业务办理差错或漏受理，与给定分类中的 [MARKETING_SALES] / [SALES_PROCESS_AND_ATTITUDE] / 业务办理差错/漏受理 完全匹配。

### WeComQH20240524112207679068

- 人工判断：`FEE_BILLING / REFUND_PENALTY_RIGHTS / 返费/赠费/退款未到账`
- AI 判断：`FEE_BILLING / REFUND_PENALTY_RIGHTS / 返费/赠费/退款未到账`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：拆机后一直未退费，核心是退款未到账。
- AI 理由：工单核心问题是拆机后账户余额退款未到账，属于费用争议中的退款未到账情形，与给定叶子分类中的“返费/赠费/退款未到账”完全匹配。

### WeComQH20240524185814517932

- 人工判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / 宣传/解释不清或误导`
- AI 判断：`MARKETING_SALES / EXPLAIN_AND_COMMITMENT / 宣传/解释不清或误导`
- 命中情况：一级=`True`，二级=`True`，叶子=`True`
- 人工理由：办理融合套餐时未解释清楚携号转网副卡加入方式，导致后续上网费产生，核心是解释不清。
- AI 理由：工单核心问题是工作人员在营销办理过程中对携号转网及副卡加入规则解释不清，造成用户误解并产生费用，属于营销环节的解释误导问题，符合'MARKETING_SALES / EXPLAIN_AND_COMMITMENT / 宣传/解释不清或误导'分类。

## 失配观察

- `WeComQH20240728095528188566`: 人工=`赠品/权益未兑现`，AI=`承诺未兑现`
- `WeComQH20240714184406787934`: 人工=`营销活动规则争议`，AI=`赠品/权益未兑现`
