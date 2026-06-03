#!/usr/bin/env python3
"""Phase 4 guard for the retired draft-review-loop skill."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_SKILL_PATH = REPO_ROOT / "skills" / "draft-review-loop" / "SKILL.md"
README_PATH = REPO_ROOT / "README.md"
REGRESSION_FIXTURES_PATH = REPO_ROOT / "evals" / "regression_phase3.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fixture_has_retired_decline(fixture: dict[str, Any]) -> bool:
    for assertion in fixture.get("assertions", []):
        if (
            assertion.get("type") == "trigger_decision_for_skill"
            and assertion.get("skill") == "draft-review-loop"
            and assertion.get("expected") == "decline"
        ):
            return True
    return False


def main() -> int:
    failures: list[str] = []

    skill_text = REVIEW_SKILL_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")
    fixtures = load_json(REGRESSION_FIXTURES_PATH).get("fixtures", [])
    fixture_by_id = {entry.get("id", ""): entry for entry in fixtures}

    required_skill_tokens = [
      "This workflow is retired",
      "edit the local file directly with normal repository tools",
      "use `draft-cli` and the headless `draft page ...` command surface"
    ]
    for token in required_skill_tokens:
        if token not in skill_text:
            failures.append(f"draft-review-loop skill is missing token: {token}")

    if "draft-review-loop" not in readme_text or "Retired workflow note" not in readme_text:
        failures.append("README must describe draft-review-loop as retired.")

    fixture = fixture_by_id.get("phase4-review-loop-retired")
    if fixture is None:
        failures.append("Missing regression fixture 'phase4-review-loop-retired'.")
    elif not fixture_has_retired_decline(fixture):
        failures.append(
            "Fixture 'phase4-review-loop-retired' must declare draft-review-loop=decline."
        )

    if failures:
        print("draft-review-loop Phase 4 workflow regression check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("draft-review-loop Phase 4 workflow regression check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
