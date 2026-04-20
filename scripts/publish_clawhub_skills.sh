#!/usr/bin/env bash
set -uo pipefail
# Note: -e is intentionally omitted so we can handle per-skill failures gracefully.

# publish_clawhub_skills.sh
# Automates Phase 1 (Preparation) and Phase 2 (Publication) for ClawHub-published Draft skills.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATE_SCRIPT="$REPO_ROOT/scripts/gate"

echo "🚀 Starting publication process for Draft skills..."

# Dependency check
if ! command -v node &>/dev/null; then
  echo "❌ Error: 'node' is not installed or not in PATH. Aborting."
  exit 1
fi

# ======= SKIP due to workspace deprecation  ===========
# # 1. Validation
# echo "🔍 Running local validation gates..."
# if ! "$GATE_SCRIPT"; then
#     echo "❌ Validation failed. Aborting publication."
#     exit 1
# fi
# ======================================================

# 2. Commit Changes (if needed)
# SSOT: the version inside each skill's metadata json block in SKILL.md
if [[ -n "$(git status --porcelain package.json)" ]]; then
    CURRENT_VERSION=$(node -p "require('./package.json').version")
    echo "💾 Committing package.json version updates..."
    git add package.json
    git commit -m "chore(release): bump package version to $CURRENT_VERSION"
fi

# 3. Publication
SKILLS=(
  "draft-cli"
  "draft-headless-pages"
  "draft-agent-loop"
)

FAILED_SKILLS=()
WARNED_SKILLS=()

for SKILL in "${SKILLS[@]}"; do
  SKILL_FILE="$REPO_ROOT/skills/$SKILL/SKILL.md"
  
  if [[ ! -f "$SKILL_FILE" ]]; then
    echo "❌ Error: $SKILL_FILE not found. Skipping $SKILL."
    FAILED_SKILLS+=("$SKILL")
    continue
  fi

  # Extract version from YAML frontmatter: version: "x.y.z"
  SKILL_VERSION=$(grep "^version:" "$SKILL_FILE" | sed -n 's/version: "\(.*\)"/\1/p' | head -n 1)

  if [[ -z "$SKILL_VERSION" ]]; then
    echo "❌ Error: Could not extract version from $SKILL/SKILL.md. Skipping."
    FAILED_SKILLS+=("$SKILL")
    continue
  fi

  echo "☁️ Publishing $SKILL@$SKILL_VERSION to ClawHub..."

  # Determine name from slug (kebab-case to Title Case)
  SKILL_NAME=$(echo "$SKILL" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')

  PUBLISH_OUTPUT=$(clawhub publish "$REPO_ROOT/skills/$SKILL" \
    --slug "$SKILL" \
    --name "$SKILL_NAME" \
    --version "$SKILL_VERSION" \
    --tags latest 2>&1)
  PUBLISH_EXIT=$?

  if [[ $PUBLISH_EXIT -eq 0 ]]; then
    echo "✅ $SKILL is now live at version $SKILL_VERSION."
  elif echo "$PUBLISH_OUTPUT" | grep -qi "already exist\|version conflict\|duplicate"; then
    echo "⚠️  Warning: $SKILL@$SKILL_VERSION already published. Skipping."
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
