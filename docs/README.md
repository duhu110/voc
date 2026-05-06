# VOC Agent Documentation

当前有效设计以三类 Agent 为主：

- `converger_agent`：分类与标签收敛，已实现。
- `advice_builder_agent`：从历史处理摘要沉淀处理建议，已实现。
- `advice_provider_agent`：面向新工单检索建议并生成处理指引，待实现。

核心文档：

- [当前 Agent 架构](current-agent-architecture.md)

归档内容：

- `archive/legacy-2026-04-design/`：早期数据库、规则表、taxonomy 多轮设计和验证材料。仅作历史参考，不代表当前实现路线。
