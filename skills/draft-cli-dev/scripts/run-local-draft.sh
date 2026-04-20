#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
CLI_DIR="${REPO_ROOT}/products/notion-editor/cli"
CLI_BIN="${CLI_DIR}/bin/draft.js"
DIST_ENTRY="${CLI_DIR}/dist/index.js"
DEV_PORT="${DRAFT_CLI_DEV_PORT:-31414}"

if [[ ! -f "${CLI_BIN}" ]]; then
  echo "draft-cli-dev: missing repo-local CLI entrypoint at ${CLI_BIN}" >&2
  exit 1
fi

ensure_build=0

if [[ ! -f "${DIST_ENTRY}" ]]; then
  ensure_build=1
else
  while IFS= read -r source_file; do
    if [[ "${source_file}" -nt "${DIST_ENTRY}" ]]; then
      ensure_build=1
      break
    fi
  done < <(find "${CLI_DIR}/src" "${CLI_DIR}/bin" "${CLI_DIR}/scripts" -type f 2>/dev/null | sort)
fi

if [[ "${DRAFT_CLI_DEV_SKIP_BUILD:-0}" != "1" && "${ensure_build}" == "1" ]]; then
  echo "draft-cli-dev: building repo-local CLI in ${CLI_DIR}" >&2
  (cd "${CLI_DIR}" && npm run build >/dev/null)
fi

port_explicit=0
for arg in "$@"; do
  if [[ "${arg}" == "--port" || "${arg}" == "-p" ]]; then
    port_explicit=1
    break
  fi
done

active_port="${DEV_PORT}"
if [[ "${port_explicit}" == "1" ]]; then
  active_port="explicit"
fi

echo "draft-cli-dev: cli=${CLI_BIN}" >&2
echo "draft-cli-dev: port=${active_port}" >&2

if [[ "${port_explicit}" == "1" ]]; then
  exec node "${CLI_BIN}" "$@"
fi

exec node "${CLI_BIN}" "$@" --port "${DEV_PORT}"
