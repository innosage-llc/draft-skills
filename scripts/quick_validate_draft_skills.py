#!/usr/bin/env python3
"""
Product-local skill validator for draft-skills.

This product intentionally permits a top-level `version` field in SKILL.md
frontmatter because shipped skills already use it and ClawHub consumes it.
Keep this wrapper local to the product so the repo gate reflects the actual
contract without changing the global validator for unrelated skills.
"""

import re
import sys
from pathlib import Path

import yaml

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500

ALLOWED_PROPERTIES = {
    "name",
    "version",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}


def validate_skill(skill_path: str):
    skill_dir = Path(skill_path)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return False, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as exc:
        return False, f"Invalid YAML in frontmatter: {exc}"

    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        allowed = ", ".join(sorted(ALLOWED_PROPERTIES))
        unexpected = ", ".join(sorted(unexpected_keys))
        return (
            False,
            f"Unexpected key(s) in SKILL.md frontmatter: {unexpected}. Allowed properties are: {allowed}",
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter.get("name", "")
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            return (
                False,
                f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)",
            )
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return (
                False,
                f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens",
            )
        if len(name) > MAX_SKILL_NAME_LENGTH:
            return (
                False,
                f"Name is too long ({len(name)} characters). Maximum is {MAX_SKILL_NAME_LENGTH} characters.",
            )

    version = frontmatter.get("version")
    if version is not None and not isinstance(version, str):
        return False, f"Version must be a string, got {type(version).__name__}"

    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description:
        if len(description) > MAX_DESCRIPTION_LENGTH:
            return (
                False,
                f"Description is too long ({len(description)} characters). Maximum is {MAX_DESCRIPTION_LENGTH} characters.",
            )

    compatibility = frontmatter.get("compatibility", "")
    if compatibility:
        if not isinstance(compatibility, str):
            return False, f"Compatibility must be a string, got {type(compatibility).__name__}"
        if len(compatibility) > MAX_COMPATIBILITY_LENGTH:
            return (
                False,
                f"Compatibility is too long ({len(compatibility)} characters). Maximum is {MAX_COMPATIBILITY_LENGTH} characters.",
            )

    return True, "Skill is valid!"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate_draft_skills.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
