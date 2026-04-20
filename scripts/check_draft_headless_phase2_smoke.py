#!/usr/bin/env python3
"""Deterministic Phase 2 local smoke gate for draft-headless-pages."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from check_draft_cli_phase3_regression import classify_prompt_for_skill, ensure_tokens_in_text, resolve_target


REPO_ROOT = Path(__file__).resolve().parents[1]
EVALS_PATH = REPO_ROOT / "evals" / "evals.json"
SMOKE_FIXTURES_PATH = REPO_ROOT / "evals" / "smoke_headless_phase2.json"
SKILL_PATHS = {
    "draft-headless-pages": REPO_ROOT / "skills" / "draft-headless-pages" / "SKILL.md",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_fixture(
    fixture: dict[str, Any], skill_texts: dict[str, str], eval_by_name: dict[str, dict[str, Any]], evals: list[dict[str, Any]]
) -> list[str]:
    failures: list[str] = []
    fixture_id = fixture.get("id", "<unknown>")
    prompt = str(fixture.get("prompt", ""))

    for assertion in fixture.get("assertions", []):
        assertion_type = assertion.get("type")

        if assertion_type == "trigger_decision_for_skill":
            skill_name = str(assertion.get("skill", ""))
            expected = str(assertion.get("expected", ""))
            actual = classify_prompt_for_skill(skill_name, prompt)
            if actual != expected:
                failures.append(
                    f"{fixture_id}: trigger_decision_for_skill '{skill_name}' expected '{expected}', got '{actual}'"
                )
            continue

        if assertion_type == "artifact_exists":
            artifact_path = str(assertion.get("path", ""))
            if artifact_path.startswith("eval:"):
                eval_name = artifact_path.split(":", 1)[1]
                if eval_name not in eval_by_name:
                    failures.append(f"{fixture_id}: missing required eval artifact '{eval_name}'")
            else:
                path = REPO_ROOT / artifact_path
                if not path.exists():
                    failures.append(f"{fixture_id}: missing required artifact '{artifact_path}'")
            continue

        if assertion_type in {"command_contains", "text_contains"}:
            target = str(assertion.get("target", ""))
            tokens = [str(item) for item in assertion.get("tokens", [])]
            try:
                text = resolve_target(target, skill_texts, eval_by_name, evals)
            except (KeyError, ValueError) as exc:
                failures.append(f"{fixture_id}: {exc}")
                continue
            if not ensure_tokens_in_text(text, tokens, ordered=False):
                failures.append(
                    f"{fixture_id}: {assertion_type} failed for target '{target}' with tokens {tokens}"
                )
            continue

        failures.append(f"{fixture_id}: unsupported assertion type '{assertion_type}'")

    return failures


def main() -> int:
    evals = load_json(EVALS_PATH).get("evals", [])
    fixtures = load_json(SMOKE_FIXTURES_PATH).get("fixtures", [])
    eval_by_name = {entry["name"]: entry for entry in evals}
    skill_texts = {name: path.read_text(encoding="utf-8") for name, path in SKILL_PATHS.items()}

    failures: list[str] = []
    for fixture in fixtures:
        failures.extend(run_fixture(fixture, skill_texts, eval_by_name, evals))

    if failures:
        print("draft-headless-pages Phase 2 smoke check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "draft-headless-pages Phase 2 smoke check passed: trigger/non-trigger coverage and deterministic headless command-shape assertions are satisfied."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
