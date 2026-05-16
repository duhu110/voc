# Chainlit 工单建议 UI

本目录是 VOC 项目的聊天式处理建议入口，支持自由文本和图片输入。图片模型只负责把截图转写/翻译成中文文本，分类、标签、建议检索和风险判断仍由现有文本 LLM 链路完成。

## 启动

在仓库根目录运行：

```powershell
Push-Location .\chainlit_app
..\.venv\Scripts\python.exe -m chainlit run .\app.py
Pop-Location
```

应用会读取仓库根目录 `.env` 和 `voc_agent/.env` 中的数据库与模型配置。

## 主题与品牌定制

Chainlit 主题和品牌资产放在 `chainlit_app/public`：

- `theme.json`：浅色/深色主题变量，颜色按 Chainlit 要求使用 HSL。
- `stylesheet.css`：补充消息排版、输入区、命中依据卡片等细节样式。
- `logo_light.png` / `logo_dark.png`：Chainlit 自动识别的明暗主题 Logo。
- `favicon`：Chainlit 自动识别的浏览器图标文件。
- `login-background.png`：登录页背景图。
- `meta-card.png`：Open Graph 预览图。

`.chainlit/config.toml` 的 `[UI]` 已启用 `custom_css`、`login_page_image`、`custom_meta_image_url`、宽布局和默认浅色主题。更新这些文件后需要重启 Chainlit 才能看到完整效果；浏览器可能会缓存 Logo 和 favicon。

## 登录认证

Chainlit 登录需要配置会话密钥和用户清单：

```dotenv
CHAINLIT_AUTH_SECRET=请换成一段随机长字符串
VOC_CHAINLIT_AUTH_USERS=admin:sha256:<password_sha256_hex>
```

生成密码哈希：

```powershell
.\.venv\Scripts\python.exe -c "import hashlib; print(hashlib.sha256('你的密码'.encode('utf-8')).hexdigest())"
```

也支持多个用户：

```dotenv
VOC_CHAINLIT_AUTH_USERS=admin:sha256:<hash>;operator:sha256:<hash>
```

## 图片模型配置

图片输入需要支持 `image_url` 多模态消息的 OpenAI-compatible 模型。该模型只需要做图片文字转写/翻译，不参与业务分类或建议生成。未配置视觉模型时会沿用现有 `VOC_LLM_*` 配置。

```dotenv
VOC_VISION_BASE_URL=https://example.com/v1
VOC_VISION_MODEL_NAME=your-vision-model
VOC_VISION_API_KEY=your-api-key
```

## 数据库配置

开发和部署统一读取仓库根目录 `.env`。数据库连接统一指向远程业务库：

```dotenv
DATABASEURL=postgresql://postgres:数据库密码@223.221.37.93:8881/voc
```

当前 UI 只读取 `raw_complaint_tickets`、`converger_handling_advice`、`converger_resolution_summary_atomic` 等表，不写入用户输入或建议结果。
