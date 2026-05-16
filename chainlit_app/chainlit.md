# VOC 工单处理建议助手

输入投诉描述，或上传包含投诉信息的截图。图片模型只负责把截图转写/翻译成中文文本，后续分类、标签、处理建议、风险提醒和人工复核判断仍由文本 LLM 链路完成。

图片直读需要配置支持 `image_url` 多模态消息的 OpenAI-compatible 模型。可选环境变量：

- `VOC_VISION_MODEL_NAME`
- `VOC_VISION_BASE_URL`
- `VOC_VISION_API_KEY`

未设置时默认沿用 `VOC_LLM_*` 配置。
