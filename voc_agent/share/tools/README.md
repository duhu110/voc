# Share Tools

这里放所有 agent 之间可复用的数据库读取工具。

规则：
- 一个工具一个文件
- 只做单一职责的数据读取或轻量数据访问
- 不在这里写 agent 专属流程逻辑
- 工具函数必须有清晰 docstring

当前工具：
- `fetch_ticket.py`: 按 `ticket_id` 读取原始工单
- `fetch_enabled_categories.py`: 读取启用中的分类树
- `fetch_enabled_tags.py`: 读取启用中的标签体系
