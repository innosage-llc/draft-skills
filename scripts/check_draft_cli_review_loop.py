#!/usr/bin/env python3
"""Guard the markdown-first Draft review loop against skill/eval drift."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "skills" / "draft-cli" / "SKILL.md"
EVALS_PATH = REPO_ROOT / "evals" / "evals.json"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    failures: list[str] = []
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    evals = load_json(EVALS_PATH).get("evals", [])
    eval_by_name = {entry["name"]: entry for entry in evals}

    required_skill_phrases = [
        "Use `draft cat <id>` when you want the page content in plain markdown for human review.",
        "Use `draft cat <id> --format json` only when you need the raw structured document data for parsing or automation.",
    ]
    for phrase in required_skill_phrases:
        if phrase not in skill_text:
            failures.append(f"Missing shared skill guidance: {phrase}")

    review_eval = eval_by_name.get("list-and-cat-with-connection-check")
    if review_eval is None:
        failures.append("Missing eval 'list-and-cat-with-connection-check'.")
    else:
        expected_output = review_eval.get("expected_output", "")
        expectations = review_eval.get("expectations", [])

        if "draft cat <id> to return the page in markdown for review" not in expected_output:
            failures.append(
                "Review-loop eval expected_output must describe `draft cat <id>` returning markdown."
            )
        if "--format json" in expected_output:
            failures.append(
                "Review-loop eval expected_output must not send human review back through `--format json`."
            )
        if "Agent reads a specific page with draft cat <id> for markdown review" not in expectations:
            failures.append(
                "Review-loop eval expectations must require `draft cat <id>` for markdown review."
            )
        if any("--format json" in item for item in expectations):
            failures.append(
                "Review-loop eval expectations must not require `draft cat <id> --format json`."
            )

    if failures:
        print("draft-cli review-loop regression check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("draft-cli review-loop regression check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
