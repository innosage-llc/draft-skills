#!/usr/bin/env python3
"""Guard draft-cli/readme alignment for the headless-only Draft contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "skills" / "draft-cli" / "SKILL.md"
README_PATH = REPO_ROOT / "README.md"
EVALS_PATH = REPO_ROOT / "evals" / "evals.json"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    failures: list[str] = []
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")
    evals = load_json(EVALS_PATH).get("evals", [])
    eval_by_name = {entry["name"]: entry for entry in evals}

    required_skill_tokens = [
        "draft start-server",
        "draft status --json",
        "draft page ls --json",
        "draft page cat <page_id> --json",
    ]
    for token in required_skill_tokens:
        if token not in skill_text:
            failures.append(f"draft-cli skill is missing token: {token}")

    forbidden_skill_tokens = [
        "draft daemon",
        "draft workspace ...",
        "draft open <path>",
        "draft public-comments ...",
        "v1_DEPRECATED",
        "--mode workspace",
    ]
    for token in forbidden_skill_tokens:
        if token in skill_text:
            failures.append(f"draft-cli skill includes removed command guidance token: {token}")

    required_readme_tokens = [
        "headless v2",
        "draft daemon",
        "draft public-comments ...",
        "draft-review-loop",
    ]
    for token in required_readme_tokens:
        if token not in readme_text:
            failures.append(f"README is missing token: {token}")

    review_eval = eval_by_name.get("list-and-cat-with-connection-check")
    if review_eval is None:
        failures.append("Missing eval 'list-and-cat-with-connection-check'.")
    else:
        expected_output = str(review_eval.get("expected_output", ""))
        expectations = review_eval.get("expectations", [])
        if "draft page cat <id>" not in expected_output:
            failures.append("Review eval expected_output must describe draft page cat markdown review.")
        if "Agent reads a specific page with draft page cat <id> for markdown review" not in expectations:
            failures.append("Review eval expectations must require page-cat markdown review behavior.")

    if failures:
        print("draft-cli review-loop regression check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("draft-cli review-loop regression check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
