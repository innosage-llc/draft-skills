#!/usr/bin/env python3
"""Guard draft-cli/readme alignment for the JSON Workspace-first Draft contract."""

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
        "draft workspace status --json",
        "draft workspace path --json",
        "draft workspace set-path <folder> --json",
        "draft --workspace-json <folder> page ls --json",
        "draft --workspace-json <folder> page search \"phrase\" --json",
        "draft --workspace-json <folder> page cat <page_id> --json",
        "Agent-Native Read Guidance",
        "manual rendering from `pages/*.json`",
        "raw workspace JSON files as a last resort",
        "prefer `draft --workspace-json <folder> page search \"phrase\" --json`",
        "On older CLIs without page search, use `rg` over workspace page files only",
        "page body markdown only",
        "decorated human `page cat` output",
        "`page cat --json` block output",
        "`draft page insert-image` returns `local_id`",
    ]
    for token in required_skill_tokens:
        if token not in skill_text:
            failures.append(f"draft-cli skill is missing token: {token}")

    forbidden_skill_tokens = [
        "draft daemon",
        "draft open <path>",
        "draft public-comments ...",
        "v1_DEPRECATED",
        "--mode workspace",
    ]
    for token in forbidden_skill_tokens:
        if token in skill_text:
            failures.append(f"draft-cli skill includes removed command guidance token: {token}")

    required_readme_tokens = [
        "JSON Workspace",
        "`draft --workspace-json <folder>` remains the explicit override",
        "draft daemon",
        "draft public-comments ...",
    ]
    for token in required_readme_tokens:
        if token not in readme_text:
            failures.append(f"README is missing token: {token}")

    review_eval = eval_by_name.get("list-and-cat-with-default-workspace")
    if review_eval is None:
        failures.append("Missing eval 'list-and-cat-with-default-workspace'.")
    else:
        expected_output = str(review_eval.get("expected_output", ""))
        expectations = review_eval.get("expectations", [])
        if "draft workspace status --json" not in expected_output:
            failures.append("Review eval expected_output must describe workspace status checks.")
        if "draft --workspace-json <active_workspace_path> page cat <id>" not in expected_output:
            failures.append("Review eval expected_output must describe workspace-anchored draft page cat markdown review.")
        if "Agent reads a specific page with draft --workspace-json <active_workspace_path> page cat <id> for markdown review" not in expectations:
            failures.append("Review eval expectations must require page-cat markdown review behavior.")
        read_tokens = [
            "preferred agent-native rendered read surface",
            "page cat --json for structured automation only",
            "does not fall back to raw workspace JSON unless lower-level recovery or inspection is required",
        ]
        for token in read_tokens:
            if token not in expected_output:
                failures.append(f"Review eval expected_output is missing token: {token}")
        if "Agent prefers page cat markdown over raw workspace JSON for rendered page reads" not in expectations:
            failures.append("Review eval expectations must require page-cat markdown as the preferred rendered read surface.")

    patch_eval = eval_by_name.get("patch-json-workspace-body-surface")
    if patch_eval is None:
        failures.append("Missing eval 'patch-json-workspace-body-surface'.")
    else:
        expected_output = str(patch_eval.get("expected_output", ""))
        expectations = patch_eval.get("expectations", [])
        required_patch_tokens = [
            "extracts only the page body markdown",
            "does not build a diff from decorated page cat headers",
            "verifies the patch",
            "only then runs draft --workspace-json <active_workspace_path> page annotate",
        ]
        for token in required_patch_tokens:
            if token not in expected_output:
                failures.append(f"Patch eval expected_output is missing token: {token}")
        if "Agent builds the patch from page body markdown only" not in expectations:
            failures.append("Patch eval expectations must require body markdown patch generation.")

    image_eval = eval_by_name.get("image-local-id-mutation-flow")
    if image_eval is None:
        failures.append("Missing eval 'image-local-id-mutation-flow'.")
    else:
        expected_output = str(image_eval.get("expected_output", ""))
        required_image_tokens = [
            "captures the returned local_id",
            "page update-image <id> <local_id>",
            "page delete-image <id> <local_id>",
            "image block id as the same identifier",
        ]
        for token in required_image_tokens:
            if token not in expected_output:
                failures.append(f"Image eval expected_output is missing token: {token}")

    if failures:
        print("draft-cli review-loop regression check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("draft-cli review-loop regression check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
