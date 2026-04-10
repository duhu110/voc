# 数据库检查清单

本文档记录 2026-04-10 对当前项目数据库做的逐表巡检与修复结果。巡检和修复通过项目数据库技能执行：

- 技能入口：`/Users/duhu/code/voc/.codex/skills/project-db-executor/SKILL.md`
- 执行脚本：`/Users/duhu/code/voc/.codex/skills/project-db-executor/scripts/run_sql.py`

## 一、巡检范围

本次逐表检查覆盖 17 张表：

- `raw_complaint_tickets`
- `complaint_category`
- `complaint_tag_group`
- `complaint_tag`
- `complaint_category_tag_relation`
- `complaint_category_rule`
- `complaint_tag_rule`
- `complaint_ticket_category_result`
- `complaint_ticket_tag_result`
- `complaint_ticket_keyword_result`
- `complaint_ticket_match_detail`
- `complaint_category_stats`
- `complaint_tag_stats`
- `complaint_category_tag_stat_relation`
- `complaint_category_keyword_stat`
- `complaint_tag_keyword_stat`
- `complaint_disposition_rule`

检查项包括：

- 表是否存在
- 主键、唯一约束、外键是否存在
- 关键索引是否存在
- 表注释、字段注释是否存在
- 关键时间字段和评估字段是否存在
- 主数据与规则表是否已有初始化数据

## 二、本轮已执行修复

### 1. 补齐表注释

已补齐以下 6 张表的表注释：

- [x] `complaint_category_stats`
- [x] `complaint_tag_stats`
- [x] `complaint_category_tag_stat_relation`
- [x] `complaint_category_keyword_stat`
- [x] `complaint_tag_keyword_stat`
- [x] `complaint_disposition_rule`

### 2. 补齐字段注释

已补齐以下项目管理表的字段注释：

- [x] `complaint_category`
- [x] `complaint_tag_group`
- [x] `complaint_tag`
- [x] `complaint_category_tag_relation`
- [x] `complaint_category_rule`
- [x] `complaint_tag_rule`
- [x] `complaint_ticket_category_result`
- [x] `complaint_ticket_tag_result`
- [x] `complaint_ticket_keyword_result`
- [x] `complaint_ticket_match_detail`
- [x] `complaint_category_stats`
- [x] `complaint_tag_stats`
- [x] `complaint_category_tag_stat_relation`
- [x] `complaint_category_keyword_stat`
- [x] `complaint_tag_keyword_stat`
- [x] `complaint_disposition_rule`

### 3. 补齐索引

本轮新增索引：

- [x] `idx_complaint_category_tag_relation_tag_id`
- [x] `idx_complaint_category_tag_stat_relation_tag_id`
- [x] `idx_complaint_disposition_rule_category_id`
- [x] `idx_complaint_disposition_rule_tag_id`

## 三、逐表结果

### 1. 源数据层

| 表名 | 存在 | 表注释 | 字段注释 | 主键 | 索引 | 当前结论 |
|---|---|---|---|---|---|---|
| `raw_complaint_tickets` | 是 | 是 | 否 | 是 | 是 | 结构可用，字段语义已整理到文档，数据库字段注释未回写 |

说明：

- `raw_complaint_tickets` 是业务已有源表，不由当前仓库初始化
- 当前主键为 `ticket_id`
- 已存在索引：`raw_complaint_tickets_pkey`、`idx_ticket_process_status`、`idx_ticket_emotion`、`idx_ticket_risk`
- 已从历史建表代码和 AI 提示词中恢复出该表的参考 DDL、字段分区和核心字段含义，已写入 `docs/db_design.md`
- 当前数据库里这 51 个字段仍未真正写入 `comment on column ...` 注释
- 后续如果要把文档定义同步到数据库，建议优先补 5 个系统字段、5 个 AI 特征字段和 6 个核心文本字段

### 2. 主数据层

| 表名 | 存在 | 表注释 | 字段注释 | 主键 | 唯一约束 | 外键 | 索引 | 当前结论 |
|---|---|---|---|---|---|---|---|---|
| `complaint_category` | 是 | 是 | 是 | 是 | 是 | 是 | 是 | 完成 |
| `complaint_tag_group` | 是 | 是 | 是 | 是 | 是 | 否 | 是 | 完成 |
| `complaint_tag` | 是 | 是 | 是 | 是 | 是 | 是 | 是 | 完成 |
| `complaint_category_tag_relation` | 是 | 是 | 是 | 是 | 是 | 是 | 是 | 完成 |

关键点：

- [x] `complaint_category` 有主键、编码唯一约束、树结构索引
- [x] `complaint_tag_group` 有主键、编码唯一约束
- [x] `complaint_tag` 有 `(group_id, code)`、`(group_id, name)` 唯一约束
- [x] `complaint_category_tag_relation` 有唯一约束 `(category_id, tag_id, relation_type)`
- [x] `complaint_category_tag_relation` 已补 `tag_id` 方向索引

### 3. 规则层

| 表名 | 存在 | 表注释 | 字段注释 | 主键 | 唯一约束 | 外键 | 索引 | 当前结论 |
|---|---|---|---|---|---|---|---|---|
| `complaint_category_rule` | 是 | 是 | 是 | 是 | 是 | 是 | 是 | 结构完成，数据未初始化 |
| `complaint_tag_rule` | 是 | 是 | 是 | 是 | 是 | 是 | 是 | 结构完成，数据未初始化 |

关键点：

- [x] `complaint_category_rule` 已有防重复唯一约束
- [x] `complaint_tag_rule` 已有防重复唯一约束
- [x] 两张规则表的外键索引已存在

### 4. AI 结果层

| 表名 | 存在 | 表注释 | 字段注释 | 主键 | 唯一约束 | 外键 | 索引 | 关键字段 | 当前结论 |
|---|---|---|---|---|---|---|---|---|---|
| `complaint_ticket_category_result` | 是 | 是 | 是 | 是 | 是 | 是 | 是 | `created_at` `updated_at` `evaluation_status` | 完成 |
| `complaint_ticket_tag_result` | 是 | 是 | 是 | 是 | 是 | 是 | 是 | `created_at` `updated_at` `evaluation_status` | 完成 |
| `complaint_ticket_keyword_result` | 是 | 是 | 是 | 是 | 不要求 | 否 | 是 | `created_at` `updated_at` | 完成 |
| `complaint_ticket_match_detail` | 是 | 是 | 是 | 是 | 不要求 | 否 | 是 | `created_at` `updated_at` | 完成 |

关键点：

- [x] 两张结果表均已补 `updated_at`
- [x] 两张结果表均已存在 `evaluation_status`
- [x] `complaint_ticket_category_result` 有唯一约束 `(ticket_id, result_source, ranking_no)`
- [x] `complaint_ticket_tag_result` 有唯一约束 `(ticket_id, tag_id, result_source, ranking_no)`
- [x] `complaint_ticket_keyword_result(ticket_id)` 索引已存在
- [x] `complaint_ticket_match_detail(ticket_id)` 索引已存在

### 5. 统计与编排层

| 表名 | 存在 | 表注释 | 字段注释 | 主键 | 唯一约束 | 外键 | 索引 | 当前结论 |
|---|---|---|---|---|---|---|---|---|
| `complaint_category_stats` | 是 | 是 | 是 | 是 | 是 | 是 | 是 | 完成 |
| `complaint_tag_stats` | 是 | 是 | 是 | 是 | 是 | 是 | 是 | 完成 |
| `complaint_category_tag_stat_relation` | 是 | 是 | 是 | 是 | 是 | 是 | 是 | 完成 |
| `complaint_category_keyword_stat` | 是 | 是 | 是 | 是 | 是 | 是 | 是 | 完成 |
| `complaint_tag_keyword_stat` | 是 | 是 | 是 | 是 | 是 | 是 | 是 | 完成 |
| `complaint_disposition_rule` | 是 | 是 | 是 | 是 | 按设计无 | 是 | 是 | 完成 |

关键点：

- [x] 6 张统计与编排表表注释已补齐
- [x] 6 张统计与编排表字段注释已补齐
- [x] `complaint_category_tag_stat_relation` 已补 `tag_id` 方向索引
- [x] `complaint_disposition_rule` 已补 `category_id`、`tag_id` 索引
- [x] `complaint_disposition_rule` 当前没有唯一约束，按现阶段设计允许同一分类/标签下存在多条动作规则

## 四、初始化数据检查

### 主数据

| 表名 | 当前记录数 | 状态 |
|---|---:|---|
| `complaint_category` | 268 | 已初始化 |
| `complaint_tag_group` | 8 | 已初始化 |
| `complaint_tag` | 59 | 已初始化 |

### 基线关系与规则

| 表名 | 当前记录数 | 状态 |
|---|---:|---|
| `complaint_category_tag_relation` | 0 | 待初始化 |
| `complaint_category_rule` | 0 | 待初始化 |
| `complaint_tag_rule` | 0 | 待初始化 |

结论：

- 分类和标签主数据已落库
- 基线关系和规则表结构已就绪，但数据还没有开始填充

## 五、最终判断

### 已完成

- [x] 17 张目标表全部存在
- [x] 所有项目管理表均有主键
- [x] 所有项目管理表均已补表注释
- [x] 除 `raw_complaint_tickets` 外，所有项目管理表均已补字段注释
- [x] `raw_complaint_tickets` 的参考 DDL 与字段语义已补入设计文档
- [x] 核心唯一约束已齐
- [x] 核心外键索引已齐
- [x] 结果表 `updated_at` 与 `evaluation_status` 已齐
- [x] 统计层和处置编排层已从“部分完成”修复到“结构完成”

### 仍待推进

- [ ] `raw_complaint_tickets` 的字段注释仍需正式回写到数据库
- [ ] `complaint_category_tag_relation` 首版基线数据需初始化
- [ ] `complaint_category_rule` 首版规则数据需初始化
- [ ] `complaint_tag_rule` 首版规则数据需初始化
- [ ] 统计表和处理建议表的实际写入逻辑仍需在后续 AI 阶段接入

## 六、结论

如果只看“数据库结构是否完整可用”，当前答案是：

- **是，当前数据库结构已经可以支撑下一阶段的历史工单 AI 标注工作。**

如果看“是否已经进入可运营状态”，当前还差：

- 分类-标签基线关系数据
- 分类规则数据
- 标签规则数据
- 历史工单首轮 AI 结果回写流程
