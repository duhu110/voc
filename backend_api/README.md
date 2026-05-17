# VOC FastAPI 后端

这是新的正式后端服务入口，目标是逐步替代临时的 Streamlit/Chainlit 直连模式。

## 当前能力

- `/health`：检查业务数据库和 RAG 服务。
- `/auth/login`、`/auth/me`、`/auth/change-password`：后台用户登录、当前用户和修改密码。
- `/users`：后台用户管理接口，管理员可维护账号、角色、状态和重置密码。
- `/overview`：管理端首页统计。
- `/agent/advice`：调用已验证的 `voc_agent.advice_provider_agent` 生成处理建议。
- `/tickets`：历史工单查询、详情和按工单生成建议。
- `/expert-playbooks`：专家经验库列表、详情、新增、更新。
- `/handling-advices`：历史建议库列表和详情。
- `/taxonomy`：分类和标签体系查询。
- `/rag/*`：封装 embedding-service 的知识库、文档上传、任务、检索接口。
- `/rag/mappings`：查看本系统维护的 RAG 知识库映射。
- `/rag/mappings/{logical_name}/search`：按业务逻辑名检索知识库，并写入召回日志。

## 前端常用接口

```text
POST /auth/login
GET  /auth/me
POST /auth/change-password
GET  /users
POST /users
GET  /users/{user_id}
PATCH /users/{user_id}
POST /users/{user_id}/reset-password
GET  /overview
GET  /overview/classification-distribution
GET  /tickets
GET  /tickets/{ticket_id}
POST /tickets/{ticket_id}/advice
POST /agent/advice
GET  /expert-playbooks
POST /expert-playbooks
GET  /expert-playbooks/{playbook_id}
PATCH /expert-playbooks/{playbook_id}
GET  /handling-advices
GET  /handling-advices/{advice_id}
GET  /taxonomy/categories
GET  /taxonomy/tags/{request|emotion|risk|product}
GET  /rag/mappings
POST /rag/mappings/{logical_name}/search
```

## 专家经验导入 RAG

当前远程库 `expert_handling_playbook` 已保存从 `热点投诉问题案例处理分享.xlsx` 导入的专家案例。同步到 RAG 知识库：

```powershell
$env:PYTHONPATH=(Get-Location).Path
uv run python deploy/scripts/sync_expert_playbooks_to_rag.py
```

## 初始化管理员

用户表由 `sql_scripts/2026-05-17_backend_auth_tables.sql` 创建。首次部署后创建后台管理员：

```powershell
$env:PYTHONPATH=(Get-Location).Path
uv run python deploy/scripts/init_backend_admin.py --username admin
```

如果账号已经存在并且需要重置密码：

```powershell
$env:PYTHONPATH=(Get-Location).Path
uv run python deploy/scripts/init_backend_admin.py --username admin --reset-existing
```

## 启动

在仓库根目录运行：

```powershell
$env:PYTHONPATH=(Get-Location).Path
uv run uvicorn backend_api.main:app --reload --host 0.0.0.0 --port 8010
```

后续 Next.js 前端只应调用这个后端，不直接访问数据库或 RAG 服务。
