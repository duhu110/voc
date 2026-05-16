#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-/home/voc}"
ROOT_ENV="${REPO_ROOT}/.env"
AGENT_ENV="${REPO_ROOT}/voc_agent/.env"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

mkdir -p "${REPO_ROOT}/deploy/chainlit/backups"

if [[ -f "${ROOT_ENV}" ]]; then
  cp "${ROOT_ENV}" "${REPO_ROOT}/deploy/chainlit/backups/root.env.${TIMESTAMP}.bak"
else
  touch "${ROOT_ENV}"
fi

if [[ -f "${AGENT_ENV}" ]]; then
  cp "${AGENT_ENV}" "${REPO_ROOT}/deploy/chainlit/backups/voc_agent.env.${TIMESTAMP}.bak"
fi

append_missing_keys() {
  local source_file="$1"
  local target_file="$2"

  [[ -f "${source_file}" ]] || return 0

  while IFS= read -r line || [[ -n "${line}" ]]; do
    [[ -z "${line}" ]] && continue
    [[ "${line}" =~ ^[[:space:]]*# ]] && continue

    key="${line%%=*}"
    if ! grep -q "^${key}=" "${target_file}"; then
      printf '%s\n' "${line}" >> "${target_file}"
    fi
  done < "${source_file}"
}

append_missing_keys "${AGENT_ENV}" "${ROOT_ENV}"

if [[ -f "${AGENT_ENV}" ]]; then
  mv "${AGENT_ENV}" "${AGENT_ENV}.disabled.${TIMESTAMP}"
fi

echo "Merged env into ${ROOT_ENV}"
echo "Disabled agent env: ${AGENT_ENV}.disabled.${TIMESTAMP}"
echo
echo "Current effective env:"
grep -E '^(DATABASEURL|DATABASE_URL|VOC_LLM_|VOC_VISION_|CHAINLIT_AUTH_SECRET|VOC_CHAINLIT_AUTH_USERS)=' "${ROOT_ENV}" \
  | sed -E \
      -e 's#^(DATABASEURL|DATABASE_URL)=.*#\1=<configured>#' \
      -e 's#^(VOC_LLM_API_KEY|VOC_VISION_API_KEY|CHAINLIT_AUTH_SECRET|VOC_CHAINLIT_AUTH_USERS)=.*#\1=<configured>#' \
  || true
