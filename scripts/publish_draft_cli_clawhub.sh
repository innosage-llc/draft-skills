#!/usr/bin/env bash
set -euo pipefail

# publish_draft_cli_clawhub.sh
# Automates Phase 1 (Preparation) and Phase 2 (Publication) for the draft-cli skill.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_PATH="$REPO_ROOT/skills/draft-cli/SKILL.md"
GATE_SCRIPT="$REPO_ROOT/scripts/gate"

echo "🚀 Starting publication process for draft-cli..."

# 1. Validation
echo "🔍 Running local validation gates..."
if ! "$GATE_SCRIPT"; then
    echo "❌ Validation failed. Aborting publication."
    exit 1
fi

# 2. Version Management (SSOT: package.json)
# Usage hint: bump version BEFORE running this script using 'npm version patch|minor|major'
CURRENT_VERSION=$(node -p "require('./package.json').version")
echo "📦 Current version from package.json: $CURRENT_VERSION"

# (Optional: If you want to automate the bump inside this script, uncomment below)
# if [[ "${1:-}" == "--bump" ]]; then
#   npm version patch --no-git-tag-version
#   CURRENT_VERSION=$(node -p "require('./package.json').version")
#   echo "⬆️ Bumped to version: $CURRENT_VERSION"
# fi

# 3. Commit Changes (if needed)
# Since npm version (without --no-git-tag-version) already commits, we only check for remaining changes.
if [[ -n "$(git status --porcelain package.json)" ]]; then
    echo "💾 Committing version updates..."
    git add package.json
    git commit -m "chore(release): bump version to $CURRENT_VERSION"
fi

# 4. Publication
echo "☁️ Publishing to ClawHub..."
clawhub publish "$REPO_ROOT/skills/draft-cli" \
  --slug draft-cli \
  --name "Draft CLI" \
  --version "$CURRENT_VERSION" \
  --tags latest

echo "✅ Publication successful! draft-cli is now live at version $CURRENT_VERSION."
echo "🔗 Verify with: clawhub inspect draft-cli"
