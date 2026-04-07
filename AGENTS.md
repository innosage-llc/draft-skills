# AGENTS.md - Draft Skills Product Guidance

> [!IMPORTANT]
> Product: shared agent skills for Draft.
> Source of truth for merge readiness: [`README.md`](/Users/weijingliunyu/innosage-hub/products/draft-skills/README.md).

## Scope

- This product packages reusable agent skills under [`skills/`](/Users/weijingliunyu/innosage-hub/products/draft-skills/skills).
- Treat each skill directory as a shippable artifact. Structural validity and behavior both matter.
- Do not make assumptions from general agent-skill conventions when this repo already defines a local gate.

## Primary Files

- [`README.md`](/Users/weijingliunyu/innosage-hub/products/draft-skills/README.md): installation, product positioning, and the authoritative local merge gate.
- [`scripts/gate`](/Users/weijingliunyu/innosage-hub/products/draft-skills/scripts/gate): executable merge gate. If documentation and code diverge, fix the divergence.
- [`package.json`](/Users/weijingliunyu/innosage-hub/products/draft-skills/package.json): stable command entrypoints.
- [`skills/draft-cli/SKILL.md`](/Users/weijingliunyu/innosage-hub/products/draft-skills/skills/draft-cli/SKILL.md): current shipped skill.
- [`evals/`](/Users/weijingliunyu/innosage-hub/products/draft-skills/evals): checked-in smoke and regression fixtures.

## Required Workflow

1. Read [`README.md`](/Users/weijingliunyu/innosage-hub/products/draft-skills/README.md) before changing any shipped skill, eval fixture, or gate logic.
2. Prefer repo-local commands from [`package.json`](/Users/weijingliunyu/innosage-hub/products/draft-skills/package.json) over ad hoc validation commands.
3. When behavior changes, update the checked-in fixtures or docs in the same change.
4. Do not treat manual spot checks as a substitute for the local gate.

## Local Verification Gate

Run from [`products/draft-skills`](/Users/weijingliunyu/innosage-hub/products/draft-skills):

```bash
npm run gate
```

Equivalent direct command:

```bash
./scripts/gate
```

The gate order is mandatory:

1. structural validation via `quick_validate.py`
2. `draft-cli` review-loop regression guard
3. Phase 2 deterministic smoke checks
4. Phase 3 regression corpus checks

Focused commands:

- `npm run smoke`: deterministic smoke assertions only
- `npm run regression`: checked-in typed regression corpus only

## Merge Requirement

- `scripts/gate` is the local merge gate for this product.
- If `npm run gate` or `./scripts/gate` fails, the change is not eligible to merge.
- A change is merge-eligible only after the gate passes locally.
- Do not claim merge readiness from partial checks when the change affects shipped skills, gate logic, or eval fixtures.

## Change Expectations

- Keep skill packaging compatible with the validator expectations enforced by `quick_validate.py`.
- Preserve or improve checked-in coverage for trigger, non-trigger, malformed, ambiguous, and bugfix scenarios when relevant.
- If you modify instructions that affect `draft-cli` behavior, expect to update files under [`evals/`](/Users/weijingliunyu/innosage-hub/products/draft-skills/evals) and rerun the gate.
- If you change the gate contract itself, update [`README.md`](/Users/weijingliunyu/innosage-hub/products/draft-skills/README.md) and this file in the same change.

## Documentation Rule

- [`README.md`](/Users/weijingliunyu/innosage-hub/products/draft-skills/README.md) is the public-facing authority for verification and merge policy.
- This file exists to make agents follow that policy consistently, not to replace it with a different one.
