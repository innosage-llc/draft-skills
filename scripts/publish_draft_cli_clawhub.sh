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

# 2. Version Management
NEW_VERSION=$(grep '"version":' "$REPO_ROOT/package.json" | head -1 | cut -d'"' -f4)
echo "📦 Version to publish (from package.json): $NEW_VERSION"

# Ensure SKILL.md is in sync
CURRENT_SKILL_VERSION=$(grep -o '"version":"[^"]*"' "$SKILL_PATH" | head -1 | cut -d'"' -f4 || echo "")
if [[ -n "$CURRENT_SKILL_VERSION" && "$CURRENT_SKILL_VERSION" != "$NEW_VERSION" ]]; then
    echo "⬆️ Syncing version in $SKILL_PATH to $NEW_VERSION..."
    sed -i '' "s/\"version\":\"$CURRENT_SKILL_VERSION\"/\"version\":\"$NEW_VERSION\"/" "$SKILL_PATH"
fi

# 3. Commit Changes
echo "💾 Committing version updates..."
cd "$REPO_ROOT"
git add "$SKILL_PATH" "package.json"
git commit -m "chore(release): bump draft-cli to $NEW_VERSION for ClawHub publication" || echo "No changes to commit"

# 4. Publication
echo "☁️ Publishing to ClawHub..."
clawhub publish "$REPO_ROOT/skills/draft-cli" \
  --slug draft-cli \
  --name "Draft CLI" \
  --version "$NEW_VERSION" \
  --tags latest

echo "✅ Publication successful! draft-cli is now live at version $NEW_VERSION."
echo "🔗 Verify with: clawhub inspect draft-cli"
