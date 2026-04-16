#!/usr/bin/env bash
set -euo pipefail

# publish_all_clawhub.sh
# Automates Phase 1 (Preparation) and Phase 2 (Publication) for Draft skills.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATE_SCRIPT="$REPO_ROOT/scripts/gate"

echo "🚀 Starting publication process for Draft skills..."

# 1. Validation
echo "🔍 Running local validation gates..."
if ! "$GATE_SCRIPT"; then
    echo "❌ Validation failed. Aborting publication."
    exit 1
fi

# 2. Version Management (SSOT: package.json)
CURRENT_VERSION=$(node -p "require('./package.json').version")
echo "📦 Current version from package.json: $CURRENT_VERSION"

# 3. Commit Changes (if needed)
if [[ -n "$(git status --porcelain package.json)" ]]; then
    echo "💾 Committing version updates..."
    git add package.json
    git commit -m "chore(release): bump version to $CURRENT_VERSION"
fi

# 4. Publication
SKILLS=(
  "draft-cli"
  "draft-agent-loop"
)

for SKILL in "${SKILLS[@]}"; do
  echo "☁️ Publishing $SKILL to ClawHub..."
  
  # Determine name from slug (kebab-case to Title Case)
  # draft-cli -> Draft CLI, draft-agent-loop -> Draft Agent Loop
  SKILL_NAME=$(echo "$SKILL" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')
  
  clawhub publish "$REPO_ROOT/skills/$SKILL" \
    --slug "$SKILL" \
    --name "$SKILL_NAME" \
    --version "$CURRENT_VERSION" \
    --tags latest
    
  echo "✅ $SKILL is now live at version $CURRENT_VERSION."
done

echo "🎉 All skills published successfully!"
echo "🔗 Verify with: clawhub inspect <slug>"
