---
name: draft-agent-loop
description: >
  Enforce a Human-in-the-Right-Loop (HITRL) lifecycle for remote agents.
  Use this skill when the user wants structured oversight over an agent task: plan approval before execution, evidence-logged execution, and result sign-off before closure.
  Trigger phrases: "work on this with my oversight", "check with me before you start", "use HITRL for this", "I want to review your plan first", "use draft-agent-loop".
  DO NOT use for tasks where the user simply asks to do something without requesting approval gates. Use draft-cli for raw Draft commands.
  This skill depends on the draft-cli skill and enforces --mode local (remote-only, no shared filesystem).
metadata: {"clawdbot":{"emoji":"🔄","requires":{"skills":["draft-cli"]}}}
---

# Draft Agent Loop Skill (HITRL)

Use this skill to implement a rigorous human-agent collaboration loop. This is the "Human-in-the-Right-Loop" (HITRL) method, designed to eliminate "blind box" agent outcomes by forcing plan approval and result verification.

## Trigger Guidance

Trigger this skill when:

- "Work on this task and check with me before and after."
- "I want to review your plan first before you do anything."
- "Use HITRL / use draft-agent-loop for this."
- "Apply structured oversight to this task."
- New task received where the user's intent is high-stakes or complex enough to warrant human gates.
- A new iteration is requested after a Phase 3 sign-off.

Do NOT trigger this skill when:

- The user asks to do a task directly with no mention of approval or review gates.
- The user only asks about Draft CLI commands (use `draft-cli`).
- The user wants a local-file authoring workflow (authorship in local markdown).

## Core Rules

- **Source of Truth**: The "Task Journal" Draft page.
- **Environment**: Always use `draft-cli` in `--mode local`. Never use `--mode workspace`.
- **Handoff Mode**: **Blocking**. STOP and wait for human approval/sign-off in the chat before proceeding to the next phase.

## Phase 0: Setup & Connection

Before doing anything, establish a stable Draft connection:

```bash
# 1. Start the daemon in local mode (required for remote agents)
draft start-server --mode local

# 2. Confirm the session is READY before proceeding
draft status --json
```

If `draft status` does not show `READY`, follow the `draft-cli` connection-first recovery pattern:
- `DAEMON_OFFLINE` → re-run `draft start-server --mode local`
- `BROWSER_NOT_CONNECTED` → run `draft daemon` to pair a browser tab
- Only proceed once `draft status --json` shows `"state": "READY"`

## Phase 1: Plan (Proposal & Approval)

Before executing any code or changes:

1.  **Create Journal**: Create a new Draft page titled `<Task Name> - Task Journal`.
    ```bash
    draft page create "<Task Name> - Task Journal" --json
    ```
2.  **Submit Plan**: Authors a detailed Task Journal using the mandatory template. Appends it to the Journal.
    ```bash
    cat << 'EOF' | draft page append <id> --json
    # 📋 Task: [Title]

    ## Context
    [Detailed background and motivation]

    ## Problem / Goal
    [Specific issue being solved or feature being added]

    ## Acceptance Criteria (Outcome-Focused)
    - [ ] [Criterion 1]
    - [ ] [Criterion 2]

    ## Implementation Notes
    [Current state analysis, relevant files, suggested approach, technical considerations]

    ## Test Coverage
    [Test strategy, scenarios to test, existing tests to reference]
    EOF
    ```
3.  **Handoff**: Publish the page and ask for approval.
    ```bash
    draft page publish <id> --invite-code innosage --json
    ```
    **Handoff Phrase**: "I have initialized the Task Journal with the plan and requirements: [URL]. Please review the context and acceptance criteria. Once you are ready for me to proceed, please reply with **APPROVED** or **LGTM** here in the chat."

4.  **Wait**: STOP. Do not proceed until the user explicitly tells you to continue in the chat. Note: Do not rely on Draft page comments for approval on remote/public pages.

## Phase 2: Execute (Action & Logging)

Once approved:

1.  **Verify Approval**: Confirm the user has provided approval in the chat.
2.  **Execute**: Perform the tasks outlined in the plan.
3.  **Log Evidence**: For every significant action, append a log entry to the Journal under a `# 📜 Execution Log` section.
    ```bash
    cat << 'EOF' | draft page append <id> --json
    ### [Timestamp] Action: [Description]
    - **Status**: Success/Failure
    - **Evidence**: [e.g., Command output snippet or file path]
    EOF
    ```

## Phase 3: Verify (Result & Sign-off)

Once the execution is complete:

1.  **Submit Results**: Append a `# ✅ Final Results` summary to the Journal. Include links to artifacts or evidence of completion.
2.  **Handoff**: Re-publish the page.
    ```bash
    draft page publish <id> --invite-code innosage --json
    ```
    **Handoff Phrase**: "I have completed the task. Please verify the results in the Task Journal: [URL]. If satisfied, reply with **DONE** or **✅** here in the chat."

3.  **Wait**: STOP. If the user provides sign-off (**DONE** / **✅**), proceed to Phase 4. If feedback is received, enter the Iteration Loop.

## Phase 4: Archive & Memory

After sign-off, ensure the task is durable in your long-term memory:

1.  **Summarize**: Write a concise summary of the task, the solution, and the location of the evidence.
2.  **Persist**: Save this summary to your **system-level memory** (e.g., a `knowledge/` archive or a persistent `TASK_LOG.md`).
3.  **Cross-Reference**: Ensure the entry includes the Draft Page ID and published URL.
    *   *Example Entry*: `[2026-04-16] Implemented Reveal Button. Page ID: abc-123. URL: https://draft.innosage.co/p/abc-123. Summary: Added target icon to sidebar header; implemented revealPath in useFileSystemTree.`

## Iteration Loop

If the user provides feedback or requests changes after Phase 3:
1.  **Acknowledge**: Acknowledge the feedback in the chat.
2.  **Start New Iteration**: Enter Phase 1 again to propose how you will address the feedback.
3.  **Append to Same Page**: Do NOT create a new page. Append the new plan to the existing Task Journal under a new heading: `# 📋 Iteration [N]: Addressing Feedback`.
4.  **Template**: Use the mandatory Phase 1 template for each new iteration to maintain context and traceability.

## Non-Goals

- Do NOT use `--mode workspace`.
- Do NOT skip the plan approval gate.
- Do NOT execute multiple un-logged steps.
