#!/usr/bin/env python3
"""Deterministic Phase 2 local smoke gate for draft-cli."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "skills" / "draft-cli" / "SKILL.md"
EVALS_PATH = REPO_ROOT / "evals" / "evals.json"
SMOKE_FIXTURES_PATH = REPO_ROOT / "evals" / "smoke_phase2.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def classify_prompt(prompt: str) -> str:
    text = prompt.lower()

    non_trigger_patterns = [
        r"\bdraft an email\b",
        r"\bdraft a response\b",
        r"\bdraft\.md\b",
        r"\binvestor_update_draft\.md\b",
    ]
    if any(re.search(pattern, text) for pattern in non_trigger_patterns):
        return "decline"

    mentions_draft_product = any(
        token in text
        for token in (
            "draft cli",
            "draft page",
            "draft doc",
            "draft workspace",
            "pages",
        )
    )
    mentions_operation = any(
        token in text
        for token in (
            "list",
            "show",
            "read",
            "create",
            "append",
            "patch",
            "replace",
            "publish",
            "content",
        )
    )
    if "draft" in text and mentions_draft_product and mentions_operation:
        return "activate"

    return "defer"


def resolve_target(target: str, skill_text: str, eval_by_name: dict[str, dict[str, Any]]) -> str:
    if target == "skill":
        return skill_text

    parts = target.split(":")
    if len(parts) != 3 or parts[0] != "eval":
        raise ValueError(f"Unsupported target: {target}")

    eval_name = parts[1]
    field = parts[2]
    eval_entry = eval_by_name.get(eval_name)
    if eval_entry is None:
        raise KeyError(f"Missing eval '{eval_name}'")

    value = eval_entry.get(field, "")
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    return str(value)


def ensure_tokens_in_text(text: str, tokens: list[str], *, ordered: bool) -> bool:
    if not ordered:
        return all(token in text for token in tokens)

    start = 0
    for token in tokens:
        idx = text.find(token, start)
        if idx == -1:
            return False
        start = idx + len(token)
    return True


def run_fixture(
    fixture: dict[str, Any], skill_text: str, eval_by_name: dict[str, dict[str, Any]]
) -> list[str]:
    failures: list[str] = []
    fixture_id = fixture.get("id", "<unknown>")

    prompt = str(fixture.get("prompt", ""))
    for assertion in fixture.get("assertions", []):
        assertion_type = assertion.get("type")

        if assertion_type == "trigger_decision":
            expected = str(assertion.get("expected", ""))
            actual = classify_prompt(prompt)
            if actual != expected:
                failures.append(
                    f"{fixture_id}: trigger_decision expected '{expected}', got '{actual}'"
                )
            continue

        if assertion_type == "artifact_exists":
            artifact_path = str(assertion.get("path", ""))
            if artifact_path.startswith("eval:"):
                eval_name = artifact_path.split(":", 1)[1]
                if eval_name not in eval_by_name:
                    failures.append(
                        f"{fixture_id}: missing required eval artifact '{eval_name}'"
                    )
            else:
                path = REPO_ROOT / artifact_path
                if not path.exists():
                    failures.append(f"{fixture_id}: missing required artifact '{artifact_path}'")
            continue

        if assertion_type == "command_sequence":
            target = str(assertion.get("target", ""))
            sequence = [str(item) for item in assertion.get("sequence", [])]
            try:
                text = resolve_target(target, skill_text, eval_by_name)
            except (KeyError, ValueError) as exc:
                failures.append(f"{fixture_id}: {exc}")
                continue
            if not ensure_tokens_in_text(text, sequence, ordered=True):
                failures.append(
                    f"{fixture_id}: command_sequence failed for target '{target}' with sequence {sequence}"
                )
            continue

        if assertion_type in {"command_contains", "text_contains"}:
            target = str(assertion.get("target", ""))
            tokens = [str(item) for item in assertion.get("tokens", [])]
            try:
                text = resolve_target(target, skill_text, eval_by_name)
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
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    evals = load_json(EVALS_PATH).get("evals", [])
    fixtures = load_json(SMOKE_FIXTURES_PATH).get("fixtures", [])
    eval_by_name = {entry["name"]: entry for entry in evals}

    failures: list[str] = []
    for fixture in fixtures:
        failures.extend(run_fixture(fixture, skill_text, eval_by_name))

    if failures:
        print("draft-cli Phase 2 smoke check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "draft-cli Phase 2 smoke check passed: trigger/non-trigger coverage and deterministic command-shape assertions are satisfied."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
