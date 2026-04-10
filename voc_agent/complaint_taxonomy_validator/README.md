# complaint_taxonomy_validator

## 这个 Agent 在做什么

`complaint_taxonomy_validator` 是项目的第一个验证型 Agent。

它的目标不是回写数据库，也不是直接进入生产处理流程，而是先验证当前投诉分类体系和标签体系是否可用。

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

## 当前边界

当前版本只做：
- 读取原始工单
- 读取分类和标签上下文
- 调用 LLM 做验证性识别
- 返回统一 JSON 结构

当前版本不做：
- 不回写数据库
- 不修改分类和标签主数据
- 不生成规则入库
- 不做批量评估统计

## 目录结构

- `chain.py`: 只负责组装 LangGraph
- `nodes/`: 图节点逻辑
- `tools/`: 当前 Agent 专用工具
- `utils/`: 当前 Agent 专用归一化与辅助逻辑
- `prompts.py`: Prompt 构造
- `state.py`: 状态和结构化输出模型

## 设计原则

- 通用 DB 工具放 `voc_agent/share/tools`
- Agent 专用工具放本 agent 的 `tools/`
- 节点逻辑放 `nodes/`
- 通用解析逻辑放 `voc_agent/share/utils`
- Agent 专用结果归一化放本 agent 的 `utils/`

## 当前建议的下一步

1. 提升 prompt 对真实分类编码的约束能力
2. 增加批量样本验证入口
3. 将验证结果保存为本地 JSONL/CSV，用于人工评估
