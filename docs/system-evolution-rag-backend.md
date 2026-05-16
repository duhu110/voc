# 系统演进方向：FastAPI + Next.js + RAG

## 结论

长期方向采用：

```text
Next.js 运营前端
        ↓
FastAPI 业务后端
        ↓
PostgreSQL 结构化业务库
        ↓
embedding-service / RAG 服务
```

`progress_dashboard/` 和 `chainlit_app/` 继续作为过渡工具保留，后续由 Next.js 页面逐步替代。

## 为什么这样演进

- 现有 Agent 已经在 Python 中验证，不应重写到 Node。
- 工单导入、批量分类、经验提取、RAG 入库都是长任务，需要后端和 worker 承接。
- 分类、标签、建议库、专家经验库需要审核、版本、状态、追溯，不能只靠临时 UI。
- RAG 适合增强语义召回，但结构化库仍然是主干。

## RAG 服务定位

RAG 服务只负责语义检索和文档向量化。以下信息仍由本系统数据库维护：

- 知识库逻辑名称和业务归属。
- 专家经验、建议、摘要的启用状态。
- 审核状态和版本。
- 文档入库任务状态快照。
- AGENT 每次建议生成时的召回日志。

## 推荐知识库

| 逻辑名称 | 内容来源 | 用途 |
| --- | --- | --- |
| `voc-expert-playbooks` | `expert_handling_playbook` | 专家处理经验语义召回。 |
| `voc-handling-advices` | `converger_handling_advice` | 历史归纳建议语义召回。 |
| `voc-resolution-summaries` | 高质量 `converger_resolution_summary_atomic` | 相似历史处理路径参考。 |
| `voc-policy-docs` | 政策、规则、回单规范、业务口径文档 | 规则依据和回单依据补充。 |
| `voc-raw-ticket-cases` | 脱敏后的高质量历史工单 | 后期再启用，不建议第一批全量导入。 |

## 后端服务边界

新建 `backend_api/`，第一版只做薄封装：

- `/health`：检查业务数据库和 RAG 服务。
- `/agent/advice`：调用 `voc_agent.advice_provider_agent`。
- `/rag/*`：封装 embedding-service 的知识库、文档、任务、检索接口。

后续继续补：

- 工单导入 API。
- 异步任务 API。
- 分类和标签维护 API。
- 专家经验库 CRUD 和审核 API。
- RAG 文档同步任务。

## 数据库基础设施

新增脚本：

- `sql_scripts/2026-05-16_rag_integration_tables.sql`
- `deploy/scripts/init_rag_knowledge_bases.py`

核心表：

- `rag_knowledge_bases`：本系统知识库和 RAG `kb_id` 的映射。
- `rag_documents`：业务对象和 RAG `document_id` / `task_id` 的映射。
- `rag_ingestion_tasks`：RAG 入库任务状态快照。
- `rag_retrieval_logs`：AGENT 建议生成时的 RAG 召回日志。

初始化知识库映射：

```powershell
$env:PYTHONPATH=(Get-Location).Path
uv run python deploy/scripts/init_rag_knowledge_bases.py
```

## AGENT 建议链路升级

目标链路：

```text
新工单输入
  ↓
converger_agent 分类打标
  ↓
结构化召回：历史建议库 / 专家剧本 / 本地兜底剧本
  ↓
RAG 补充召回：专家经验 / 历史建议 / 历史摘要 / 政策规则
  ↓
后端过滤：active、reviewed、published、当前版本
  ↓
生成 final_action_plan
  ↓
写入 rag_retrieval_logs 和 advice_request_logs
```

第一阶段只接入 RAG 基础设施，不让 RAG 结果覆盖结构化命中结果。

## RAG 服务地址

业务代码只读一个变量：

```dotenv
RAG_BASE_URL=https://xnct.qhduhu.com:8884
```

部署到可访问内网的服务器时，可改为：

```dotenv
RAG_BASE_URL=http://172.31.255.59:8884
```

不要在业务代码中写死这两个地址。
