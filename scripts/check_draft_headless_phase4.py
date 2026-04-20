#!/usr/bin/env python3
"""Phase 4 contract guard for draft-headless-pages."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "skills" / "draft-headless-pages" / "SKILL.md"
README_PATH = REPO_ROOT / "README.md"
EVALS_PATH = REPO_ROOT / "evals" / "evals.json"
REGRESSION_FIXTURES_PATH = REPO_ROOT / "evals" / "regression_phase3.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fixture_has_skill_trigger(fixture: dict[str, Any], *, skill: str, expected: str) -> bool:
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

    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")
    evals = load_json(EVALS_PATH).get("evals", [])
    eval_by_name = {entry["name"]: entry for entry in evals}
    fixtures = load_json(REGRESSION_FIXTURES_PATH).get("fixtures", [])
    fixture_by_id = {entry.get("id", ""): entry for entry in fixtures}

    required_skill_tokens = [
        "For OpenClaw and other remote-agent environments, this should be the default Draft runtime skill.",
        "## Use This Skill When",
        "## Do Not Use This Skill When",
        "draft start-server --runtime v2",
        "draft public-comments list --url '<published_or_preview_url>' --json",
        "Do not start with `draft status`.",
        "## Trigger Prompt Examples",
        "My OpenClaw agent is running in Docker.",
        "Read public comments from this published Draft preview URL",
    ]
    for token in required_skill_tokens:
        if token not in skill_text:
            failures.append(f"draft-headless-pages skill is missing required guidance token: {token}")

    required_readme_tokens = [
        "Remote OpenClaw agent, Docker, CI, Linux worker, isolated runtime",
        "[draft-headless-pages](skills/draft-headless-pages)",
        "default Draft runtime skill for OpenClaw-style isolated environments",
    ]
    for token in required_readme_tokens:
        if token not in readme_text:
            failures.append(f"README is missing required headless taxonomy token: {token}")

    required_evals = {
        "headless-create-publish-review": [
            "draft start-server --runtime v2",
            "draft status --json",
            "draft page create 'Release Plan' --json",
            "draft page publish <page_id> --json",
        ],
        "headless-public-comments-url-read": [
            "does not begin with draft status",
            "does not require draft start-server",
            "draft public-comments list --url '<published_or_preview_url>' --json",
        ],
        "headless-page-annotate-and-comments": [
            "draft page annotate <page_id>",
            "draft page comments <page_id> --json",
        ],
    }

    for eval_name, expected_tokens in required_evals.items():
        eval_entry = eval_by_name.get(eval_name)
        if eval_entry is None:
            failures.append(f"Missing headless eval fixture '{eval_name}' in evals.json")
            continue
        expected_output = str(eval_entry.get("expected_output", ""))
        for token in expected_tokens:
            if token not in expected_output:
                failures.append(
                    f"Headless eval '{eval_name}' expected_output missing token: {token}"
                )

    required_fixture_expectations = [
        ("phase4-headless-trigger-remote-create-publish", "draft-headless-pages", "activate"),
        ("phase4-headless-trigger-public-comments-url", "draft-headless-pages", "activate"),
        ("phase4-headless-nontrigger-local-review-loop", "draft-headless-pages", "decline"),
        ("phase4-headless-nontrigger-hitrl-workflow", "draft-headless-pages", "decline"),
    ]

    for fixture_id, skill, expected in required_fixture_expectations:
        fixture = fixture_by_id.get(fixture_id)
        if fixture is None:
            failures.append(f"Missing headless regression fixture '{fixture_id}'")
            continue
        if not fixture_has_skill_trigger(fixture, skill=skill, expected=expected):
            failures.append(
                f"Fixture '{fixture_id}' must declare trigger_decision_for_skill for {skill}={expected}"
            )

    if failures:
        print("draft-headless-pages Phase 4 contract check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("draft-headless-pages Phase 4 contract check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
