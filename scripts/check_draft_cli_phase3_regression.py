#!/usr/bin/env python3
"""Phase 3 regression corpus runner for draft-cli.

Phase 3.1 goals:
- Enforce fixture contract fields relevant to current corpus execution.
- Keep local regression semantics aligned with future CI use.
- Remove Phase 3-only shortcuts that can drift in CI promotion.
"""

from __future__ import annotations

import argparse
import json
import statistics
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATHS = {
    "draft-cli": REPO_ROOT / "skills" / "draft-cli" / "SKILL.md",
    "draft-review-loop": REPO_ROOT / "skills" / "draft-review-loop" / "SKILL.md",
}
EVALS_PATH = REPO_ROOT / "evals" / "evals.json"
REGRESSION_FIXTURES_PATH = REPO_ROOT / "evals" / "regression_phase3.json"
ALLOWED_SCENARIO_CLASSES = {"hard-pass", "scored", "informational"}
ALLOWED_SCOPES = {"local-structural", "local-smoke", "regression", "ci-promotion"}
ALLOWED_NONDETERMINISM_MODES = {"deterministic", "retryable", "drifted"}


@dataclass
class FixtureRun:
    fixture_id: str
    scenario_class: str
    blocking_failures: list[str]
    informational_failures: list[str]
    notes: list[str]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def classify_draft_cli_prompt(prompt: str) -> str:
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
            "draft",
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
            "command",
            "status",
            "fix",
            "recover",
        )
    )
    if mentions_draft_product and mentions_operation:
        return "activate"

    return "defer"


def classify_draft_review_loop_prompt(prompt: str) -> str:
    text = prompt.lower()

    non_trigger_patterns = [
        r"\bdraft an email\b",
        r"\bdraft a response\b",
        r"\bdraft\.md\b",
        r"\binvestor_update_draft\.md\b",
    ]
    if any(re.search(pattern, text) for pattern in non_trigger_patterns):
        return "decline"

    if "draft" not in text:
        return "defer"

    pure_command_intent = any(
        token in text
        for token in (
            "how do i run",
            "what command",
            "command syntax",
            "usage of",
            "just the command",
        )
    ) and "review" not in text
    if pure_command_intent:
        return "decline"

    workflow_tokens = (
        "review in draft",
        "review surface",
        "open it in draft",
        "open in draft",
        "comments on",
        "review comments",
        "apply comments",
        "handoff",
    )
    local_first_tokens = (
        "local",
        "workspace",
        "repo",
        "markdown file",
        "source of truth",
        "design doc",
        "release notes",
        "proposal",
        "spec",
        "revise",
        "update the file",
    )
    has_workflow_token = any(token in text for token in workflow_tokens)
    has_local_first_token = any(token in text for token in local_first_tokens)
    if has_workflow_token and has_local_first_token:
        return "activate"
    if "review" in text and has_local_first_token:
        return "activate"

    return "defer"


def classify_prompt_for_skill(skill_name: str, prompt: str) -> str:
    if skill_name == "draft-cli":
        return classify_draft_cli_prompt(prompt)
    if skill_name == "draft-review-loop":
        return classify_draft_review_loop_prompt(prompt)
    raise ValueError(f"Unsupported skill classifier '{skill_name}'")


def load_skill_texts() -> dict[str, str]:
    return {name: path.read_text(encoding="utf-8") for name, path in SKILL_PATHS.items()}


def resolve_target(
    target: str, skill_texts: dict[str, str], eval_by_name: dict[str, dict[str, Any]], evals: list[dict[str, Any]]
) -> str:
    if target == "skill":
        return skill_texts["draft-cli"]
    if target.startswith("skill:"):
        skill_name = target.split(":", 1)[1]
        skill_text = skill_texts.get(skill_name)
        if skill_text is None:
            raise ValueError(f"Unsupported skill target: {target}")
        return skill_text
    if target == "evals":
        return str(len(evals))

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


def read_numeric_target(
    target: str, skill_texts: dict[str, str], eval_by_name: dict[str, dict[str, Any]], evals: list[dict[str, Any]]
) -> float:
    text = resolve_target(target, skill_texts, eval_by_name, evals).strip()
    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(f"Target '{target}' is not numeric: {text!r}") from exc


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


def validate_fixture_contract(fixture: dict[str, Any], *, allowed_scopes: set[str]) -> list[str]:
    errors: list[str] = []
    fixture_id = str(fixture.get("id", "<unknown>"))
    title = fixture.get("title")
    scenario_class = fixture.get("scenario_class")
    scope = fixture.get("scope")
    prompt = fixture.get("prompt")
    assertions = fixture.get("assertions")
    nondeterminism = fixture.get("nondeterminism")

    if not title or not isinstance(title, str):
        errors.append(f"{fixture_id}: missing or invalid 'title'")
    if scenario_class not in ALLOWED_SCENARIO_CLASSES:
        errors.append(
            f"{fixture_id}: scenario_class must be one of {sorted(ALLOWED_SCENARIO_CLASSES)}, got {scenario_class!r}"
        )
    if scope not in ALLOWED_SCOPES:
        errors.append(f"{fixture_id}: scope must be one of {sorted(ALLOWED_SCOPES)}, got {scope!r}")
    elif scope not in allowed_scopes:
        errors.append(f"{fixture_id}: scope '{scope}' is not enabled for this run")
    if not isinstance(prompt, str):
        errors.append(f"{fixture_id}: missing or invalid 'prompt'")
    if not isinstance(assertions, list) or not assertions:
        errors.append(f"{fixture_id}: assertions must be a non-empty list")
    if not isinstance(nondeterminism, dict):
        errors.append(f"{fixture_id}: missing or invalid 'nondeterminism' block")
        return errors

    mode = nondeterminism.get("mode")
    reruns = nondeterminism.get("reruns", 1)
    if mode not in ALLOWED_NONDETERMINISM_MODES:
        errors.append(
            f"{fixture_id}: nondeterminism.mode must be one of {sorted(ALLOWED_NONDETERMINISM_MODES)}, got {mode!r}"
        )
    if not isinstance(reruns, int) or reruns < 1:
        errors.append(f"{fixture_id}: nondeterminism.reruns must be an integer >= 1")
        return errors

    if mode == "deterministic" and reruns != 1:
        errors.append(f"{fixture_id}: deterministic fixtures must declare reruns=1")
    if mode == "retryable" and reruns > 3:
        errors.append(f"{fixture_id}: retryable fixtures must declare reruns <= 3")
    if mode == "drifted" and reruns not in {3, 5}:
        errors.append(f"{fixture_id}: drifted fixtures must declare reruns of 3 or 5")
    return errors


def count_regression_fixtures(fixtures: list[dict[str, Any]], *, tag: str | None = None) -> int:
    if tag is None:
        return len(fixtures)
    return sum(1 for fixture in fixtures if tag in fixture.get("tags", []))


def run_fixture_once(
    fixture: dict[str, Any],
    skill_texts: dict[str, str],
    eval_by_name: dict[str, dict[str, Any]],
    evals: list[dict[str, Any]],
    scoped_fixtures: list[dict[str, Any]],
) -> list[str]:
    failures: list[str] = []
    fixture_id = fixture.get("id", "<unknown>")
    prompt = str(fixture.get("prompt", ""))

    for assertion in fixture.get("assertions", []):
        assertion_type = assertion.get("type")

        if assertion_type == "trigger_decision":
            expected = str(assertion.get("expected", ""))
            actual = classify_prompt_for_skill("draft-cli", prompt)
            if actual != expected:
                failures.append(
                    f"{fixture_id}: trigger_decision expected '{expected}', got '{actual}'"
                )
            continue

        if assertion_type == "trigger_decision_for_skill":
            skill_name = str(assertion.get("skill", ""))
            expected = str(assertion.get("expected", ""))
            if not skill_name:
                failures.append(f"{fixture_id}: trigger_decision_for_skill missing 'skill'")
                continue
            try:
                actual = classify_prompt_for_skill(skill_name, prompt)
            except ValueError as exc:
                failures.append(f"{fixture_id}: {exc}")
                continue
            if actual != expected:
                failures.append(
                    f"{fixture_id}: trigger_decision_for_skill '{skill_name}' expected '{expected}', got '{actual}'"
                )
            continue

        if assertion_type == "artifact_exists":
            artifact_path_value = assertion.get("path")
            if not artifact_path_value:
                failures.append(f"{fixture_id}: artifact_exists assertion missing 'path'")
                continue
            artifact_path = str(artifact_path_value)
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
                text = resolve_target(target, skill_texts, eval_by_name, evals)
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
                text = resolve_target(target, skill_texts, eval_by_name, evals)
            except (KeyError, ValueError) as exc:
                failures.append(f"{fixture_id}: {exc}")
                continue
            if not ensure_tokens_in_text(text, tokens, ordered=False):
                failures.append(
                    f"{fixture_id}: {assertion_type} failed for target '{target}' with tokens {tokens}"
                )
            continue

        if assertion_type == "count_at_least":
            target = str(assertion.get("target", ""))
            minimum = int(assertion.get("minimum", 0))
            tag = assertion.get("tag")
            if tag is not None:
                tag = str(tag)

            if target == "regression_fixtures":
                actual = count_regression_fixtures(scoped_fixtures, tag=tag)
            elif target == "evals":
                # Backward-compatible legacy target; Phase 3.1 fixtures should use regression_fixtures.
                actual = len(evals)
            else:
                failures.append(f"{fixture_id}: unsupported count target '{target}'")
                continue
            if actual < minimum:
                failures.append(f"{fixture_id}: count_at_least expected {minimum}, got {actual}")
            continue

        if assertion_type == "score_within":
            target = str(assertion.get("target", ""))
            try:
                current = read_numeric_target(target, skill_texts, eval_by_name, evals)
            except ValueError as exc:
                failures.append(f"{fixture_id}: {exc}")
                continue

            if "min" in assertion or "max" in assertion:
                minimum = assertion.get("min")
                maximum = assertion.get("max")
                if minimum is not None and current < float(minimum):
                    failures.append(f"{fixture_id}: score_within expected >= {minimum}, got {current}")
                if maximum is not None and current > float(maximum):
                    failures.append(f"{fixture_id}: score_within expected <= {maximum}, got {current}")
                continue

            baseline = assertion.get("baseline")
            max_delta = assertion.get("max_delta")
            if baseline is None and isinstance(fixture.get("baseline"), (int, float)):
                baseline = fixture["baseline"]
            if baseline is None or max_delta is None:
                failures.append(
                    f"{fixture_id}: score_within requires min/max bounds or baseline+max_delta"
                )
                continue
            if abs(current - float(baseline)) > float(max_delta):
                failures.append(
                    f"{fixture_id}: score_within drift exceeded; current={current}, baseline={baseline}, max_delta={max_delta}"
                )
            continue

        failures.append(f"{fixture_id}: unsupported assertion type '{assertion_type}'")

    return failures


def run_fixture_with_policy(
    fixture: dict[str, Any],
    skill_texts: dict[str, str],
    eval_by_name: dict[str, dict[str, Any]],
    evals: list[dict[str, Any]],
    scoped_fixtures: list[dict[str, Any]],
) -> FixtureRun:
    fixture_id = str(fixture.get("id", "<unknown>"))
    scenario_class = str(fixture.get("scenario_class", "hard-pass"))
    nondeterminism = fixture.get("nondeterminism", {})
    mode = nondeterminism.get("mode", "deterministic")
    reruns = int(nondeterminism.get("reruns", 1))
    notes: list[str] = []

    if scenario_class == "scored":
        notes.append(
            f"{fixture_id}: scored scenario parsed for contract compatibility; use score_within assertions to make it blocking."
        )

    attempts: list[list[str]] = []
    for _ in range(reruns):
        failures = run_fixture_once(
            fixture=fixture,
            skill_texts=skill_texts,
            eval_by_name=eval_by_name,
            evals=evals,
            scoped_fixtures=scoped_fixtures,
        )
        attempts.append(failures)

        if mode == "deterministic":
            break
        if mode == "retryable" and not failures:
            break

    attempt_failures: list[str] = attempts[-1] if attempts else []
    if mode == "drifted":
        # For drifted checks, assertions should usually be score_within and aggregate-friendly.
        # Current Phase 3 corpus is deterministic; this path remains forward-compatible.
        median_failures_count = int(statistics.median(len(run) for run in attempts)) if attempts else 0
        if median_failures_count > 0:
            attempt_failures = next((run for run in attempts if run), attempts[-1])
        else:
            attempt_failures = []

    if scenario_class == "informational":
        return FixtureRun(
            fixture_id=fixture_id,
            scenario_class=scenario_class,
            blocking_failures=[],
            informational_failures=attempt_failures,
            notes=notes,
        )

    return FixtureRun(
        fixture_id=fixture_id,
        scenario_class=scenario_class,
        blocking_failures=attempt_failures,
        informational_failures=[],
        notes=notes,
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run draft-cli Phase 3 regression fixtures with contract-aware semantics."
    )
    parser.add_argument(
        "--scopes",
        default="regression",
        help="Comma-separated fixture scopes to execute (default: regression).",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(sys.argv[1:])
    allowed_scopes = {part.strip() for part in args.scopes.split(",") if part.strip()}
    if not allowed_scopes:
        print("ERROR: --scopes must include at least one scope.")
        return 1

    skill_texts = load_skill_texts()
    evals = load_json(EVALS_PATH).get("evals", [])
    fixtures = load_json(REGRESSION_FIXTURES_PATH).get("fixtures", [])
    eval_by_name = {entry["name"]: entry for entry in evals}
    scoped_fixtures = [fixture for fixture in fixtures if fixture.get("scope") in allowed_scopes]

    failures: list[str] = []
    informational_failures: list[str] = []
    notes: list[str] = []

    invalid_fixture_ids: set[str] = set()
    for fixture in scoped_fixtures:
        fixture_id = str(fixture.get("id", "<unknown>"))
        contract_errors = validate_fixture_contract(fixture, allowed_scopes=allowed_scopes)
        if contract_errors:
            invalid_fixture_ids.add(fixture_id)
            failures.extend(contract_errors)

    for fixture in scoped_fixtures:
        if str(fixture.get("id", "<unknown>")) in invalid_fixture_ids:
            continue
        result = run_fixture_with_policy(
            fixture=fixture,
            skill_texts=skill_texts,
            eval_by_name=eval_by_name,
            evals=evals,
            scoped_fixtures=scoped_fixtures,
        )
        failures.extend(result.blocking_failures)
        informational_failures.extend(result.informational_failures)
        notes.extend(result.notes)

    if failures:
        print("draft-cli Phase 3 regression check failed (blocking fixtures):")
        for failure in failures:
            print(f"- {failure}")
        if informational_failures:
            print("informational fixture findings:")
            for failure in informational_failures:
                print(f"- {failure}")
        if notes:
            print("notes:")
            for note in notes:
                print(f"- {note}")
        return 1

    if informational_failures:
        print("informational fixture findings (non-blocking):")
        for failure in informational_failures:
            print(f"- {failure}")
    if notes:
        print("notes:")
        for note in notes:
            print(f"- {note}")
    print(
        "draft-cli Phase 3 regression check passed: contract-aware fixture semantics and corpus assertions are satisfied."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
