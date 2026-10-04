---
name: principle-guard-the-context-window
description: "Apply when context is filling up with xcodebuild logs, crash reports, screenshots, long Swift files, repeated reads, or fan-out planning. Route bulk to Claude subagents (build-verify, Explore, ui-verify) and pass file paths, not payloads; keep conclusions in the main thread."
disable-model-invocation: true
---

# Guard the Context Window

The context window is finite and non-renewable within a session. Every token should be worth its cost.

**Why:** Context overflow degrades reasoning quality, creates compression artifacts, and halts progress. iOS work produces payloads far larger than the answer in them. One `xcodebuild` log runs to thousands of lines for a single `file:line: error`. One crash report is mostly binary images. One screenshot costs more than a page of text.

**Pattern:**
- **Isolate large payloads.** Route verbose outputs to subagents through the Agent tool and take back the conclusion.
  - Builds and tests go to `build-verify`, which returns only `file:line: message`.
  - Broad searches across the codebase go to `Explore`.
  - Screenshots, frame sheets and visual judgement go to `ui-verify`.
  - Review of a diff goes to `review-lens`, one lens each.
- **Pass pointers, not payloads.** Write a long output to a file and hand over its path (`.xcresult`, `.ips`, a `.trace`, a log). Read the slice you need with an offset, not the whole file. A script that extracts the answer (`scripts/ai/xcresult.py`) beats reading the raw output.
- **Keep frequently used content inline.** Templates and references used on every invocation belong in the skill file, not in separate files that cost a read each time.
- **Size phases and cap scope.** Limit files per phase, set turn budgets for subagents, and account for what each mechanism costs (a screenshot, a full test run, a subagent's report).

`principle-minimize-reader-load` is the same rule for human readers. `principle-never-block-on-the-human` covers what to do with the time a subagent buys.
