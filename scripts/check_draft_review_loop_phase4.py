#!/usr/bin/env python3
"""Phase 4 workflow-level regression guard for draft-review-loop."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_SKILL_PATH = REPO_ROOT / "skills" / "draft-review-loop" / "SKILL.md"
README_PATH = REPO_ROOT / "README.md"
EVALS_PATH = REPO_ROOT / "evals" / "evals.json"
REGRESSION_FIXTURES_PATH = REPO_ROOT / "evals" / "regression_phase3.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fixture_has_skill_trigger(
    fixture: dict[str, Any], *, skill: str, expected: str
) -> bool:
    for assertion in fixture.get("assertions", []):
        if (
            assertion.get("type") == "trigger_decision_for_skill"
            and assertion.get("skill") == skill
            and assertion.get("expected") == expected
        ):
            return True
    return False


def main() -> int:
    failures: list[str] = []

    skill_text = REVIEW_SKILL_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")
    evals = load_json(EVALS_PATH).get("evals", [])
    eval_by_name = {entry["name"]: entry for entry in evals}
    fixtures = load_json(REGRESSION_FIXTURES_PATH).get("fixtures", [])
    fixture_by_id = {entry.get("id", ""): entry for entry in fixtures}

    required_skill_tokens = [
        "Do not trigger this skill when:",
        "the user only asks how to run Draft commands",
        "the user uses \"draft\" only as a verb for generic writing",
        "Source of truth: local workspace markdown file.",
        "draft open <path> --json",
        "draft comments list <path> --json",
        "Do not imply fully headless live collaboration.",
    ]
    for token in required_skill_tokens:
        if token not in skill_text:
            failures.append(f"draft-review-loop skill is missing required guidance token: {token}")

    required_phase5_skill_tokens = [
        "## Reusable Handoff Templates",
        "## Example Patterns",
        "### Proposal Review (Trigger: yes)",
        "### Spec Review (Trigger: yes)",
        "### Release Notes Review (Trigger: yes)",
        "### Non-Trigger Contrast (Trigger: no)",
        "## Full Loop Example (Draft To Comment Resolution)",
        "I wrote `<path>` locally (source of truth) and opened it in Draft for your review.",
        "Please review in Draft and leave comments there; I will update the local markdown file from accepted feedback.",
        "I read the Draft comments for `<path>` and applied the accepted changes to the workspace file.",
    ]
    for token in required_phase5_skill_tokens:
        if token not in skill_text:
            failures.append(
                f"draft-review-loop skill is missing required Phase 5 examples/templates token: {token}"
            )

    required_phase5_readme_tokens = [
        "## Review Handoff Examples",
        "Proposal review:",
        "Spec review:",
        "Release-note review:",
        "Always keep local markdown as the source of truth.",
    ]
    for token in required_phase5_readme_tokens:
        if token not in readme_text:
            failures.append(
                f"README is missing required Phase 5 handoff-example token: {token}"
            )

    required_evals = {
        "workflow-write-design-doc-open-handoff": [
            "local markdown file",
            "draft open <path> --json",
            "invites the human to review in Draft",
        ],
        "workflow-release-notes-local-review-handoff": [
            "local markdown file",
            "draft open <path> --json",
            "asks the human to review in Draft",
        ],
        "workflow-apply-comments-back-to-local-file": [
            "draft comments list <path|document_id> --json",
            "local file",
            "instead of defaulting to draft patch",
        ],
        "workflow-source-of-truth-local-markdown": [
            "local-first model",
            "source of truth",
            "avoid implying fully headless live collaboration",
        ],
    }

    for eval_name, expected_tokens in required_evals.items():
        eval_entry = eval_by_name.get(eval_name)
        if eval_entry is None:
            failures.append(f"Missing workflow eval fixture '{eval_name}' in evals.json")
            continue
        expected_output = str(eval_entry.get("expected_output", ""))
        for token in expected_tokens:
            if token not in expected_output:
                failures.append(
                    f"Workflow eval '{eval_name}' expected_output missing token: {token}"
                )

    required_fixture_expectations = [
        ("phase4-review-loop-trigger-design-doc", "draft-review-loop", "activate"),
        ("phase4-review-loop-trigger-apply-comments-local", "draft-review-loop", "activate"),
        ("phase4-review-loop-nontrigger-command-only", "draft-review-loop", "decline"),
        ("phase4-review-loop-nontrigger-generic-draft-verb", "draft-review-loop", "decline"),
    ]

    for fixture_id, skill, expected in required_fixture_expectations:
        fixture = fixture_by_id.get(fixture_id)
        if fixture is None:
            failures.append(f"Missing workflow regression fixture '{fixture_id}'")
            continue
        if not fixture_has_skill_trigger(fixture, skill=skill, expected=expected):
            failures.append(
                f"Fixture '{fixture_id}' must declare trigger_decision_for_skill for {skill}={expected}"
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
