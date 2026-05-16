# VOC FastAPI 后端

这是新的正式后端服务入口，目标是逐步替代临时的 Streamlit/Chainlit 直连模式。

## 当前能力

- `/health`：检查业务数据库和 RAG 服务。
- `/agent/advice`：调用已验证的 `voc_agent.advice_provider_agent` 生成处理建议。
- `/rag/*`：封装 embedding-service 的知识库、文档上传、任务、检索接口。

## 启动

在仓库根目录运行：

```powershell
$env:PYTHONPATH=(Get-Location).Path
uv run uvicorn backend_api.main:app --reload --host 0.0.0.0 --port 8010
```

后续 Next.js 前端只应调用这个后端，不直接访问数据库或 RAG 服务。

