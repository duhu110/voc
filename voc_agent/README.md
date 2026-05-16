# voc_agent 模块说明

`voc_agent/` 是投诉处理建议链路的核心代码目录。

## 目录分工

| 路径 | 作用 |
| --- | --- |
| `converger_agent/` | 历史工单分类、标签、处理摘要提取。 |
| `advice_builder_agent/` | 从历史处理摘要归纳可复用建议，写入 `converger_handling_advice`。 |
| `advice_provider_agent/` | 面向新投诉生成最终处理方案。 |
| `share/` | 共享读取、映射、工具函数。 |
| `core/` | 配置、数据库连接、LLM 客户端等公共能力。 |

## advice_provider_agent 当前重点文件

| 文件 | 作用 |
| --- | --- |
| `provider.py` | 新工单建议主编排：分类、召回、风险、最终输出。 |
| `action_plan.py` | 把候选建议整理为四段式 `final_action_plan`。 |
| `experience_playbooks.py` | 本地兜底经验剧本，覆盖常见高频场景。 |
| `reply_standards.py` | 回访和回单规范提醒。 |
| `input_normalizer.py` | Chainlit 输入和截图转写文本的工单字段归一化。 |

更完整的架构说明见 `../docs/current-agent-architecture.md`。
