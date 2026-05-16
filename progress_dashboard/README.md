# VOC 项目进度统计看板

这是一个独立的 Streamlit 小项目，用于统计 VOC 项目整体进度。当前看板包含多个页面：

- 首页：第一阶段分类 AGENT 运行结果，统计口径参考 `sql_scripts/2026-05-06_converger_data_audit.sql`
- 第二阶段页面：`advice_builder_agent` 运行结果，统计 `converger_handling_advice` 对历史摘要场景的覆盖情况

## 第一阶段页面

- 总体工单处理进度
- 分类结果和摘要覆盖率
- 状态、结果、摘要一致性检查
- 分类体系版本、AGENT 版本、模型和结果状态分布
- 分类结果分布
- 诉求、情绪、风险、产品标签覆盖与分布
- 摘要质量信号与异常样本
- 处理建议准备度和缺口
- 近期人工复核样本

## 第二阶段页面

- 活跃处理建议总数
- 已覆盖叶子分类和场景数
- 按历史摘要场景统计的覆盖率
- 按样本量分层覆盖及目标判断
- 未覆盖的高价值场景
- 处理建议质量抽样

## 本地启动

在仓库根目录运行：

```powershell
.\.venv\Scripts\python.exe -m streamlit run .\progress_dashboard\app.py
```

看板会读取仓库根目录 `.env` 中的 `DATABASEURL`、`DATABASE_URL` 或 `DB_URL`。

## 数据库环境变量

开发和部署统一读取仓库根目录 `.env`，数据库连接统一指向远程业务库：

```dotenv
DATABASEURL=postgresql://postgres:数据库密码@223.221.37.93:8881/voc
```

## 服务器手动启动 8882

在仓库根目录运行：

```bash
python -m streamlit run progress_dashboard/app.py \
  --server.port 8882 \
  --server.address 0.0.0.0 \
  --server.headless true
```

如果你使用项目虚拟环境：

```bash
./.venv/bin/python -m streamlit run progress_dashboard/app.py \
  --server.port 8882 \
  --server.address 0.0.0.0 \
  --server.headless true
```

启动后浏览器访问：

```text
http://服务器IP:8882
```

如果只允许本机访问，可以把 `--server.address 0.0.0.0` 改成 `--server.address 127.0.0.1`。

## 目录结构

```text
progress_dashboard/
  app.py              # 第一阶段页面
  pages/              # 第二阶段等独立页面
  db.py               # 数据库连接和查询缓存
  queries.py          # 统计 SQL
  requirements.txt    # 独立依赖声明
  README.md           # 使用说明
```
