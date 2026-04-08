# Draft CLI Live E2E Test Suite

## Purpose
This document serves as the canonical live E2E test suite (Layer 3 of the testing pyramid) for the Draft CLI. It tests real integrations against live Draft daemon/browser environments, catching regressions that agent mocked evals or pure CI gating might miss.

## Execution Guide
- **Execution Policy**: These test cases are to be executed against live environments.
- **History Update**: Every test run **MUST** overwrite the `Execution Result` block for that TC with a timestamped result snippet (do not append continuously).
- **Changelog**: Additions to the test suite logic itself should be recorded at the bottom in the `Changelog` section.

## Status Taxonomy
- ✅ **PASS**: The expected outcome was reached seamlessly.
- ❌ **FAIL**: Hard error or incorrect behavior.
- ⚠️ **FLAKY**: Inconsistent success.
- ⏭ **SKIPPED**: Not currently automatable or testable in the standard environment.
- 🆕 **NEW**: Un-executed new test logic.

---

## Core Functionality

### TC01: Basic Operations (Smoke Test)
- **Eval ID**: `1`
- **Goal**: Verify that `ls`, `cat`, and `create` work in a basic ready state.
- **Scenario**:
    1. Check status (`draft status --json`).
    2. List pages (`draft ls --json`).
    3. Create a new page titled "Test Page" (`draft create "Test Page" --json`).
    4. Read the content of the new page (`draft cat <id>`).
- **Execution Result (# 2026-04-07 13:45)**: ✅ **PASS**
    ```json
    {"ok":true,"state":"READY",...}
    {"ok":true,"pages":[{"id":"ou3devbyp","title":"draft-cli Skill: TC5 Patch Fix — Verification",...}]}
    {"ok":true,"operation":"create","page_id":"k0eyiwtwc","title":"Smoke Test Page 20260407-134500",...}
    ```
- **Expected Outcome**: All commands succeed and return correct data.

---

### TC02: Append with Multiline Content (stdin)
- **Eval ID**: `2`
- **Goal**: Verify that multiline Markdown can be appended via stdin without formatting loss.
- **Scenario**:
    1. Prepare a multiline Markdown string.
    2. Pipe it to `draft append <id>`.
    3. Verify the end of the file matches the appended content.
- **Execution Result (# 2026-04-07 13:46)**: ✅ **PASS**
    ```bash
    printf "## New Section\n- Item 1\n- Item 2\n" | draft append k0eyiwtwc --json
    {"ok":true,"operation":"append","page_id":"k0eyiwtwc"}
    ```
- **Expected Outcome**: Content is appended exactly as provided.

---

### TC03: Replace Section by Heading
- **Eval ID**: `3`
- **Goal**: Verify the precision of the `--heading` replacement logic.
- **Scenario**:
    1. Create a page with multiple sections.
    2. Replace "Section 2" with "New Content 2".
    3. Verify that "Section 1" and "Section 3" are untouched, and "Section 2" heading remains but its body is updated.
- **Execution Result (# 2026-04-07 13:48)**: ✅ **PASS**
    ```bash
    printf "New Content 2" | draft replace g243w6cvp --heading "Section 2" --json
    {"ok":true,"operation":"replace_section","page_id":"g243w6cvp","heading":"Section 2"}
    ```
- **Expected Outcome**: Surgical replacement within the targeted section.

---

### TC04: Replace Nested Heading
- **Goal**: Verify replacement logic for sub-headings.
- **Scenario**:
    1. Replace content under `### Sub-heading`.
    2. Ensure it doesn't leak into the next `## Heading` (higher level) or next `### Sub-heading` (same level).
- **Execution Result (# 2026-04-07 13:50)**: ✅ **PASS**
    ```bash
    printf "UPDATED Sub 1 CONTENT" | draft replace 22vq4eapt --heading "Sub 1" --json
    {"ok":true,"operation":"replace_section","page_id":"22vq4eapt","heading":"Sub 1"}
    ```
- **Expected Outcome**: Correct boundary detection for nested structures.

---

### TC05: Patch with Unified Diff
- **Goal**: Verify surgical editing via `draft patch`.
- **Scenario**:
    1. Create a page with a specific paragraph.
    2. Generate a unified diff for that paragraph.
    3. Apply the patch using `draft patch <id>`.
    4. Verify the change.
- **Execution Result (# 2026-04-07 13:54)**: ✅ **PASS**
    ```bash
    # Generated diff from body only (excluding Title/ID headers)
    diff -u /tmp/tc5_body_before.md /tmp/tc5_body_after.md > /tmp/tc5_body.diff
    # Applied patch
    cat /tmp/tc5_body.diff | draft patch kqoixvmdr --json
    {"ok":true,"operation":"patch","page_id":"kqoixvmdr"}
    ```
- **Fix Notes**: Use only the markdown body (between `---` separators) when generating the diff. Always run `draft cat <id>` first to capture the live serialization.
- **Expected Outcome**: Diff is applied correctly.

---

## Daemon & Connection Lifecycle

### TC06: Recovery: Daemon Offline
- **Goal**: Verify the agent can recover when the local server is not running.
- **Scenario**:
    1. Stop the server (`draft stop-server`).
    2. Run a command (e.g., `draft ls`).
    3. Agent should catch `DAEMON_OFFLINE`, run `draft start-server`, then retry.
- **Execution Result (# 2026-04-07 13:54)**: ✅ **PASS**
    ```bash
    draft stop-server
    draft ls --json -> ✅ Succeeds (CLI handles automatic restart or transparent recovery)
    ```
- **Expected Outcome**: Successful recovery and execution.

---

### TC07: Recovery: Browser Not Connected
- **Eval ID**: `5`
- **Goal**: Verify recovery when the daemon is up but the browser tab is missing.
- **Scenario**:
    1. Ensure daemon is running but close the paired tab.
    2. Run a command.
    3. Agent should catch `BROWSER_NOT_CONNECTED`, run `draft daemon`, then retry.
- **Execution Result (# 2026-04-07 13:54)**: ⏭ **SKIPPED**
- **Expected Outcome**: Successful recovery and execution (Difficult to automate without UI automation).

---

### TC08: Recovery: Editor Not Ready
- **Eval ID**: `6`
- **Goal**: Verify recovery when a tab is connected but not on a writable page.
- **Scenario**:
    1. Connect tab to the home page or a non-editor route.
    2. Run a write command (e.g., `append`).
    3. Agent should catch `EDITOR_NOT_READY`, navigate to the correct page URL, then retry.
- **Execution Result (# 2026-04-07 13:55)**: ✅ **PASS**
    ```bash
    draft daemon https://draft.innosage.co/ && draft append kqoixvmdr "Recovery test" --json
    # -> EDITOR_NOT_READY
    draft daemon https://draft.innosage.co/#/page/kqoixvmdr && draft append kqoixvmdr "Recovery test" --json
    # -> {"ok":true,"operation":"append","page_id":"kqoixvmdr"}
    ```
- **Expected Outcome**: Successful navigation and write.

---

## Advanced Scenarios

### TC09: Switching Environments
- **Goal**: Verify the agent can switch between production and staging.
- **Scenario**:
    1. Connect to production.
    2. Request to use staging (`https://markdown-editor-staging.web.app/`).
    3. Agent should stop the server and restart it with the new URL.
- **Execution Result (# 2026-04-07 13:55)**: ⏭ **SKIPPED** (Environment restricted).
- **Expected Outcome**: Connection switched to the requested environment.

---

### TC10: Publishing with Auth
- **Eval ID**: `4`
- **Goal**: Verify the publish flow and URL return.
- **Scenario**:
    1. Set `GLOBAL_PUBLISH_PASSWORD=innosage`.
    2. Run `draft publish <id> --json`.
    3. Verify the JSON response contains a `publish_url`.
- **Execution Result (# 2026-04-07 13:55)**: ✅ **PASS**
    ```bash
    GLOBAL_PUBLISH_PASSWORD=innosage draft publish kqoixvmdr --json
    {"ok":true,"operation":"publish","page_id":"kqoixvmdr","url":"https://draft.innosage.co/?mode=static#/preview/kqoixvmdr"}
    ```
- **Expected Outcome**: Page is published and URL is retrieved.

---

## Comment Discovery Settings

### TC11: List Comments on a Page
- **Eval ID**: `7`
- **Goal**: Verify that `draft comments <page_id> --json` returns all annotation records from a page with multiple highlights.
- **Scenario**:
    1. Open a Draft page in the editor and add **at least 2 annotation highlights** with distinct note text.
    2. Check status (`draft status --json`).
    3. Run `draft comments <page_id> --json`.
    4. Verify the response shape and field presence.
- **Execution Result (# 2026-04-07 21:10)**: ✅ **PASS**
    ```bash
    draft comments bkghstf9v --json
    # {"ok":true,"page_id":"bkghstf9v","comments":[
    #   {"comment_id":"5ca4a836-57bf-42b2-869a-31f126b788a0","anchor_text":"brown","note":"A","position_hint":10},
    #   {"comment_id":"fdb40a3c-c903-4456-ad12-a87a7986ade1","anchor_text":"over","note":"B","position_hint":26}
    # ]}
    ```
- **Expected Outcome**: `ok: true`, `comments` array with ≥ 2 items. Fields `resolved`, `author`, and `timestamp` must **not** be present.

---

### TC12: List Comments on a Page with No Annotations
- **Goal**: Verify that `draft comments` returns an empty array (not an error) when a page has no highlights.
- **Scenario**:
    1. Identify a Draft page with **zero annotation highlights** (plain text only).
    2. Check status (`draft status --json`).
    3. Run `draft comments <page_id> --json`.
    4. Verify the response is `ok: true` with an empty `comments` array.
- **Execution Result (# 2026-04-07 21:12)**: ✅ **PASS**
    ```bash
    draft comments 4selppb9k --json
    # {"ok":true,"page_id":"4selppb9k","comments":[]}
    ```
- **Expected Outcome**: `ok: true`, `comments: []`. No error or failure field.

---

### TC13: Invalid Page ID Returns Error
- **Goal**: Verify that `draft comments` with a non-existent page ID returns a clear error and does not crash.
- **Scenario**:
    1. Check status (`draft status --json`).
    2. Run `draft comments does-not-exist-00000 --json`.
    3. Verify the response surface is a clean error, not an unhandled exception.
- **Execution Result (# 2026-04-07 21:14)**: ✅ **PASS**
    ```bash
    draft comments does-not-exist-00000 --json
    # {"ok":false,"error":{"code":"PAGE_NOT_FOUND","message":"Page does-not-exist-00000 not found."...}}
    ```
- **Expected Outcome**: `ok: false`, with describing error fields. Exit code 1.

---

## Comment Inspection & Action

### TC14: Inspect a Single Comment with Bounded Context
- **Eval ID**: `8`
- **Goal**: Verify that `draft comment <comment_id> <page_id> --json` returns the note, anchor text, and a valid bounded context window.
- **Scenario**:
    1. Use a page with at least one annotation **not at the very beginning or end of the document**.
    2. Check status (`draft status --json`).
    3. Run `draft comments <page_id> --json` to retrieve a valid `comment_id`.
    4. Run `draft comment <comment_id> <page_id> --json`.
    5. Verify the response. `before + anchor_text + after` should match a contiguous block of `draft cat <page_id>`.
- **Execution Result (# 2026-04-07 21:16)**: ✅ **PASS**
    ```bash
    draft comment 5ca4a836-57bf-42b2-869a-31f126b788a0 bkghstf9v --json
    # {"ok": true, "bounded_context": {"before": "The quick ", "after": " fox jumps over the lazy cat.\n"}}
    ```
- **Expected Outcome**: `bounded_context.before` and `after` are correct; text matches exactly.

---

### TC15: End-to-End: Comment Discovery → Inspect → Surgical Patch
- **Goal**: Verify the full review-locate-patch cycle using comment context as the edit anchor.
- **Requirements Note**: You **MUST strip note markers** (`[:: User Note: ... :]`) from the `draft cat` output before generating the diff, otherwise `PATCH_MISMATCH` will occur as the editor state expects clean markdown.
- **Scenario**:
    1. Spot annotation over `"Fix: reword this sentence"`.
    2. Use `comments` and `comment` commands to obtain context and note.
    3. Strip markers out of `draft cat` output for base cleanly.
    4. Make edits based on anchor location context.
    5. Generate simple unified patch.
    6. Apply patch: `draft patch <id>`.
    7. Look at `draft cat` correctly updated.
- **Execution Result (# 2026-04-07 21:20)**: ✅ **PASS**
    ```bash
    # 1. Capture and strip markers
    draft cat bkghstf9v | sed '1,4d' | sed '$d' | sed 's/ \[:: User Note: [^:]* :\]//g' > /tmp/before_clean.md
    # 2. Patch applied successfully
    diff -u /tmp/before_clean.md /tmp/after_clean.md > /tmp/patch_clean.diff ; cat /tmp/patch_clean.diff | draft patch bkghstf9v --json
    # {"ok":true,"operation":"patch","page_id":"bkghstf9v"}
    ```
- **Expected Outcome**: Patch matches completely without `PATCH_MISMATCH`. Change applied identically over editor sync.

---

## Changelog

*Initial commit creating Layer 3 consolidated live E2E Test Suite.*
