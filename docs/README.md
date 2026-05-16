# VOC Agent 文档入口

当前有效文档：

- [项目地图](project-map.md)：目录结构、几个 Agent 的职责、新工单处理链路。
- [数据库表说明](database-tables.md)：当前远程库核心表用途、关键字段和表关系。
- [当前 Agent 架构](current-agent-architecture.md)：Agent 处理流程和验证方法。
- [系统演进方向](system-evolution-rag-backend.md)：FastAPI、Next.js、RAG 服务和任务化演进路线。

归档内容：

- `../OLD/`：早期数据库、规则表、taxonomy 多轮设计、旧 SQL、旧样例入口和验证材料。仅作历史参考，不代表当前实现路线。

维护约定：

- 新的当前状态文档放在 `docs/` 根目录。
- 旧方案、废弃设计、历史验证材料放进根目录 `OLD/`。
- 数据库结构变更脚本放在 `sql_scripts/`。
- 不要在文档中保存真实数据库密码。
