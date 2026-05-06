# 分类体系重设计草案 V2

## 1. 目的

这份文档回答的是：

如果允许重新设计 `primary_category` 的分类体系，新的体系应该长什么样。

这里的目标不是“保持四级结构”，而是让分类体系更适合：

- `complaint_taxonomy_converger` 稳定选择
- 与原始工单高频问题对齐
- 与后续处理建议映射
- 保持足够的业务区分度，同时控制分类数量

---

## 2. 重设计目标

新的分类体系建议遵守下面 5 个原则：

### 2.1 让 AI 更容易选

- 分类边界要清楚
- 一个分类只表达一个核心问题
- 不要同时混入诉求、处理结果、责任判断

### 2.2 最终可选分类数量明显收敛

当前叶子分类共有 `173` 个，对 agent 来说偏多。

V2 建议目标：

- 最终叶子分类控制在 `40-70` 个

### 2.3 不再执着于“四级”

V2 更建议按：

- 一级：问题大域
- 二级：业务场景
- 三级：最终可选分类

也就是一套更适合运行的**三级叶子体系**。

### 2.4 保留可解释性

每个最终分类都应该能回答：

- 这是什么问题
- 为什么归到这里
- 后续大致应该怎么处理

### 2.5 老体系与新体系并行

如果未来真的落库，建议：

- 保留现有 `complaint_category`
- 新增 `complaint_category_v2`
- 新增 `complaint_category_mapping`

而不是直接改老表。

---

## 3. 为什么值得重设计

从当前数据库看：

- 现有树结构本身没有明显假层级
- 但叶子节点太多，已经达到 `173` 个
- 高频问题高度集中在少数主题：
  - 套餐收费
  - 解释宣传不清/误导
  - 拆机销户
  - 套外费用
  - 业务退订
  - 关停不认可
  - 用户否认订购
  - 宽带预约拆机处理不及时
  - 办理差错/漏受理
  - 翼支付权益金争议
  - 营销活动规则争议
  - 基础功能异常
  - 业务生效/失效规则争议

说明：

- 现有分类树对人工管理友好
- 但对 agent 来说过细
- 高频问题适合合并为更稳定的运行时分类

---

## 4. V2 一级结构建议

建议把 V2 一级分类收敛成 9 个大域：

1. `FEE_BILLING`
   - 收费、账单、缴费与退款争议
2. `SUBSCRIBE_CANCEL`
   - 订购、退订、变更、销户类问题
3. `OPEN_RECOVERY_CONTROL`
   - 开通、停复机、限制与恢复类问题
4. `MARKETING_SALES`
   - 宣传、承诺、销售过程与服务态度问题
5. `RULE_POLICY`
   - 规则、资格、活动、生效使用政策类问题
6. `PRODUCT_PLATFORM`
   - 产品功能、APP/网厅、账号、展示查询类问题
7. `NETWORK_QUALITY`
   - 信号、网速、通话、漫游、宽带网络质量问题
8. `INSTALL_DELIVERY`
   - 装维、施工、交付、履约、催装移机类问题
9. `SERVICE_PROCESS`
   - 投诉处理、工单流转、客户经理协调、举报与特殊服务流程问题

这 9 个大域比现有 10 个一级域更适合 agent。

主要合并关系：

- `资费与收费争议` + `账单、缴费与发票` 合并到 `FEE_BILLING`
- `服务投诉与其他` 中的流程类内容合并到 `SERVICE_PROCESS`

第二轮判断说明：

- `SERVICE_PROCESS` 建议保留
  - 原始工单里与客户经理协调、查询申请代理资料、投诉处理不满意、工单流转、举报相关的问题量并不小
  - 这类问题有独立的处理路径，不适合硬塞进营销、规则或其他兜底类
- `NETWORK_DELIVERY` 建议拆开
  - `网络质量类` 和 `装维服务类` 在原始工单里本身就是两套不同主题
  - 前者偏网络表现，后者偏履约交付
  - 对后续处理建议来说，也应该分开

---

## 5. V2 二级结构建议

### 5.1 `FEE_BILLING`

- `PACKAGE_AND_USAGE_FEE`
- `ACCOUNT_AND_PAYMENT`
- `REFUND_PENALTY_RIGHTS`

判断说明：

- 当前数据库高频值里：
  - `翼支付权益金争议`
  - `违约金/滞纳金争议`
  - `返费/赠费/退款/提现未到账`
  - `充值缴费未到帐`
  - `账单、发票的寄送/推送/获取问题`
  已经比较稳定地落在这 3 个二级桶里
- 所以 `FEE_BILLING` 当前不建议再拆得更细
- 第一版二级结构保持这 3 类即可

### 5.2 `SUBSCRIBE_CANCEL`

- `ORDER_AND_DENY`
- `CANCEL_AND_UNSUBSCRIBE`
- `PLAN_CHANGE_AND_ACCOUNT_CLOSE`

判断说明：

- 当前数据库高频值里：
  - `用户否认订购`
  - `业务退订`
  - `拆机销户`
  - `套餐变更`
  已经能稳定对应这 3 个二级桶
- 这里建议把“订购/退订/变更/销户”放在一个一级域里处理
- 因为它们本质上都属于客户对业务关系的建立、变更、终止
- 不建议把“套餐变更”单独拉成一级域

### 5.3 `OPEN_RECOVERY_CONTROL`

- `OPEN_AND_ACTIVATION`
- `SHUTDOWN_AND_CONTROL`
- `RECOVERY_AND_UNBLOCK`

判断说明：

- 这个一级域和 `SUBSCRIBE_CANCEL` 的边界要明确：
  - `SUBSCRIBE_CANCEL`: 客户主动要求订购、退订、变更、销户
  - `OPEN_RECOVERY_CONTROL`: 服务状态异常，例如开通失败、停机争议、复机恢复、解限
- 当前数据库高频值里：
  - `欠费停机`
  - `要求屏蔽/解限`
  - `复机不及时`
  都更适合归到这里
- 所以这一级域有保留必要

### 5.4 `MARKETING_SALES`

- `EXPLAIN_AND_MISLEADING`
- `PROMISE_AND_DELIVERY`
- `SALES_PROCESS_AND_ATTITUDE`

判断说明：

- 当前数据库高频值里：
  - `解释、说明、宣传不清晰/错误/误导`
  - `业务办理差错/漏受理`
  - `服务态度不好`
  已经比较清晰地对应这 3 个二级桶
- 第一版这里也不建议再细拆

### 5.5 `RULE_POLICY`

- `ACTIVITY_AND_EFFECTIVE_RULE`
- `USAGE_AND_LIMIT_RULE`
- `QUALIFICATION_AND_PROCESS_RULE`

判断说明：

- 当前数据库高频值里：
  - `营销活动规则争议`
  - `业务生效/失效规则争议`
  - `达量降速规则争议`
  - `实名制/一证五号办理规则`
  - `停复机规则不认可`
  已经比较稳定地落在这 3 个二级桶里
- 这里的核心不是客户情绪或办理动作，而是“规则是否合理、是否适用、是否讲清楚”
- 第一版这 3 个二级桶已经够用

### 5.6 `PRODUCT_PLATFORM`

- `BASIC_FUNCTION`
- `APP_AND_ACCOUNT`
- `QUERY_AND_DISPLAY`

判断说明：

- 当前数据库高频值里：
  - `基础功能异常`
  - `网站/平台/客户端软件问题`
  - `产品功能缺失/不稳定/不便捷`
  - `第三方平台标记错误`
  比较适合归到这一域
- 这里要和 `SERVICE_PROCESS` 拉开边界：
  - 平台、账号、展示、功能本身异常，归 `PRODUCT_PLATFORM`
  - 查询代理资料、联系客户经理、举报协调，归 `SERVICE_PROCESS`
- 第一版建议维持这 3 个二级桶，不再细拆
  - `BASIC_FUNCTION`
  - `APP_AND_ACCOUNT`
  - `QUERY_AND_DISPLAY`

### 5.7 `NETWORK_QUALITY`

- `NETWORK_QUALITY`

判断说明：

- 当前数据库高频值里：
  - `漫游使用异常省际漫游质量`
  - `网速慢宽带`
  - `网速慢手机`
  - `手机无信号`
  - `信号弱/不稳定`
  - `有信号上网/通话不正常`
  已经说明这类问题可以作为独立一级域
- 这一域当前先不拆更多二级桶
- 原因是第一版先保证稳定识别“网络表现问题”，不急着进一步拆成信号、网速、通话、漫游四类
- 叶子层再承接这些细分即可

### 5.8 `INSTALL_DELIVERY`

- `INSTALL_TIMELINESS`
- `INSTALL_STANDARD_AND_RESULT`

判断说明：

- 当前数据库高频值里：
  - `宽带预约拆机处理不及时`
  - `履约不及时/超时履约/未履约`
  - `装维服务或交付不规范`
  已经比较明确地分成两类：
  - 时效履约问题
  - 上门/施工/交付标准问题
- 所以第一版建议只保留这 2 个二级桶，不再继续展开
- 它与 `NETWORK_QUALITY` 的边界是：
  - `NETWORK_QUALITY`: 网络最终表现不好
  - `INSTALL_DELIVERY`: 装维履约或交付过程不好

### 5.9 `SERVICE_PROCESS`

- `COMPLAINT_HANDLING`
- `WORK_ORDER_FLOW`
- `SPECIAL_REPORT_AND_MANAGER`

判断说明：

- 当前数据库高频值里：
  - `要求联系客户经理业务核实`
  - `查询申请代理资料`
  - `举报骚扰电话（本网省内）`
  - `要求联系客户经理个人业务咨询/受理`
  - `举报不良信息（本网）`
  - `用户建议及表扬`
  说明这不是零散兜底类，而是一组独立问题
- 这里建议分成 3 个二级桶：
  - `COMPLAINT_HANDLING`: 投诉处理不满意、久拖未决、重复投诉处理不满意
  - `WORK_ORDER_FLOW`: 工单超时、流转、转派、多部门扯皮
  - `SPECIAL_REPORT_AND_MANAGER`: 客户经理协调、查询代理资料、举报与建议表扬
- 第一版建议保留这一域，不并回其他一级类

---

## 6. V2 叶子分类候选清单

下面是一版第一轮候选清单，目标控制在 `50-60` 个左右。

### 6.1 `FEE_BILLING`

#### `PACKAGE_AND_USAGE_FEE`

- 套餐收费争议
- 套外流量费用争议
- 套外通话费用争议
- 漫游费用争议
- 增值业务收费争议
- 不明收费争议
- 宽带/电视收费争议

#### `ACCOUNT_AND_PAYMENT`

- 账单金额异常
- 余额/账单展示异常
- 充值缴费未到账
- 客户错充值缴费
- 发票问题

#### `REFUND_PENALTY_RIGHTS`

- 返费/赠费/退款未到账
- 翼支付权益金争议
- 违约金争议
- 滞纳金/历史欠费争议

### 6.2 `SUBSCRIBE_CANCEL`

#### `ORDER_AND_DENY`

- 用户否认订购
- 未明确同意订购
- 业务办理/订购争议
- 自动续订争议

#### `CANCEL_AND_UNSUBSCRIBE`

- 业务退订失败
- 退订后仍收费
- 业务退订争议

#### `PLAN_CHANGE_AND_ACCOUNT_CLOSE`

- 套餐变更争议
- 拆机销户
- 销户后仍计费
- 销户规则争议

### 6.3 `OPEN_RECOVERY_CONTROL`

#### `OPEN_AND_ACTIVATION`

- 业务开通失败
- 号卡开通失败
- 宽带开通失败
- 激活异常
- 实名认证异常

#### `SHUTDOWN_AND_CONTROL`

- 欠费停机不认可
- 风险关停不认可
- 模型关停不认可
- 屏蔽/解限问题

#### `RECOVERY_AND_UNBLOCK`

- 复机失败
- 复机不及时
- 服务恢复失败

### 6.4 `MARKETING_SALES`

#### `EXPLAIN_AND_MISLEADING`

- 解释说明不清
- 宣传错误/误导
- 资费或规则解释不清

#### `PROMISE_AND_DELIVERY`

- 赠品/权益未兑现
- 返费承诺未兑现
- 速率能力未兑现

#### `SALES_PROCESS_AND_ATTITUDE`

- 业务办理差错
- 漏受理
- 业务办理不畅
- 客服服务态度问题
- 客户经理服务态度问题
- 营业厅服务态度问题

### 6.5 `RULE_POLICY`

#### `ACTIVITY_AND_EFFECTIVE_RULE`

- 营销活动规则争议
- 套餐生效时间争议
- 业务失效规则争议

#### `USAGE_AND_LIMIT_RULE`

- 达量降速/限速规则争议
- 权益适用范围争议
- 流量使用范围争议
- 合约限制争议

#### `QUALIFICATION_AND_PROCESS_RULE`

- 资格条件争议
- 实名制/一证五号规则争议
- 代办规则争议
- 办理流程规则争议

### 6.6 `PRODUCT_PLATFORM`

#### `BASIC_FUNCTION`

- 语音功能异常
- 短信功能异常
- 流量功能异常
- 产品基础功能缺失/不稳定

#### `APP_AND_ACCOUNT`

- APP/网厅报错
- 线上办理失败
- 账号登录失败
- 身份校验异常

#### `QUERY_AND_DISPLAY`

- 订单状态展示异常
- 套餐信息展示异常
- 查询展示异常
- 网站/平台/客户端软件问题

### 6.7 `NETWORK_QUALITY`

- 无信号
- 信号弱/不稳定
- 移动上网慢
- 宽带网速慢
- 宽带频繁掉线
- 通话掉话/接通困难/杂音回声
- 漫游通信异常

### 6.8 `INSTALL_DELIVERY`

#### `INSTALL_TIMELINESS`

- 宽带预约拆机处理不及时
- 履约不及时/超时履约/未履约
- 预约未上门
- 超时未完成
- 催装移机

#### `INSTALL_STANDARD_AND_RESULT`

- 上门服务不规范
- 安装施工质量问题
- 施工损坏问题
- 交付结果不符
- 实测速率不达标

### 6.9 `SERVICE_PROCESS`

#### `COMPLAINT_HANDLING`

- 久拖未决
- 处理结果不认可
- 重复投诉处理不满意

#### `WORK_ORDER_FLOW`

- 工单超时未处理
- 转派错误
- 多部门扯皮
- 工单流转问题

#### `SPECIAL_REPORT_AND_MANAGER`

- 要求联系客户经理
- 查询申请代理资料
- 举报骚扰电话
- 举报不良信息
- 第三方平台标记错误

---

## 7. 当前收敛总结

截至目前，这版 V2 草案已经完成到下面这个粒度：

### 7.1 一级域

共 `9` 个：

1. `FEE_BILLING`
2. `SUBSCRIBE_CANCEL`
3. `OPEN_RECOVERY_CONTROL`
4. `MARKETING_SALES`
5. `RULE_POLICY`
6. `PRODUCT_PLATFORM`
7. `NETWORK_QUALITY`
8. `INSTALL_DELIVERY`
9. `SERVICE_PROCESS`

### 7.2 二级域

共 `24` 个：

- `FEE_BILLING`
  - `PACKAGE_AND_USAGE_FEE`
  - `ACCOUNT_AND_PAYMENT`
  - `REFUND_PENALTY_RIGHTS`
- `SUBSCRIBE_CANCEL`
  - `ORDER_AND_DENY`
  - `CANCEL_AND_UNSUBSCRIBE`
  - `PLAN_CHANGE_AND_ACCOUNT_CLOSE`
- `OPEN_RECOVERY_CONTROL`
  - `OPEN_AND_ACTIVATION`
  - `SHUTDOWN_AND_CONTROL`
  - `RECOVERY_AND_UNBLOCK`
- `MARKETING_SALES`
  - `EXPLAIN_AND_MISLEADING`
  - `PROMISE_AND_DELIVERY`
  - `SALES_PROCESS_AND_ATTITUDE`
- `RULE_POLICY`
  - `ACTIVITY_AND_EFFECTIVE_RULE`
  - `USAGE_AND_LIMIT_RULE`
  - `QUALIFICATION_AND_PROCESS_RULE`
- `PRODUCT_PLATFORM`
  - `BASIC_FUNCTION`
  - `APP_AND_ACCOUNT`
  - `QUERY_AND_DISPLAY`
- `NETWORK_QUALITY`
  - `NETWORK_QUALITY`
- `INSTALL_DELIVERY`
  - `INSTALL_TIMELINESS`
  - `INSTALL_STANDARD_AND_RESULT`
- `SERVICE_PROCESS`
  - `COMPLAINT_HANDLING`
  - `WORK_ORDER_FLOW`
  - `SPECIAL_REPORT_AND_MANAGER`

### 7.3 叶子分类

当前候选叶子约 `60` 个左右。

这一版 V2 草案的特点是：

- 仍然保留业务语义
- 不再要求四级
- 把当前 `173` 个叶子压缩到约 `60` 个左右的可选叶子
- 高度贴近原始工单高频主题

适合 `converger` 的原因：

- 选择范围明显更小
- 分类边界更偏业务语义，而不是管理语义
- 更容易和后续处理建议做映射

### 7.4 已经明确的边界

- `FEE_BILLING` 保留收费、账单、缴费、退款的合并一级域
- `SUBSCRIBE_CANCEL` 和 `OPEN_RECOVERY_CONTROL` 已经分清
  - 前者是业务关系变更
  - 后者是服务状态异常
- `SERVICE_PROCESS` 保留为独立一级域
- 原来的 `NETWORK_DELIVERY` 已拆成：
  - `NETWORK_QUALITY`
  - `INSTALL_DELIVERY`

---

## 8. 下一步建议

如果继续推进 V2，建议按这个顺序做：

1. 以这版 `9` 个一级域、`24` 个二级域为基础，逐组确认叶子分类清单
2. 为每个叶子分类补“定义、边界、典型样例”
3. 形成 `old_category -> new_category` 映射草案
4. 最后形成：
   - `complaint_category_v2`
   - `old_category -> new_category` 映射表

当前最适合的下一步不是再讨论一级域，而是直接开始做映射：

- 从现有高频旧分类出发
- 一条条映射到这版 V2 叶子分类
- 找出仍然模糊或冲突的点再回头调结构
