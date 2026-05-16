# Chainlit Server Deployment

## Upload Target

Server repository root:

```text
/home/voc
```

Upload each file by keeping the same relative path under `/home/voc`.

Authoritative upload list:

- `deploy/chainlit/UPLOAD_FILES.txt`

## Windows Upload Example

From the local repo root:

```powershell
.\deploy\chainlit\local_upload_example.ps1 -Server root@your-server -RemoteRoot /home/voc
```

This script uploads only the files listed in `UPLOAD_FILES.txt`.

## Server Apply Steps

Run on the server after upload:

```bash
cd /home/voc
chmod +x deploy/chainlit/*.sh
./deploy/chainlit/server_merge_env.sh /home/voc
uv sync
./deploy/chainlit/server_smoke_test.sh /home/voc
./deploy/chainlit/server_start_chainlit.sh /home/voc 8883
```

Stop the service:

```bash
./deploy/chainlit/server_stop_chainlit.sh /home/voc
```

## Recommended Root Env

Keep only one effective env file:

```text
/home/voc/.env
```

The merge script copies any missing keys from `/home/voc/voc_agent/.env` into `/home/voc/.env`, then disables the agent env by renaming it to `voc_agent/.env.disabled.<timestamp>`.

Suggested `.env` shape:

```dotenv
DATABASEURL=postgresql://postgres:数据库密码@223.221.37.93:8881/voc

VOC_LLM_BASE_URL=https://wishub-x6.ctyun.cn/v1
VOC_LLM_MODEL_NAME=DeepSeek-V4-Flash
VOC_LLM_API_KEY=replace-me
VOC_LLM_TEMPERATURE=0

CHAINLIT_AUTH_SECRET=replace-with-a-random-secret
VOC_CHAINLIT_AUTH_USERS=admin:sha256:<password_sha256_hex>

# Optional dedicated vision config. If omitted, the app falls back to VOC_LLM_*.
# VOC_VISION_BASE_URL=https://example.com/v1
# VOC_VISION_MODEL_NAME=your-vision-model
# VOC_VISION_API_KEY=replace-me
```

## What The Smoke Test Checks

- `voc_agent.core.config.get_settings()` can read the merged env
- database connectivity works
- targeted tests pass:
  - `voc_agent/advice_provider_agent/tests`
  - `chainlit_app/tests`
- `chainlit_app.app` can import with auth env present

## Notes

- The vision model is only used to transcribe or translate image text into Chinese text.
- Classification, tags, risk checks, and advice generation still run through the existing text LLM pipeline.
