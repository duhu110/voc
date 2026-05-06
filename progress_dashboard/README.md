# VOC 项目进度统计看板

这是一个独立的 Streamlit 小项目，用于统计 VOC 项目整体进度。当前第一版页面聚焦第一阶段分类 AGENT 的运行结果，统计口径参考 `sql_scripts/2026-05-06_converger_data_audit.sql`。

## 当前页面

- 总体工单处理进度
- 分类结果和摘要覆盖率
- 状态、结果、摘要一致性检查
- 分类体系版本、AGENT 版本、模型和结果状态分布
- 分类结果分布
- 诉求、情绪、风险、产品标签覆盖与分布
- 摘要质量信号与异常样本
- 处理建议准备度和缺口
- 近期人工复核样本

## 启动

在仓库根目录运行：

```powershell
.\.venv\Scripts\python.exe -m streamlit run .\progress_dashboard\app.py
```

看板会读取仓库根目录 `.env` 中的 `DATABASEURL`、`DATABASE_URL` 或 `DB_URL`。

## 目录结构

```text
progress_dashboard/
  app.py              # Streamlit 页面
  db.py               # 数据库连接和查询缓存
  queries.py          # 统计 SQL
  requirements.txt    # 独立依赖声明
  README.md           # 使用说明
```
