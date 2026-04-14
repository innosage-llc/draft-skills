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
CURRENT_VERSION=$(grep "version:" "$SKILL_PATH" | awk -F'"' '{print $2}')
echo "📦 Current version: $CURRENT_VERSION"

# Simple patch version bump (e.g., 1.4 -> 1.4.1 or 1.4.1 -> 1.4.2)
if [[ $CURRENT_VERSION =~ ^([0-9]+)\.([0-9]+)$ ]]; then
    NEW_VERSION="${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.1"
elif [[ $CURRENT_VERSION =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    NEW_VERSION="${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.$((BASH_REMATCH[3] + 1))"
else
    echo "❌ Could not parse version '$CURRENT_VERSION'. Please update SKILL.md manually."
    exit 1
fi

echo "⬆️ Bumping version to $NEW_VERSION..."
sed -i '' "s/version: \"$CURRENT_VERSION\"/version: \"$NEW_VERSION\"/" "$SKILL_PATH"

# 3. Commit Changes (Submodule)
echo "💾 Committing version bump to submodule..."
cd "$REPO_ROOT"
git add "$SKILL_PATH"
git commit -m "chore(release): bump draft-cli to $NEW_VERSION for ClawHub publication"

# 4. Publication
echo "☁️ Publishing to ClawHub..."
clawhub publish "$REPO_ROOT/skills/draft-cli" \
  --slug draft-cli \
  --name "Draft CLI" \
  --version "$NEW_VERSION" \
  --tags latest

echo "✅ Publication successful! draft-cli is now live at version $NEW_VERSION."
echo "🔗 Verify with: clawhub inspect draft-cli"
