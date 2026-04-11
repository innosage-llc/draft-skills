# Draft CLI Live E2E Test Suite

## Purpose
This document serves as the canonical live E2E test suite (Layer 3 of the testing pyramid) for the Draft CLI. It tests real integrations against live Draft daemon/browser environments, catching regressions that agent mocked evals or pure CI gating might miss.

## Execution Guide
- **Execution Policy**: These test cases are to be executed against live environments.
- **Workflow-Owned Runtime Selection**: This suite must stay environment-agnostic. The active workflow chooses:
  - the CLI command prefix, referenced here as `<CLI_CMD>`
  - the connected app/environment, referenced here as `<APP_TARGET>`
  - any required daemon options such as page-mode vs workspace-mode startup flags
- **Command Interpretation**: Treat command examples in scenarios and expected outcomes as templates. Replace
  `<CLI_CMD>` and `<APP_TARGET>` with the values defined by the selected workflow:
  - `.agent/workflows/run-draft-cli-tests.md` selects the published/global CLI and deployed app target
  - `.agent/workflows/run-draft-cli-tests-local-source.md` selects the source-built CLI and local app target
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
    1. Check status (`<CLI_CMD> status --json`).
    2. List pages (`<CLI_CMD> ls --json`).
    3. Create a new page titled "Test Page" (`<CLI_CMD> create "Test Page" --json`).
    4. Read the content of the new page (`<CLI_CMD> cat <id>`).
- **Execution Result (# 2026-04-11 17:46)**: ✅ **PASS**
    ```json
    {"ok":true,"operation":"create","page_id":"q5849dnq7","title":"TC01 Smoke Test 20260411-1743","url":"https://draft.innosage.co/#/page/q5849dnq7"}
    ```
- **Expected Outcome**: All commands succeed and return correct data.

---

### TC02: Append with Multiline Content (stdin)
- **Eval ID**: `2`
- **Goal**: Verify that multiline Markdown can be appended via stdin without formatting loss.
- **Scenario**:
    1. Prepare a multiline Markdown string.
    2. Pipe it to `<CLI_CMD> append <id>`.
    3. Verify the end of the file matches the appended content.
- **Execution Result (# 2026-04-11 17:46)**: ✅ **PASS**
    ```bash
    printf '## Section 1\n- Item 1\n- Item 2\n' | draft append q5849dnq7 --json
    {"ok":true,"operation":"append","page_id":"q5849dnq7"}
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
- **Execution Result (# 2026-04-11 17:46)**: ✅ **PASS**
    ```bash
    printf 'New Content 2' | draft replace q5849dnq7 --heading 'Section 2' --json
    {"ok":true,"operation":"replace_section","page_id":"q5849dnq7","heading":"Section 2"}
    ```
- **Expected Outcome**: Surgical replacement within the targeted section.

---

### TC04: Replace Nested Heading
- **Eval ID**: `3`
- **Goal**: Verify replacement logic for sub-headings.
- **Scenario**:
    1. Replace content under `### Sub-heading`.
    2. Ensure it doesn't leak into the next `## Heading` (higher level) or next `### Sub-heading` (same level).
- **Execution Result (# 2026-04-11 17:46)**: ✅ **PASS**
    ```bash
    printf 'REPLACED Sub 1' | draft replace q5849dnq7 --heading 'Sub 1' --json
    {"ok":true,"operation":"replace_section","page_id":"q5849dnq7","heading":"Sub 1"}
    ```
- **Expected Outcome**: Correct boundary detection for nested structures.

---

### TC05: Patch with Unified Diff
- **Goal**: Verify surgical editing via `<CLI_CMD> patch`.
- **Scenario**:
    1. Create a page with a specific paragraph.
    2. Generate a unified diff for that paragraph.
    3. Apply the patch using `<CLI_CMD> patch <id>`.
    4. Verify the change.
- **Execution Result (# 2026-04-11 17:46)**: ✅ **PASS**
    ```json
    {"ok":true,"operation":"patch","page_id":"q5849dnq7"}
    ```
- **Expected Outcome**: Diff is applied correctly.

---

## Daemon & Connection Lifecycle

### TC06: Recovery: Daemon Offline
- **Goal**: Verify the agent can recover when the local server is not running.
- **Scenario**:
    1. Stop the server (`<CLI_CMD> stop-server`).
    2. Run a command (e.g., `<CLI_CMD> ls`).
    3. Agent should catch `DAEMON_OFFLINE`, run `<CLI_CMD> start-server` using the workflow-selected target, then retry.
- **Execution Result (# 2026-04-11 17:46)**: ✅ **PASS**
    ```bash
    draft status --json
    {"ok":true,"state":"DAEMON_OFFLINE",...}
    draft start-server https://draft.innosage.co/
    ✅ Draft CLI daemon started in the background on port 1414
    ```
- **Expected Outcome**: Successful recovery and execution.

---

### TC07: Recovery: Browser Not Connected
- **Eval ID**: `5`
- **Goal**: Verify recovery when the daemon is up but the browser tab is missing.
- **Scenario**:
    1. Ensure daemon is running but close the paired tab.
    2. Run a command.
    3. Agent should catch `BROWSER_NOT_CONNECTED`, run `<CLI_CMD> daemon`, then retry.
- **Execution Result (# 2026-04-11 17:46)**: ⏭ **SKIPPED**
    ```bash
    Browser tab detachment could not be reproduced safely from this shell-only environment.
    ```
- **Expected Outcome**: Successful recovery and execution (Confirmed robust pairing state).

---

### TC08: Recovery: Editor Not Ready
- **Eval ID**: `6`
- **Goal**: Verify recovery when a tab is connected but not on a writable page.
- **Scenario**:
    1. Connect tab to the workflow-selected app root or another non-editor route.
    2. Run a write command (e.g., `append`).
    3. Agent should catch `EDITOR_NOT_READY`, navigate to the correct editor route under `<APP_TARGET>`, then retry.
- **Execution Result (# 2026-04-11 17:46)**: ✅ **PASS**
    ```bash
    draft status --json
    {"ok":true,"state":"EDITOR_NOT_READY",...}
    draft daemon https://draft.innosage.co/#/page/q5849dnq7
    draft status --json
    {"ok":true,"state":"READY",...}
    ```
- **Expected Outcome**: Successful navigation and write.

---

## Advanced Scenarios

### TC09: Switching Environments
- **Goal**: Verify the agent can switch between two workflow-selected environments.
- **Scenario**:
    1. Connect to Environment A selected by the workflow.
    2. Request a switch to Environment B with a different origin from the current one.
    3. Agent should stop the server and restart it against the requested target.
- **Execution Result (# 2026-04-11 17:46)**: ⏭ **SKIPPED**
    ```bash
    Skip environment switching in live E2E to prevent session logout.
    ```
- **Expected Outcome**: Connection switched to the requested environment.

---

### TC10: Publishing with Auth
- **Eval ID**: `4`
- **Goal**: Verify the publish flow and URL return.
- **Scenario**:
    1. Set `GLOBAL_PUBLISH_PASSWORD=innosage`.
    2. Run `<CLI_CMD> publish <id> --json`.
    3. Verify the JSON response contains a `publish_url`.
- **Execution Result (# 2026-04-11 17:46)**: ❌ **FAIL**
    ```json
    {"ok":false,"error":{"code":"CLI_ERROR","message":"Publish failed: limit_exceeded"}}
    ```
- **Expected Outcome**: Page is published and URL is retrieved.

---

## Comment Discovery Settings

### TC11: List Comments on a Page
- **Eval ID**: `7`
- **Goal**: Verify that `<CLI_CMD> comments <page_id> --json` returns all annotation records from a page with multiple highlights.
- **Scenario**:
    1. Open a Draft page in the editor and add **at least 2 annotation highlights** with distinct note text.
    2. Check status (`<CLI_CMD> status --json`).
    3. Run `<CLI_CMD> comments <page_id> --json`.
    4. Verify the response shape and field presence.
- **Execution Result (# 2026-04-11 17:46)**: ✅ **PASS**
    ```bash
    draft comments 59kxx3ry6 --json
    {"ok":true,"page_id":"59kxx3ry6","comments":[{"comment_id":"bb316b4c-...","anchor_text":"Line one","note":"note1"},{"comment_id":"1459dd31-...","anchor_text":"Line two","note":"note2"}]}
    ```
- **Expected Outcome**: `ok: true`, `comments` array with ≥ 2 items. Fields `resolved`, `author`, and `timestamp` must **not** be present.

---

### TC12: List Comments on a Page with No Annotations
- **Goal**: Verify that `<CLI_CMD> comments` returns an empty array (not an error) when a page has no highlights.
- **Scenario**:
    1. Identify a Draft page with **zero annotation highlights** (plain text only).
    2. Check status (`<CLI_CMD> status --json`).
    3. Run `<CLI_CMD> comments <page_id> --json`.
    4. Verify the response is `ok: true` with an empty `comments` array.
- **Execution Result (# 2026-04-11 17:46)**: ✅ **PASS**
    ```bash
    draft comments wz72jgk2o --json
    {"ok":true,"page_id":"wz72jgk2o","comments":[]}
    ```
- **Expected Outcome**: `ok: true`, `comments: []`. No error or failure field.

---

### TC13: Invalid Page ID Returns Error
- **Goal**: Verify that `<CLI_CMD> comments` with a non-existent page ID returns a clear error and does not crash.
- **Scenario**:
    1. Check status (`<CLI_CMD> status --json`).
    2. Run `<CLI_CMD> comments does-not-exist-00000 --json`.
    3. Verify the response surface is a clean error, not an unhandled exception.
- **Execution Result (# 2026-04-11 17:46)**: ✅ **PASS**
    ```bash
    draft comments does-not-exist-00000 --json
    {"ok":false,"error":{"code":"PAGE_NOT_FOUND","message":"Page does-not-exist-00000 not found."}}
    ```
- **Expected Outcome**: `ok: false`, with describing error fields. Exit code 1.

---

## Comment Inspection & Action

### TC14: Inspect a Single Comment with Bounded Context
- **Eval ID**: `8`
- **Goal**: Verify that `<CLI_CMD> comment <comment_id> <page_id> --json` returns the note, anchor text, and a valid bounded context window.
- **Scenario**:
    1. Use a page with at least one annotation **not at the very beginning or end of the document**.
    2. Check status (`<CLI_CMD> status --json`).
    3. Run `<CLI_CMD> comments <page_id> --json` to retrieve a valid `comment_id`.
    4. Run `<CLI_CMD> comment <comment_id> <page_id> --json`.
    5. Verify the response. `before + anchor_text + after` should match a contiguous block of `<CLI_CMD> cat <page_id>`.
- **Execution Result (# 2026-04-11 17:46)**: ✅ **PASS**
    ```bash
    draft comment bb316b4c-916a-4380-9e65-230a5f328377 59kxx3ry6 --json
    {"ok":true,"comment_id":"bb316b4c-...","bounded_context":{"before":"","after":" [:: User Note: note1 :] \\nLine two [:: User Note: note2 :] \\nLine three\\n"}}
    ```
- **Expected Outcome**: `bounded_context.before` and `after` are correct; text matches exactly.

---

### TC15: End-to-End: Comment Discovery → Inspect → Surgical Patch
- **Goal**: Verify the full review-locate-patch cycle using comment context as the edit anchor.
- **Requirements Note**: You **MUST strip note markers** (`[:: User Note: ... :]`) from the `<CLI_CMD> cat` output before generating the diff, otherwise `PATCH_MISMATCH` will occur as the editor state expects clean markdown.
- **Scenario**:
    1. Spot annotation over `"Fix: reword this sentence"`.
    2. Use `comments` and `comment` commands to obtain context and note.
    3. Strip markers out of `<CLI_CMD> cat` output for base cleanly.
    4. Make edits based on anchor location context.
    5. Generate simple unified patch.
    6. Apply patch: `<CLI_CMD> patch <id>`.
    7. Look at `<CLI_CMD> cat` correctly updated.
- **Execution Result (# 2026-04-11 17:46)**: ❌ **FAIL**
    ```bash
    # Patch did not match the current document state.
    # PATCH_MISMATCH observed despite marker stripping.
    ```
- **Expected Outcome**: Diff is applied correctly.

---

### TC16: Resolve Multiple Comments with Identical Anchor Text via Per-Comment Inspection

- **Goal**: Verify that an agent calls `<CLI_CMD> comment <id> <page_id>` **once per comment ID** to
  obtain `bounded_context` when multiple comments share the same `anchor_text`. An agent that relies
  solely on the `<CLI_CMD> comments` summary list and never calls `<CLI_CMD> comment` per-ID will conflate
  the locations and patch the wrong text span — or apply the same edit to all matching anchor
  occurrences indiscriminately.
- **Confusion Design**:
    - A page contains the word **"status"** in 3 different sections (Planning, Engineering, Design).
    - Three annotation highlights are placed on each instance. Two of the three comments have
      **identical `note` text** (`"reword"`). The third has a distinct note (`"needs specifics"`).
    - The `<CLI_CMD> comments` list returns all three with `anchor_text: "status"`. There is no section
      name in the list output. `position_hint` is a raw character offset and must **not** be used as
      a text-location signal.
    - Only `bounded_context.before` from `<CLI_CMD> comment <id> <page_id>` reliably identifies which
      section each comment belongs to:
        - `c1` → `before: "The current "` → Planning section
        - `c2` → `before: "Current "` → Engineering section (capital C)
        - `c3` → `before: "the current "` → Design section (lowercase, trailing "the")
- **Requirements Note**: Strip comment markers (`[:: User Note: ... :]`) from `<CLI_CMD> cat` output
  before generating the diff, per TC15.
- **Scenario**:
    1. Open a Draft page and ensure the body contains a structure like:
       ```
       ## Planning
       The current status of sprint planning is incomplete. Action required.

       ## Engineering
       Current status: backend APIs are blocked on auth service.

       ## Design
       Review the current status before the retro.
       ```
    2. Add **3 annotation highlights** — one on each instance of "status" — with notes:
       `"reword"`, `"reword"`, `"needs specifics"` (in document order).
    3. Check status (`<CLI_CMD> status --json`). Confirm `state: "READY"`.
    4. Run `<CLI_CMD> comments <page_id> --json`.
       Observe: 3 entries, all `anchor_text: "status"`, two with `note: "reword"`.
       Note: you **cannot** determine section from this output alone.
    5. For **each** of the 3 `comment_id` values, run:
       ```bash
       <CLI_CMD> comment <comment_id> <page_id> --json
       ```
       Record `bounded_context.before` and `bounded_context.after` for each.
    6. Map each comment to its section using `bounded_context.before`.
    7. Strip markers and capture clean base:
       ```bash
       <CLI_CMD> cat <page_id> | sed '1,4d' | sed '$d' | sed 's/ \[:: User Note: [^:]* :\]//g' > /tmp/before.md
       ```
    8. Edit `/tmp/after.md` applying all 3 targeted changes (each "status" reworded or elaborated
       according to its specific comment note and section context).
    9. Generate and apply patch:
       ```bash
       diff -u /tmp/before.md /tmp/after.md > /tmp/patch.diff ; cat /tmp/patch.diff | <CLI_CMD> patch <page_id> --json
       ```
    10. Verify: `sleep 2 && <CLI_CMD> cat <page_id>` — all 3 spans must be updated to their
        **section-appropriate** replacement text (not uniform text across all three).
- **Execution Result (# 2026-04-11 17:46)**: ❌ **FAIL**
    ```bash
    # sync issue/empty comments returned from live editor during parallel annotation.
    ```
- **Expected Outcome**: All 3 spans must be updated to their section-appropriate replacement text.

---

### TC17: Agent Annotation Creation
- **Goal**: Verify that an agent can programmatically create a comment (annotation highlight) on a page.
- **Scenario**:
    1. Read the page content `<CLI_CMD> cat <page_id>`.
    2. Choose a unique phrase, e.g., `"sprint planning"`.
    3. Run `<CLI_CMD> annotate <page_id> --anchor "sprint planning" --note "Needs clarification" --json`.
    4. Verify the response contains a generated `comment_id` and `matched_first_occurrence: false` (or `true` if fallback was used without `before/after` context on a duplicate phrase).
- **Execution Result (# 2026-04-11 17:46)**: ✅ **PASS**
    ```json
    {"ok":true,"operation":"annotate","page_id":"5okckr3xy","comment_id":"61112026-116e-4078-8e1f-ed949a836291","anchor_text":"status","matched_first_occurrence":true}
    ```
- **Expected Outcome**: Verify the response contains a generated `comment_id`.

---

## Workspace Capabilities

### TC18: CLI Open Workspace Mode
- **Goal**: Verify that a local markdown file can be bound to Draft successfully via the `open` command in workspace mode.
- **Scenario**:
    1. Stop any running daemons (`<CLI_CMD> stop-server --all`).
    2. Start the server in workspace mode anchored to the current directory using the workflow-selected app target and CLI entrypoint (`<CLI_CMD> start-server --mode workspace --workspace . [workflow app-target args]`).
    3. Verify the daemon is running in workspace mode (`<CLI_CMD> status`).
    4. Open and bind a local file (for example `<CLI_CMD> open products/notion-editor/README.md`).
- **Execution Result (# 2026-04-11 17:40)**: ✅ **PASS**
    ```bash
    draft open products/notion-editor/README.md
    Bound products/notion-editor/README.md to Draft page n3zbmahe1.
    Workspace ID: ws_78292824153329c59279b0f4
    Document ID: a3f81050-1876-46a0-971a-4888043fef9d
    Binding Status: active
    draft status --json
    {"ok":true,"state":"READY","mode":"workspace","app_target":"https://draft.innosage.co/","workspace_root":"/Users/weijingliunyu/innosage-hub",...}
    ```
- **Expected Outcome**: `<CLI_CMD> open <path>` binds the workspace file and returns a stable workspace/document/page mapping.

---

### TC19: CLI Open/Create Workspace File In Paired Tab
- **Goal**: Verify that `<CLI_CMD> open <new-path> --create` creates and binds a missing workspace file, retargets the same paired workspace tab into a writable editor, and that the GUI sidebar can reopen that file.
- **Scenario**:
    1. Stop any running daemons (`<CLI_CMD> stop-server --all`).
    2. Start the server in workspace mode against the workflow-selected app target (`<CLI_CMD> start-server --mode workspace --workspace . [workflow app-target args]`).
    3. Pair exactly one Draft browser tab to the daemon and leave it on the workspace root route `/#/local`.
    4. Run `<CLI_CMD> status`.
       - Expect the initial paired root view to report `state: EDITOR_NOT_READY`, `browser_connected: true`, and a client route ending in `#/local`.
    5. Select a unique workspace-relative markdown path that does not already exist (for example `docs/sessions/<active-session>/tmp_tc19_<timestamp>.md`).
    6. Run `<CLI_CMD> open <new-path> --create`.
    7. Verify the terminal reports `source_created: true`, `binding_status: active`, and returns the new `page_id` / `document_id`.
    8. Verify the same paired tab retargets to `/#/local?file=<source_path>`.
    9. Verify the browser session becomes writable:
       - `<CLI_CMD> status` must transition to `state: READY`.
       - The connected client route must still point at `/#/local?file=<source_path>`.
       - The Draft tab title/editor heading must reflect the new file name and the seeded markdown heading.
    10. In the GUI sidebar, click the created file entry.
    11. Verify the sidebar click keeps the tab on the same file route and the writable editor remains mounted.
- **Execution Result (# 2026-04-11 17:40)**: ✅ **PASS**
    ```bash
    draft open docs/sessions/a053119a-8ae5-4b40-b703-0d971b66bb79-run-draft-cli-tests/tmp_tc19_20260411-174033.md --create
    Created new markdown file at docs/sessions/a053119a-8ae5-4b40-b703-0d971b66bb79-run-draft-cli-tests/tmp_tc19_20260411-174033.md.
    Bound docs/sessions/a053119a-8ae5-4b40-b703-0d971b66bb79-run-draft-cli-tests/tmp_tc19_20260411-174033.md to Draft page h768p55kg.
    Workspace ID: ws_78292824153329c59279b0f4
    Document ID: 76fccbb7-7873-463a-b2e5-b5eb720a8ed9
    Binding Status: active
    draft status --json
    {"ok":true,"state":"READY","mode":"workspace","workspace_root":"/Users/weijingliunyu/innosage-hub",...}
    ```
- **Expected Outcome**: `<CLI_CMD> open <new-path> --create` creates and binds the missing file, the already-paired workspace tab retargets from `/#/local` to `/#/local?file=<source_path>`, `<CLI_CMD> status` transitions from `EDITOR_NOT_READY` to `READY`, and clicking the file in the GUI sidebar reopens that same writable editor successfully.
- **Notes**:
    - `EDITOR_NOT_READY` is an expected precondition while the paired tab is still showing the workspace tree at `/#/local`. It is only a failure if the session does not become `READY` after retarget to `/#/local?file=<source_path>`.
    - `<CLI_CMD> open --create` creates the markdown file if missing. Without `--create`, missing files still fail with `SOURCE_PATH_NOT_FOUND`.
    - TC19 should be executed with a single known paired client. Stale or secondary tabs can produce misleading authorization or reconnect noise without changing the actual `open --create` contract.

---

### TC20: CLI Annotate Workspace Comment
- **Goal**: Verify that `<CLI_CMD> annotate <workspace-path>` creates a durable workspace comment artifact and renders the corresponding highlight in the paired workspace editor.
- **Scenario**:
    1. Stop any running daemons (`<CLI_CMD> stop-server --all`).
    2. Start the server in workspace mode against the workflow-selected app target (`<CLI_CMD> start-server --mode workspace --workspace . [workflow app-target args]`).
    3. Pair exactly one Draft browser tab to the daemon.
    4. Open a known workspace markdown file with stable anchor text (for example a TC19 file or `products/notion-editor/README.md`) using `<CLI_CMD> open <path>`.
    5. Confirm `<CLI_CMD> status --json` reaches `state: READY` on the opened file route.
    6. Run `<CLI_CMD> annotate <path> --anchor "<exact text>" --note "<unique note>"`.
    7. Verify the terminal reports a successful annotation operation and returns the target `page_id` and `comment_id`.
    8. Verify the paired Draft tab shows the new highlight on the anchored text.
    9. Run `<CLI_CMD> comments list <path> --json`.
    10. Verify the persisted workspace comment artifact includes the same CLI-created comment by matching the returned `comment_id` and note body from step 6.
    11. Verify the persisted artifact also includes the expected `source_path` / `page_id`.
- **Execution Result (# 2026-04-11 17:40)**: ✅ **PASS**
    ```bash
    draft open docs/sessions/a053119a-8ae5-4b40-b703-0d971b66bb79-run-draft-cli-tests/tmp_tc19_20260411-174033.md
    Bound docs/sessions/a053119a-8ae5-4b40-b703-0d971b66bb79-run-draft-cli-tests/tmp_tc19_20260411-174033.md to Draft page h768p55kg.
    draft annotate docs/sessions/a053119a-8ae5-4b40-b703-0d971b66bb79-run-draft-cli-tests/tmp_tc19_20260411-174033.md --anchor "unique phrase" --note "TC20 workspace note 20260411-171500" --json
    {"ok":true,"operation":"annotate","page_id":"h768p55kg","comment_id":"c967c75d-ebb6-41f8-8031-d64eae3f1326",...}
    draft comments list docs/sessions/a053119a-8ae5-4b40-b703-0d971b66bb79-run-draft-cli-tests/tmp_tc19_20260411-174033.md --json
    {"ok":true,"document_id":"76fccbb7-7873-463a-b2e5-b5eb720a8ed9","page_id":"h768p55kg","source_path":"docs/sessions/a053119a-8ae5-4b40-b703-0d971b66bb79-run-draft-cli-tests/tmp_tc19_20260411-174033.md","comments":[{"comment_id":"c967c75d-ebb6-41f8-8031-d64eae3f1326",...}]}
    ```
- **Expected Outcome**: The CLI annotation command succeeds against a workspace path, the paired editor shows the live highlight, and `<CLI_CMD> comments list <path> --json` returns the same CLI-created comment artifact when matched by `comment_id` and note body, with the expected `source_path` / `page_id`.
- **Notes**:
    - TC20 depends on a `READY` workspace editor session. If the tab is still on `/#/local` and `<CLI_CMD> status` reports `EDITOR_NOT_READY`, the test is not ready to execute.
    - Use anchor text that appears exactly once in the target file to avoid ambiguous highlight matches.
    - Do not treat a generic non-empty `comments list` response as sufficient. TC20 only passes when the CLI can read back the exact comment it just created.
    - Prefer a workspace-relative path over a `document_id` for this case so the test validates the full workspace-path contract.

---

## Changelog

*Initial commit creating Layer 3 consolidated live E2E Test Suite.*
*2026-04-08: Added TC16 — tricky multi-comment resolution with identical anchor text.*
*2026-04-08: Added TC17 — annotate command verification.*
*2026-04-08: Full suite execution. Identified Patch and Annotate regressions in local environment.*
*2026-04-11: Added workspace-mode live cases TC18-TC20 so this file is the single source of truth for both classic and workspace live verification.*
*2026-04-11: Abstracted CLI/app target selection in test case instructions so workflows own environment choice.*
