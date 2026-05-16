# converger 最终收敛分类体系 V2

## 1. 目标

这份文档给出一版可直接用于 `complaint_taxonomy_converger` 的最终收敛分类体系。

设计目标只有 3 个：

- 让 AI 更容易稳定选择
- 保留足够的业务区分度
- 能和后续处理建议直接衔接

这版不是旧分类体系的翻译版，也不是和旧分类做一一映射，而是面向新 agent 的运行时分类体系。

---

## 2. 小样本实测结论

我已经基于真实工单做了一轮 `OpenAI-compatible` 模型实测，脚本和报告在：

- [validate_v2_samples.py](D:/project/FullStack/voc/voc_agent/complaint_taxonomy_converger/scripts/validate_v2_samples.py)
- [taxonomy_v2_validation_report.md](D:/project/FullStack/voc/docs/converger_design/taxonomy_v2_validation_report.md)
- [taxonomy_v2_validation_report.json](D:/project/FullStack/voc/docs/converger_design/taxonomy_v2_validation_report.json)

实测模型：

- `Qwen3-Max`

实测结果：

- 样本数：`12`
- 一级命中：`11/12`
- 二级命中：`8/12`
- 叶子命中：`5/12`

这轮结果说明：

- 一级域设计已经比较稳定
- 二级域大体可用
- 叶子层仍有几组边界太近，需要继续合并

我又按这份 `V2 final` 体系追加做了第二轮真实验证，脚本和报告在：

- [validate_v2_final_round2.py](D:/project/FullStack/voc/voc_agent/complaint_taxonomy_converger/scripts/validate_v2_final_round2.py)
- [taxonomy_v2_final_round2_report.md](D:/project/FullStack/voc/docs/converger_design/taxonomy_v2_final_round2_report.md)
- [taxonomy_v2_final_round2_report.json](D:/project/FullStack/voc/docs/converger_design/taxonomy_v2_final_round2_report.json)

第二轮结果：

- 样本数：`10`
- 一级命中：`9/10`
- 二级命中：`8/10`
- 叶子命中：`7/10`

第二轮说明：

- 一级域已经基本稳定
- 二级域大多数样本可稳定命中
- 剩余冲突主要集中在少数近邻叶子，而不是顶层结构失稳
- `V2 final` 已经可以作为 converger 的首版运行时分类体系

我继续按同一流程做了第三轮真实验证，脚本和报告在：

- [validate_v2_final_round3.py](D:/project/FullStack/voc/voc_agent/complaint_taxonomy_converger/scripts/validate_v2_final_round3.py)
- [taxonomy_v2_final_round3_report.md](D:/project/FullStack/voc/docs/converger_design/taxonomy_v2_final_round3_report.md)
- [taxonomy_v2_final_round3_report.json](D:/project/FullStack/voc/docs/converger_design/taxonomy_v2_final_round3_report.json)

第三轮结果：

- 样本数：`10`
- 一级命中：`7/10`
- 二级命中：`6/10`
- 叶子命中：`6/10`

第三轮说明：

- 这轮故意挑了更多边界样本，不是常规高频样本
- 失配主要集中在“用户可感知问题”与“后台处理原因”之间的归因差异
- 结构本身仍可用，但 prompt 里必须补更明确的优先级规则

我继续做了第四轮真实验证，脚本和报告在：

- [validate_v2_final_round4.py](D:/project/FullStack/voc/voc_agent/complaint_taxonomy_converger/scripts/validate_v2_final_round4.py)
- [taxonomy_v2_final_round4_report.md](D:/project/FullStack/voc/docs/converger_design/taxonomy_v2_final_round4_report.md)
- [taxonomy_v2_final_round4_report.json](D:/project/FullStack/voc/docs/converger_design/taxonomy_v2_final_round4_report.json)

第四轮结果：

- 样本数：`10`
- 一级命中：`8/10`
- 二级命中：`8/10`
- 叶子命中：`8/10`

第四轮说明：

- 在收费、退费、缴费、发票、规则、恢复、履约这些高频问题上，`V2 final` 已经比较稳定
- 剩余冲突主要集中在“发票问题 vs 客户经理协调”和“未告知合约期 vs 用户否认订购”两组近邻边界
- 现阶段继续大改分类树的收益已经不高，后续更应该靠 prompt 规则和样例约束来稳住输出

我继续做了第五轮真实验证，脚本和报告在：

- [validate_v2_final_round5.py](D:/project/FullStack/voc/voc_agent/complaint_taxonomy_converger/scripts/validate_v2_final_round5.py)
- [taxonomy_v2_final_round5_report.md](D:/project/FullStack/voc/docs/converger_design/taxonomy_v2_final_round5_report.md)
- [taxonomy_v2_final_round5_report.json](D:/project/FullStack/voc/docs/converger_design/taxonomy_v2_final_round5_report.json)

第五轮结果：

- 样本数：`10`
- 一级命中：`9/10`
- 二级命中：`9/10`
- 叶子命中：`8/10`

第五轮说明：

- `V2 final` 已经进入平台期，主要高频类可以稳定判断
- 当前残留冲突主要只剩营销域内部的近邻叶子
- 尤其是：
  - `承诺未兑现` vs `赠品/权益未兑现`
  - `营销活动规则争议` vs `赠品/权益未兑现`
- 这说明后续如果还想继续提高命中率，收益更高的动作不是继续改一级、二级结构，而是：
  - 在 prompt 里补更细的营销域示例
  - 或者直接把营销域的近邻叶子再合并一次

---

## 3. 从实测得到的收敛原则

这轮实测里暴露出 5 类典型冲突：

### 3.1 “宣传误导”和“承诺未兑现”过近

例如：

- 承诺免费赠送监控但套餐中根本没有该业务
- 承诺取消业务但实际未取消

这类案例里，AI 很容易在：

- `宣传错误/误导`
- `赠品/权益未兑现`
- `承诺未兑现`

之间摇摆。

结论：

- 这几类应该收敛合并，避免人为把“承诺”和“误导”拆得过细

### 3.2 “退订争议”和“退订失败”过近

AI 能稳定判断到“退订类”，但不稳定区分：

- 是一般争议
- 还是已经构成失败

结论：

- 这类应该优先合并成更宽的叶子

### 3.3 “风险关停”和“模型关停”过近

在高风险双停类案例里，AI 很自然会落到：

- `模型关停不认可`

而人工有时会判：

- `风险关停不认可`

结论：

- 这两个叶子对 agent 来说应合并

### 3.4 “预约未上门”是“履约不及时”的具体情形

AI 对这类样本更倾向收敛到：

- `履约不及时/未履约`

而不是更具体的：

- `预约未上门`

结论：

- `预约未上门` 不值得保留为独立叶子

### 3.5 “要求联系客户经理”需要更强的流程优先级

在商机单里，如果同时出现业务内容和“要求客户经理联系”，AI 有可能被业务内容带偏。

结论：

- `SERVICE_PROCESS` 要继续保留
- 同时把叶子定义写得更明确：
  - `客户经理协调/业务核实`

---

## 4. 最终设计原则

最终版按下面原则收敛：

1. 一级域保持 `9` 个，不再改
2. 二级域保持 `23` 个，不再改
3. 叶子域继续压缩，优先合并边界近、容易混淆的类
4. 最终叶子数量控制在 `60-70` 左右
5. 对 AI 来说，叶子命名优先选择“宽而稳”，不追求特别细

第二轮验证后，需要额外固定两条判定优先级：

6. 如果工单核心争议是“业务本该取消但未取消”，优先落到 `SUBSCRIBE_CANCEL / CANCEL_AND_UNSUBSCRIBE`
7. 如果工单核心争议是“流量用尽后是否断网/限速/继续收费”，优先落到 `RULE_POLICY / USAGE_AND_LIMIT_RULE`

第三轮验证后，再补 4 条判定优先级：

8. 如果工单核心是“套餐变更、销户、退订本身想做但被系统或在途流程挡住”，优先落到 `SUBSCRIBE_CANCEL`，不要因为“办理不畅”字样直接归到 `MARKETING_SALES`
9. 如果工单核心是“APP 上无法领取权益、无法提交、线上办理失败”，优先落到 `PRODUCT_PLATFORM / APP_AND_ACCOUNT`；`QUERY_AND_DISPLAY` 只保留给查询、展示、页面信息呈现异常
10. 如果工单是“修障后短时间再次故障、仍无法连接、仍不稳定”，优先按用户感知结果归 `NETWORK_QUALITY`；只有明确指向施工、安装、上门质量问题时才归 `INSTALL_DELIVERY / INSTALL_STANDARD_AND_RESULT`
11. 如果同时出现“套外收费”与“达量降速/规则承诺”冲突：
    - 争议点在规则承诺、达量降速口径、是否该继续收费时，优先 `RULE_POLICY / USAGE_AND_LIMIT_RULE`
    - 争议点只在已经产生的费用金额时，优先 `FEE_BILLING / PACKAGE_AND_USAGE_FEE`
12. 如果工单最终诉求是“开具发票、补开发票、发票金额/获取异常”，即使处理中出现客户经理、营业厅、企微客服等角色，也优先 `FEE_BILLING / ACCOUNT_AND_PAYMENT / 发票问题`
13. 如果工单表述为“业务是办过的，但办理时未告知合约期/规则/限制”，优先 `MARKETING_SALES / EXPLAIN_AND_COMMITMENT / 宣传/解释不清或误导`；只有明确否认自己办理、否认订购关系本身时，才归 `SUBSCRIBE_CANCEL / ORDER_AND_DENY / 用户否认订购`
14. 如果工单是“营销中承诺给某个具体权益、礼包、赠品，但实际没有兑现”，优先 `MARKETING_SALES / EXPLAIN_AND_COMMITMENT / 赠品/权益未兑现`
15. 如果工单是“营销口径、活动使用条件、活动资格、生效规则本身有争议”，优先 `RULE_POLICY / ACTIVITY_AND_EFFECTIVE_RULE / 营销活动规则争议`；不要因为最终表现为“权益没到账/不能用”就默认归到 `赠品/权益未兑现`

---

## 5. 最终一级域

1. `FEE_BILLING`
2. `SUBSCRIBE_CANCEL`
3. `OPEN_RECOVERY_CONTROL`
4. `MARKETING_SALES`
5. `RULE_POLICY`
6. `PRODUCT_PLATFORM`
7. `NETWORK_QUALITY`
8. `INSTALL_DELIVERY`
9. `SERVICE_PROCESS`

---

## 6. 最终二级域

### 6.1 `FEE_BILLING`

- `PACKAGE_AND_USAGE_FEE`
- `ACCOUNT_AND_PAYMENT`
- `REFUND_PENALTY_RIGHTS`

### 6.2 `SUBSCRIBE_CANCEL`

- `ORDER_AND_DENY`
- `CANCEL_AND_UNSUBSCRIBE`
- `PLAN_CHANGE_AND_ACCOUNT_CLOSE`

### 6.3 `OPEN_RECOVERY_CONTROL`

- `OPEN_AND_ACTIVATION`
- `SHUTDOWN_AND_CONTROL`
- `RECOVERY_AND_UNBLOCK`

### 6.4 `MARKETING_SALES`

- `EXPLAIN_AND_COMMITMENT`
- `SALES_PROCESS_AND_ATTITUDE`

说明：

- 这里把原来的：
  - `EXPLAIN_AND_MISLEADING`
  - `PROMISE_AND_DELIVERY`
  合并成一个更稳的二级域：`EXPLAIN_AND_COMMITMENT`

### 6.5 `RULE_POLICY`

- `ACTIVITY_AND_EFFECTIVE_RULE`
- `USAGE_AND_LIMIT_RULE`
- `QUALIFICATION_AND_PROCESS_RULE`

### 6.6 `PRODUCT_PLATFORM`

- `BASIC_FUNCTION`
- `APP_AND_ACCOUNT`
- `QUERY_AND_DISPLAY`

### 6.7 `NETWORK_QUALITY`

- `NETWORK_QUALITY`

### 6.8 `INSTALL_DELIVERY`

- `INSTALL_TIMELINESS`
- `INSTALL_STANDARD_AND_RESULT`

### 6.9 `SERVICE_PROCESS`

- `COMPLAINT_HANDLING`
- `WORK_ORDER_FLOW`
- `SPECIAL_REPORT_AND_MANAGER`

---

## 7. 最终叶子分类清单

### 7.1 `FEE_BILLING / PACKAGE_AND_USAGE_FEE`

- 套餐收费争议
- 套外使用费用争议
- 增值业务收费争议
- 异常扣费/不明收费
- 宽带/电视收费争议

### 7.2 `FEE_BILLING / ACCOUNT_AND_PAYMENT`

- 账单金额/展示异常
- 充值缴费异常
- 发票问题
- 展示类账单问题

### 7.3 `FEE_BILLING / REFUND_PENALTY_RIGHTS`

- 返费/赠费/退款未到账
- 翼支付权益/费用争议
- 违约金/滞纳金争议

### 7.4 `SUBSCRIBE_CANCEL / ORDER_AND_DENY`

- 用户否认订购
- 订购办理争议
- 自动续订争议

### 7.5 `SUBSCRIBE_CANCEL / CANCEL_AND_UNSUBSCRIBE`

- 业务退订/取消争议
- 业务退订/取消失败
- 退订后仍收费

### 7.6 `SUBSCRIBE_CANCEL / PLAN_CHANGE_AND_ACCOUNT_CLOSE`

- 套餐变更争议
- 拆机销户争议
- 销户后仍计费/销户规则争议

### 7.7 `OPEN_RECOVERY_CONTROL / OPEN_AND_ACTIVATION`

- 业务开通失败
- 号卡开通失败
- 宽带开通失败
- 激活/实名认证异常

### 7.8 `OPEN_RECOVERY_CONTROL / SHUTDOWN_AND_CONTROL`

- 欠费停机不认可
- 风险/模型关停不认可
- 屏蔽/解限问题

### 7.9 `OPEN_RECOVERY_CONTROL / RECOVERY_AND_UNBLOCK`

- 复机/恢复失败或不及时

### 7.10 `MARKETING_SALES / EXPLAIN_AND_COMMITMENT`

- 宣传/解释不清或误导
- 承诺未兑现
- 赠品/权益未兑现

### 7.11 `MARKETING_SALES / SALES_PROCESS_AND_ATTITUDE`

- 业务办理差错/漏受理
- 业务办理不畅
- 服务态度问题

### 7.12 `RULE_POLICY / ACTIVITY_AND_EFFECTIVE_RULE`

- 营销活动规则争议
- 生效/失效规则争议

### 7.13 `RULE_POLICY / USAGE_AND_LIMIT_RULE`

- 达量降速/限速规则争议
- 权益/流量使用范围争议
- 合约限制争议

### 7.14 `RULE_POLICY / QUALIFICATION_AND_PROCESS_RULE`

- 资格条件/实名规则争议
- 代办/流程规则争议

### 7.15 `PRODUCT_PLATFORM / BASIC_FUNCTION`

- 语音功能异常
- 短信功能异常
- 流量功能异常
- 产品功能缺失/不稳定

### 7.16 `PRODUCT_PLATFORM / APP_AND_ACCOUNT`

- APP/网厅报错或线上办理失败
- 账号登录/身份校验异常

### 7.17 `PRODUCT_PLATFORM / QUERY_AND_DISPLAY`

- 订单/套餐/信息查询展示异常
- 网站/平台/客户端软件问题

### 7.18 `NETWORK_QUALITY / NETWORK_QUALITY`

- 无信号/信号弱
- 移动上网慢
- 宽带网速慢
- 宽带掉线/网络不稳定
- 通话质量异常
- 漫游通信异常

### 7.19 `INSTALL_DELIVERY / INSTALL_TIMELINESS`

- 履约不及时/未履约
- 催装移机

### 7.20 `INSTALL_DELIVERY / INSTALL_STANDARD_AND_RESULT`

- 上门服务不规范
- 安装施工质量问题
- 施工损坏问题
- 交付结果不符/实测速率不达标

### 7.21 `SERVICE_PROCESS / COMPLAINT_HANDLING`

- 久拖未决/重复投诉处理不满意
- 处理结果不认可

### 7.22 `SERVICE_PROCESS / WORK_ORDER_FLOW`

- 工单流转/转派错误/多部门扯皮

### 7.23 `SERVICE_PROCESS / SPECIAL_REPORT_AND_MANAGER`

- 客户经理协调/业务核实
- 查询申请代理资料
- 举报骚扰/诈骗电话
- 举报不良信息/第三方平台标记错误
- 建议表扬

---

## 8. 总量评估

这版最终体系大致为：

- 一级域：`9`
- 二级域：`23`
- 叶子分类：`67`

这比上一版候选清单进一步收敛，更符合 agent 的实际稳定选择能力。

---

## 9. 推荐实现方式

对 `complaint_taxonomy_converger`，建议直接按这版最终体系实现：

1. `primary_category` 只允许在这 `67` 个叶子分类里选 1 个
2. prompt 中直接给出：
   - 一级域
   - 二级域
   - 叶子名称
3. 返回结构固定为：
   - `level1_code`
   - `level2_code`
   - `leaf_name`
   - `reason`

如果后续还要继续优化，不建议再先扩分类数量，而应该优先：

- 增加样本验证
- 调 prompt
- 补典型样例

---

## 10. 当前结论

当前这版 `V2 final` 可以视为一版完整、高度收敛、可直接进入 agent 实现的分类体系。

和原始 `173` 个叶子相比，它的优势是：

- 更少
- 更稳
- 更贴近原始工单高频问题
- 更适合 AI 选择
- 更容易挂接后续处理建议
