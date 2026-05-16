# 运营商投诉处理建议 Agent

本项目面向运营商投诉工单，当前主线不是单纯“自动分类”，而是把历史工单、历史处理摘要、专家处理案例组合起来，为新投诉生成更可执行的处理建议。

## 当前入口

- [项目地图](docs/project-map.md)：目录结构、几个 Agent 的职责、新工单处理链路。
- [数据库表说明](docs/database-tables.md)：当前远程库核心表用途、关键字段和表关系。
- [当前 Agent 架构](docs/current-agent-architecture.md)：三类 Agent 的处理流程、输出结构和验证方法。
- [系统演进方向](docs/system-evolution-rag-backend.md)：FastAPI 后端、Next.js 前端、RAG 服务和异步任务规划。
- [Chainlit 工单建议助手](chainlit_app/README.md)：聊天式 UI，本地运行和部署说明。
- [进度看板](progress_dashboard/README.md)：批处理覆盖、摘要质量、建议库覆盖情况。

归档的早期方案、旧 SQL、旧样例入口在 `OLD/`，仅作历史参考。

## 当前 Agent 分工

| Agent | 主要职责 | 主要写入表 | 主要读取表 |
| --- | --- | --- | --- |
| `converger_agent` | 历史工单分类、标签、处理摘要提取 | `converger_agent_result`、`converger_resolution_summary_atomic` | `raw_complaint_tickets` |
| `advice_builder_agent` | 从历史处理摘要归纳可复用建议 | `converger_handling_advice` | `converger_resolution_summary_atomic` |
| `advice_provider_agent` | 面向新投诉生成最终处理方案 | 不默认写库 | `converger_handling_advice`、`expert_handling_playbook`、历史分类/摘要表 |

新的正式后端入口位于 `backend_api/`，负责把已验证的 Python Agent、RAG 服务和后续导入/任务能力统一成 API。

`advice_provider_agent` 当前输出的主结果是 `final_action_plan`，会把处理建议组织成：

- 先核实事实
- 判断规则和责任
- 执行处理动作
- 回访和回单要求
- 必要时补充人工复核重点

## 核心数据表

| 表名 | 作用 |
| --- | --- |
| `raw_complaint_tickets` | 原始历史投诉工单。 |
| `converger_agent_result` | 每条工单的分类和标签结果。 |
| `converger_resolution_summary_atomic` | 从历史处理过程提炼出的处理摘要。 |
| `converger_handling_advice` | 从历史摘要归纳出的可复用处理建议。 |
| `expert_handling_playbook` | 人工专家案例沉淀的处理剧本，供新投诉召回。 |

详细字段说明见 [数据库表说明](docs/database-tables.md)。

## 本地运行

运行 `advice_provider_agent` 测试：

```powershell
$env:PYTHONPATH=(Get-Location).Path
uv run pytest voc_agent/advice_provider_agent/tests/test_provider.py
```

运行 Chainlit 工单建议助手：

```powershell
$env:PYTHONPATH=(Get-Location).Path
Push-Location .\chainlit_app
uv run chainlit run .\app.py
Pop-Location
```

图片直读需要配置支持 `image_url` 多模态消息的 OpenAI-compatible 模型；未设置 `VOC_VISION_*` 时默认沿用 `VOC_LLM_*`。

## 配置约定

- 根目录 `.env` 保存数据库和模型配置。
- 不要把真实数据库密码写入 README、docs 或 SQL 脚本。
- SQL 结构变更脚本放在 `sql_scripts/`。
- 当前有效文档放在 `docs/` 根目录；旧设计、旧检查表、历史验证材料统一放进 `OLD/`。
