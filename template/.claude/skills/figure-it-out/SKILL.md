---
name: figure-it-out
description: Design an auditable playbook when no narrower one fits (a large migration, an ambitious multi-part iOS change, or work a human reviews after stepping away), then run it as a hypothesis loop with a verification harness built first and a decision trail kept as it goes. Use for /figure-it-out, "figure it out", a large migration (ObservableObject to @Observable, Core Data to SwiftData, completion handlers to async), or when no playbook in ios-loop applies.
argument-hint: "[the goal]"
disable-model-invocation: true
---

# Figure it out

**Job:** when the task matches no playbook, design one, run it, and hand back work a human can audit after stepping away.

**Not my job:** tasks a playbook in `ios-loop` already covers (use it) · one-way-door design decisions on their own (`/architect`, which this skill calls) · merging (the owner, after `/verify` and `scripts/ai/pr.sh`).

**When there is nothing to report:** "A playbook already fits", naming it, then follow that playbook instead.

When the task matches no playbook, design one. The deliverable before any code is the workflow itself: a sequence of phases that scales rigor to the task, runs the scientific method, and leaves a decision trail a human can audit after stepping away.

## Start

Open a todo list whose first item is to read the Principles index in `.claude/skills/ios-loop/SKILL.md` and the `principle-<name>` skills it points to. Then add the phases below as todos.

## Phase A: Frame

Ground first, then commit. Do not start the run until you can state:

- **The definition of done** as a falsifiable predicate, per `principle-prove-it-works`. "Every `ObservableObject` in the app target is `@Observable`, `/verify` passes, and the visual sheets match the baseline" is a predicate. "Modernize the models" is not.
- **Scope, quantified:** rough units and effort (34 types across 12 files), plus the blockers grounding surfaced (a type used from a widget extension, a test that subclasses one).
- **The rigor level, biased high.** One-way doors (a Core Data model version, a CloudKit schema deployed to Production, a shipped URL scheme) and a wide blast radius get more. Reversible low-stakes steps get less. Rigor is gates and artifacts, not "try harder".

Present the framing and tradeoffs before committing to a long run. Reversible work proceeds, per `principle-never-block-on-the-human`. A multi-hour run earns one checkpoint with `AskUserQuestion`.

## Phase B: Design the workflow

Decompose into atomic, independently landable units. Sequence the riskiest unknown first. Scaffold and verification come before features, per `principle-foundational-thinking`.

- **Build the verification harness before the work,** with the baseline captured from the pre-change state, so each check reads "old value vs. new value". On iOS that is usually some of: a `/verify` run on the base commit (its visual sheets are the screenshot baseline), `python3 scripts/ai/blast-radius.py --diff "<base>...HEAD"` to list the surfaces to re-check, a Swift Testing suite that pins current behavior, an XCTest `measure` baseline, a grep test that counts the old pattern.
- **For one-way-door design decisions, run `/architect`** (it runs `/arena`). Skip it for mechanical work whose shape is already concrete. A second arena over a settled design is over-engineering, per `principle-laziness-protocol`.
- **Decide what fans out.** Parallelize only across seams, and give each worker its own worktree (`scripts/ai/worktree.sh new <id>`, which also gives it its own simulator), per `principle-separate-before-serializing-shared-state`. Coupled code stays in one session. Work that needs no Xcode can go to a cloud session (`scripts/ai/cloud.sh`). Do not over-fan.
- **Write the designed phase list down.** That list is what the human reviews.

Then execute the design. Add its steps to the todo list as concrete items, after the Phase C entry and before Phase D. Run each under the Phase C loop, and weave the Phase D log through them, a row as each step lands, rather than saving the trail for the end.

## Phase C: Run the loop

Each unit is an experiment. State the hypothesis, make the smallest change, measure against the predicate on the real artifact, keep it if it advanced, revert it if it did not. Verify each unit before starting the next, per `principle-sequence-verifiable-units`. Each unit goes through the `ios-loop` skill: `scripts/ai/build.sh`, `scripts/ai/test.sh`, the surface.

- **Verify by inspecting the artifact, never a self-report.** Open the screenshot. Read the `.xcresult` summary `scripts/ai/test.sh` prints. When something passes too easily, suspect the observation method before the system: a stale install, another session's build, a test that ran zero cases.
- **Pair delegated work with a judge.** If a worker games the gate, reset and harden the contract. If the gate itself is wrong, fix the gate in its own change rather than routing around it.
- **A verdict is VERIFIED, NOT VERIFIED, or INCONCLUSIVE.** Inconclusive is not a pass. Do not hide a negative.

## Phase D: Keep the audit trail

Log the run through the **show-me-your-work** skill. Work this ambitious usually earns a committed trail, so the reviewer can read it in the PR. The trail plus the diff is what lets the human come back and trust the work.

## Phase E: Verify and hand back

Check the whole against the Phase A predicate on the real product, not only the harness: `/verify` on the final commit, the visual sheets judged with `python3 scripts/ai/history.py judge PASS|FAIL`, and a device run where only a device can prove it. Encode any recurring correction as a type, a test, a hook or a script, per `principle-encode-lessons-in-structure`. Open the PR with `scripts/ai/pr.sh`.

**Reply:** the playbook you designed, the rigor level and why, the decision-trail path, what is verified against the predicate, and what is still open.
