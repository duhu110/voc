# 项目下一步任务


## 背景结论

相关设计文档：

- [用户投诉分类与标签设计](/Users/duhu/code/voc/docs/complaint-taxonomy-design.md)
- [AI 标注与数据库闭环设计](/Users/duhu/code/voc/docs/ai-annotation-db-architecture.md)

- 投诉体系不要把所有信息都塞进一棵分类树。
- 主结构应是“主分类树 + 辅助标签”。
- 主分类树回答“客户到底在投诉什么”。
- 其他维度通过标签承载，例如：
  - 工单类型
  - 涉及产品
  - 责任条线
  - 根因标签
  - 处理结果
  - 风险标签

## 当前目标架构

### 1. 基础主数据层

- `complaint_category`
- `complaint_tag_group`
- `complaint_tag`
- `complaint_category_tag_relation`

### 2. 规则层

- `complaint_category_rule`
- `complaint_tag_rule`
- 后续可补：
  - 原始字段映射规则
  - 处理建议规则

### 3. AI 结果层

- `complaint_ticket_category_result`
- `complaint_ticket_tag_result`
- `complaint_ticket_keyword_result`
- `complaint_ticket_match_detail`

### 4. 评估与统计层

- 先保留轻量评估字段：
  - `evaluation_status`
- 后续再补统计表：
  - 分类-标签统计关系
  - 分类-关键词统计
  - 标签-关键词统计
  - 原始字段值到分类/标签的映射统计

### 5. 处置编排层

- 分类处理建议
- 分类 + 标签组合处理规则
- 风险升级规则
- 派单建议

## 已完成

- 分类表和标签表已创建并完成初始化
- 项目专属数据库技能已创建：
  - `.codex/skills/project-db-executor`
- 数据库结构巡检与修复已完成：
  - 结果表补齐 `updated_at`
  - 已确认结果表存在 `evaluation_status`
  - 补齐关键外键索引
  - 补齐结果表常用索引
  - 补齐分类结果表唯一约束
  - 补齐规则表防重复唯一约束

## 待推进

### 第一阶段：完成主数据与基线关系

- [x] 确认分类树采用“主分类树 + 标签体系”
- [x] 完成分类、标签主数据初始化
- [ ] 初始化 `complaint_category_tag_relation`
- [ ] 先采用“人工基线关系”，不要直接做动态学习关系

### 第二阶段：完成规则层

- [ ] 为分类补关键词/短语/规则配置
- [ ] 为标签补关键词/短语/规则配置
- [ ] 明确规则命中字段、匹配方式、否定规则、优先级
- [x] 明确当前阶段不建设“原始字段映射规则表”
- [ ] 决定是否补“处理建议规则表”

### 第三阶段：批量跑历史工单

- [ ] 从 `raw_complaint_tickets` 读取历史工单
- [ ] 让 AI 基于完整工单信息判定分类和标签
- [ ] 将分类结果写入 `complaint_ticket_category_result`
- [ ] 将标签结果写入 `complaint_ticket_tag_result`
- [ ] 将关键词结果写入 `complaint_ticket_keyword_result`
- [ ] 将命中依据写入 `complaint_ticket_match_detail`

### 第四阶段：评估与反哺规则

- [ ] 统计分类命中率、标签命中率、冲突率
- [ ] 对比 AI 结果与现有业务字段映射效果
- [ ] 从原始投诉文本中提取高频关键词
- [ ] 反向沉淀分类关键词规则
- [ ] 反向沉淀标签关键词规则
- [ ] 校正分类-标签基线推荐关系

### 第五阶段：落地处置编排

- [ ] 根据分类 + 标签生成处理建议
- [ ] 根据分类 + 标签配置派单规则
- [ ] 根据分类 + 标签配置风险升级规则

## 当前优先级

1. 初始化 `complaint_category_tag_relation` 基线数据
2. 明确并落库规则表的第一版数据
3. 设计并实现历史工单批量 AI 标注流程
4. 在结果表中仅保留轻量评估字段 `evaluation_status`
5. 最后再补复杂统计层和处置编排层

## 设计原则

- 关系配置放数据库，不写死在代码里。
- 分类-标签推荐关系分两层：
  - 人工基线关系
  - 统计学习关系
- 初期先做人控基线，等历史结果稳定后再做动态统计增强。
- 结果表和规则表保持可追踪、可回溯、可复核。
