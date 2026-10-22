#!/usr/bin/env bash
# Validation is safe by default. Public release still needs separate user approval.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
mode=dry-run
skill=draft-cli
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) mode=dry-run; shift ;;
    --publish) mode=publish; shift ;;
    --skill) [[ $# -ge 2 ]] || { echo 'Missing --skill value' >&2; exit 2; }; skill="$2"; shift 2 ;;
    *) echo "Usage: $0 [--dry-run|--publish] [--skill draft-cli|draft-agent-loop]" >&2; exit 2 ;;
  esac
done
case "$skill" in draft-cli|draft-agent-loop) ;; *) echo 'Unsupported skill' >&2; exit 2 ;; esac
# Always run the authoritative gate. Never commit, tag, push or change versions.
if ! "$REPO_ROOT/scripts/gate"; then
  echo 'Preflight failed: repair scripts/gate before publication.' >&2
  exit 1
fi
version="$(sed -n 's/^version: "\([0-9][0-9.]*\)"$/\1/p' "skills/$skill/SKILL.md")"
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo 'Invalid skill version' >&2; exit 1; }
printf 'Validated %s@%s\n' "$skill" "$version"
shasum -a 256 "skills/$skill/SKILL.md"
if [[ "$mode" == dry-run ]]; then
  echo 'DRY RUN: no publication, commits, tags or pushes. Separate release approval required.'
  exit 0
fi
[[ -z "$(git status --porcelain)" ]] || { echo 'Commit reviewed changes before publishing.' >&2; exit 1; }
command -v clawhub >/dev/null || { echo 'clawhub CLI required for approved publication.' >&2; exit 1; }
clawhub publish "$REPO_ROOT/skills/$skill" --slug "$skill" --name "$skill" --version "$version" --tags latest
# Success is not an artifact/audit receipt; duplicate versions fail rather than imply equality.
echo "Upload returned success. Inspect exact $skill@$version bytes and audit before declaring release consistency."
