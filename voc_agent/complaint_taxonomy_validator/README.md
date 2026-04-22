# complaint_taxonomy_validator

## 这个 Agent 在做什么

`complaint_taxonomy_validator` 是项目的第一个验证型 Agent。

它的第一目标是验证当前投诉分类体系和标签体系是否可用，并把验证结果按结果表结构落库，供后续评估与统计使用。

输入：
- `raw_complaint_tickets` 中的单条原始工单
- 当前启用的分类树
- 当前启用的标签体系

输出：
- 主分类候选
- 候选标签
- 分类关键词
- 标签关键词
- 风险与不确定点
- 结果表、关键词表、命中明细表的数据库写入 payload
- 统计表与关系表的聚合刷新能力

## 当前边界

当前版本只做：
- 读取原始工单
- 读取分类和标签上下文
- 调用 LLM 做验证性识别
- 返回统一 JSON 结构
- 将 AI 结果写入结果表与命中明细表
- 将 `raw_complaint_tickets.process_status` 更新为是否已处理
- 提供统计表与关系表的刷新脚本入口

当前版本不做：
- 不修改分类和标签主数据
- 不生成规则入库
- 不做自动调度和定时运行
- 不自动修正规则或基线关系

## 目录结构

- `chain.py`: 只负责组装 LangGraph
- `persistence.py`: 单条工单的结果落库入口
- `batch_persistence.py`: 批量处理未落库工单的入口
- `stats_aggregation.py`: 统计表与关系表刷新入口
- `nodes/`: 图节点逻辑
- `tools/`: 当前 Agent 专用工具
- `utils/`: 当前 Agent 专用归一化与辅助逻辑
- `prompts.py`: Prompt 构造
- `state.py`: 状态和结构化输出模型

## 当前可运行入口

- 单条工单验证：`python -m voc_agent.complaint_taxonomy_validator.tests.manual_validate_ticket --ticket-id <ticket_id>`
- 刷新统计表：`python -m voc_agent.complaint_taxonomy_validator.stats_aggregation --stat-date 2026-04-10`
- 单条工单落库：通过 `run_validator_and_persist(ticket_id)` 调用
- 批量处理未处理工单：通过 `run_persistence_batch(sample_size=20)` 调用

统计刷新说明：
- `complaint_category_stats` 和 `complaint_tag_stats` 按指定 `stat_date` 重算当天 AI 结果
- `complaint_category_tag_stat_relation`、`complaint_category_keyword_stat`、`complaint_tag_keyword_stat` 会按当前 AI 结果全量重建

## 设计原则

- 通用 DB 工具放 `voc_agent/share/tools`
- Agent 专用工具放本 agent 的 `tools/`
- 节点逻辑放 `nodes/`
- 通用解析逻辑放 `voc_agent/share/utils`
- Agent 专用结果归一化放本 agent 的 `utils/`

## 当前建议的下一步

1. 给统计刷新补批处理编排或定时调度
2. 明确统计表全量/增量策略，避免大表重算
3. 为失败重试和幂等写入补充运行态日志
