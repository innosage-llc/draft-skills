#!/usr/bin/env bash
set -uo pipefail
# Note: -e is intentionally omitted so we can handle per-skill failures gracefully.

# publish_all_clawhub.sh
# Automates Phase 1 (Preparation) and Phase 2 (Publication) for Draft skills.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATE_SCRIPT="$REPO_ROOT/scripts/gate"

echo "🚀 Starting publication process for Draft skills..."

# Dependency check
if ! command -v node &>/dev/null; then
  echo "❌ Error: 'node' is not installed or not in PATH. Aborting."
  exit 1
fi

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

FAILED_SKILLS=()
WARNED_SKILLS=()

for SKILL in "${SKILLS[@]}"; do
  echo "☁️ Publishing $SKILL to ClawHub..."

  # Determine name from slug (kebab-case to Title Case)
  # draft-cli -> Draft CLI, draft-agent-loop -> Draft Agent Loop
  SKILL_NAME=$(echo "$SKILL" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')

  PUBLISH_OUTPUT=$(clawhub publish "$REPO_ROOT/skills/$SKILL" \
    --slug "$SKILL" \
    --name "$SKILL_NAME" \
    --version "$CURRENT_VERSION" \
    --tags latest 2>&1)
  PUBLISH_EXIT=$?

  if [[ $PUBLISH_EXIT -eq 0 ]]; then
    echo "✅ $SKILL is now live at version $CURRENT_VERSION."
  elif echo "$PUBLISH_OUTPUT" | grep -qi "already exist\|version conflict\|duplicate"; then
    echo "⚠️  Warning: $SKILL@$CURRENT_VERSION already published. Skipping."
    WARNED_SKILLS+=("$SKILL")
  else
    echo "❌ Error: Failed to publish $SKILL. Details:"
    echo "   $PUBLISH_OUTPUT"
    FAILED_SKILLS+=("$SKILL")
  fi
done

# 5. Summary
echo ""
if [[ ${#FAILED_SKILLS[@]} -gt 0 ]]; then
  echo "❌ Publication finished with errors:"
  for S in "${FAILED_SKILLS[@]}"; do echo "   - $S (FAILED)"; done
  [[ ${#WARNED_SKILLS[@]} -gt 0 ]] && for S in "${WARNED_SKILLS[@]}"; do echo "   - $S (already published, skipped)"; done
  exit 1
elif [[ ${#WARNED_SKILLS[@]} -gt 0 ]]; then
  echo "⚠️  Publication finished with warnings (some skills already published):"
  for S in "${WARNED_SKILLS[@]}"; do echo "   - $S"; done
else
  echo "🎉 All skills published successfully!"
fi
echo "🔗 Verify with: clawhub inspect <slug>"
