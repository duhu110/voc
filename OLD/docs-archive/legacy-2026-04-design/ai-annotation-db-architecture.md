# AI 标注与数据库闭环设计

## 文档目的

沉淀基于历史工单进行 AI 分类、打标签、规则挖掘、命中率评估和后续处理编排的数据库设计思路。

当前输入前提：

- 历史工单源表为 `raw_complaint_tickets`
- 工单主键为 `ticket_id`
- 分类表和标签表已创建并完成初始化

## 目标链路

目标闭环可以概括为：

历史工单 -> AI 分类/打标签 -> 与现有字段和业务经验对比 -> 评估命中率/冲突率 -> 反向沉淀关键词规则和推荐关系 -> 新投诉更快更准分类 -> 根据分类和标签触发处理建议

这个链路的核心不是一次性把所有规则写死，而是让：

- 主数据可维护
- AI 结果可沉淀
- 规则可迭代
- 推荐关系可学习
- 处置策略可编排

## 关键设计结论

### 1. 分类-标签推荐关系不要写死在代码里

不建议：

- 写死在代码
- 完全依赖 AI 即时判断

建议：

- 放在数据库里
- 区分人工基线关系和统计学习关系

推荐采用两层关系：

- `baseline`：人工维护的基线关系
- `stat`：后续从历史结果中学习出的统计关系

当前阶段先只做 `baseline`。

### 2. 原始字段映射规则表暂时不做

当前阶段不需要先建设 `old field -> new category/tag` 的规则系统。

原因：

- 当前重点是验证新分类体系是否合理
- 当前重点是让 AI 直接读取完整工单信息
- 当前重点是沉淀关键词和命中明细

因此当前策略是：

- 保留老字段
- 不建立 `complaint_field_mapping_rule`
- 等后续发现某些老字段足够稳定，再考虑补建

### 3. 单条级评估字段先只保留 `evaluation_status`

当前不做重型评估体系，只做轻量状态标记。

建议在以下两张结果表中保留：

- `complaint_ticket_category_result`
- `complaint_ticket_tag_result`

字段：

- `evaluation_status varchar(50) null`

建议取值：

- `pending`
- `correct`
- `wrong`
- `partial`

## 推荐数据库分层

### 第 1 层：基础主数据层

存“定义是什么”。

当前包含：

- `complaint_category`
- `complaint_tag_group`
- `complaint_tag`
- `complaint_category_tag_relation`

### 第 2 层：规则层

存“为什么会命中”。

当前建议保留：

- `complaint_category_rule`
- `complaint_tag_rule`

后续可补但当前不优先：

- 原始字段映射规则表
- 处理建议规则表

### 第 3 层：AI 标注结果层

存“AI 怎么判的”。

当前建议保留：

- `complaint_ticket_category_result`
- `complaint_ticket_tag_result`
- `complaint_ticket_keyword_result`
- `complaint_ticket_match_detail`

### 第 4 层：校验评估层

存“准不准、能不能优化”。

当前先轻量处理：

- 结果表保留 `evaluation_status`

暂不单独建设复杂人工评估表。

### 第 5 层：关系学习层

存“从历史中学到了什么”。

当前概念上保留，暂不优先落表：

- 分类-标签统计关系
- 分类-关键词统计
- 标签-关键词统计
- 原字段值到分类/标签的映射统计

### 第 6 层：处置编排层

存“后续怎么处理”。

当前概念上保留，暂不优先落表：

- 分类处理建议
- 分类 + 标签组合处理规则
- 风险升级规则
- 派单建议

## 当前推荐保留的最小闭环表

### 主数据

- `complaint_category`
- `complaint_tag_group`
- `complaint_tag`
- `complaint_category_tag_relation`

### 规则

- `complaint_category_rule`
- `complaint_tag_rule`

### 结果

- `complaint_ticket_category_result`
- `complaint_ticket_tag_result`
- `complaint_ticket_keyword_result`
- `complaint_ticket_match_detail`

## 当前明确不做或延后

- `complaint_field_mapping_rule`
- 各种复杂统计表
- 复杂人工校验表
- 过早引入自动学习关系落表

## 分类标签基线关系表定位

`complaint_category_tag_relation` 的作用不是最终命中结果，而是：

- 某个分类通常可能对应哪些标签
- AI 打标签时作为提示与校验
- 后续可统计“推荐命中率”
- 后续可被真实结果反向修正

建议精简字段思路：

- `category_id`
- `tag_id`
- `relation_type`
- `recommended_weight`
- `is_enabled`
- `notes`
- `created_at`
- `updated_at`

唯一性建议：

- `(category_id, tag_id, relation_type)`

## 结果表定位

### 分类结果表

用途：

- 存储单次或多次 AI/规则/人工分类结果
- 支持多版本模型重跑
- 支持最终结果与候选结果并存

最重要字段：

- `ticket_id`
- `category_id`
- `result_source`
- `matched_by`
- `ranking_no`
- `is_final`
- `evaluation_status`

### 标签结果表

用途：

- 存储单条工单的多标签结果

最重要字段：

- `ticket_id`
- `tag_id`
- `result_source`
- `matched_by`
- `ranking_no`
- `is_final`
- `evaluation_status`

## 关键词和命中明细的作用

### 关键词结果表

用途：

- 从原始投诉文本中沉淀高频关键词
- 为后续规则表建设提供候选词

### 命中明细表

用途：

- 记录某条工单为什么命中某分类或标签
- 支撑后续解释、审计、规则优化

它应该能回答：

- 为什么这条工单被归到该分类
- 是 AI 判的、规则命中的，还是其他方式得出的
- 命中的关键词或依据是什么

## 命中率评估的口径

“命中率”不要只理解成一个单指标，至少要拆成：

- 分类命中率
- 标签命中率
- 关键词规则命中率
- 推荐关系命中率

但当前阶段先不做复杂统计表，先依赖结果表中的 `evaluation_status` 做最小闭环。

## 当前建议流程

### 阶段 1：历史工单批量跑 AI

输入：

- `raw_complaint_tickets.ticket_id`
- 工单全部字段
- 用户原始投诉文本

产出：

- 分类结果
- 标签结果
- 关键词结果
- 命中明细

### 阶段 2：观察结果质量

重点观察：

- 哪些分类稳定
- 哪些标签不稳定
- 哪些关键词高频但没有规则
- 哪些分类和标签长期高相关

### 阶段 3：反向沉淀规则

把历史结果反向沉淀到：

- `complaint_category_rule`
- `complaint_tag_rule`
- `complaint_category_tag_relation`

### 阶段 4：新工单走混合策略

未来新投诉进入后：

1. AI 读取完整文本和上下文
2. 先判主分类
3. 再抽多标签
4. 再参考基线关系校验或补充标签
5. 最后根据分类 + 标签触发处理建议

## 当前取舍结论

当前项目应遵循以下取舍：

- 主数据静态管理
- 规则表动态迭代
- AI 结果单独沉淀
- 推荐关系先做人控基线
- 统计学习关系后补
- 原始字段映射规则暂时不做
- 单条评估先只保留 `evaluation_status`
