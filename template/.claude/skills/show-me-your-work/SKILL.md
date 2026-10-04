---
name: show-me-your-work
description: "Keep a reviewable decision trail for long-running or unattended work: a TSV log with one row per decision (what, why, evidence, result), audited against the session transcript and reviewed by a second Claude model. Local by default. Commit it when a reviewer needs the trail to trust the result. Use for /show-me-your-work, autonomous or multi-phase runs, or work a person reviews after stepping away."
disable-model-invocation: true
---

# Show me your work

**Job:** keep one canonical decision log for a run, audit it against what actually happened, and end the reply with what the person should look at.

**Not my job:** logging every tool call · rewriting history to make a run look better · the verification itself (`/verify` and the playbooks own that, and the log only points at their evidence) · a summary for readers outside the run.

**When there is nothing to report:** the log's path and row count, and an Attention section that reads `reviewed by <model>` and "No flags".

## The format

One TSV file, one row per decision. Cells stay on one line. Evidence is a pointer, not prose.

Copy `references/decision-log-template.tsv` (the header row) to start a clean log. The columns:

- **ts.** ISO 8601 timestamp.
- **phase.** The phase or workstream.
- **decision.** What was chosen or done, one line.
- **why.** The reason in plain words. If a principle drove it, say the reason plainly, not as a jargon tag.
- **evidence.** A pointer that proves it. A commit hash, a PR number, `file:line`, a `/verify` report, a screenshot or frame-strip path, an `.xcresult`, an Instruments `.trace`. Never a paragraph.
- **result.** The outcome. `tests green`, `verify PASS`, `reverted`, `pixel-diff 0`, `INCONCLUSIVE`, `open`.

An example, plain enough to read at a glance.

```
ts	phase	decision	why	evidence	result
2026-05-24T09:02:00Z	frame	counted the screens first, 14 screens and about 30 hours	wanted the size before starting a long run	commit 3a9f1c2	found 3 things to settle before starting
2026-05-24T09:40:00Z	baseline	took screenshots of every screen before changing anything	so old and new can be compared and any visual change caught	.build/visual/before/	saved 42 screenshots at 3 sizes
2026-05-24T11:15:00Z	settings	moved the settings rows to the new list style without changing how they look	keep the change small and the result identical	commit 7c21e0a, sim.sh compare diff 0	looks identical, tests pass
2026-05-24T12:30:00Z	settings	threw out a helper's work because its screenshots were blank	checked the real images instead of trusting its summary	worktree reset	reverted, tightened the brief for next time
```

## Logging a row

Write each row the way you would tell a teammate what you did. Plain words, concrete actions, no jargon. `/unslop` applies to log text too.

Use the helper.

```bash
.claude/skills/show-me-your-work/scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>
```

It stamps `ts`, writes the header on first use, strips stray tabs and newlines, and puts a single quote before any cell that starts with `=`, `+`, `-` or `@`, so a spreadsheet never runs a cell as a formula. A bare `printf` that appends a row works too, but guard the same bytes when a cell comes from generated or outside text (a PR title, a file name).

Log decision points and checkpoints, not every action. A fork chosen, a unit finished with its verification result, a pivot or revert with its trigger, a blocker found, a gate fixed. For loop runs, one row per iteration. Skip the trivial and the self-evident.

A run is one agent session, including its later turns and any summary of it. A pickup, a replacement agent or a new session starts a new run. When a run adds to a log that already has rows, its first row has phase `start`, and so does its first row after another run's `start` row. So a run that comes back to a log in a later turn first reads the log's last rows to see whether another run wrote since. A `start` row names the `ts` range of the rows before it that this run did not write, and its evidence names this run (its session id). Use phase `start` for nothing else.

## Where it lives

By default the log is a working file, not committed. Keep it at `decisions.tsv` in the working directory, or `.audit/<task-slug>.tsv` when several efforts run at once, and keep it out of git.

Commit it only when the work is ambitious enough that a reviewer needs the trail to trust the result.

## Rules

- Append only. A wrong call gets a new row that supersedes it. Never edit or delete history.
- Prefer evidence that committed scripts produce (`/verify`, `scripts/ai/test.sh`, `sim.sh compare`) over one-off hand checks. See **principle-encode-lessons-in-structure**.

## Audit the log against the transcript

At the end of the run, before handing back, check that the log told the truth. Read this run's transcript, under this repo's directory only. Never glob across `~/.claude/projects/*/`. That reads unrelated private sessions.

```bash
python3 .claude/skills/recall/scripts/sessions.py find "<the opening words of this run's first prompt>"
python3 .claude/skills/recall/scripts/sessions.py digest <session id>
```

Walk this run's rows against what happened. This run's rows are each stretch that begins at one of its `start` rows (or at the first row, if this run created the log) and ends at the next `start` row of another run.

- Check that every row maps to a real decision or action.
- Check that each row's evidence resolves and shows what the row claims.
- A fork, pivot or abandoned approach that shaped the work but is not logged is a gap. Add it.

Correct the log, not the story. The audit never edits or removes a row, even an invented one. When a row records neither a real decision nor a real action, or its claim or evidence is wrong, add a row that supersedes it with what actually happened and a pointer that resolves. The audit does not check rows outside this run's stretches. If this run's own work shows one of them is wrong, supersede it like any wrong call.

## Second-model review of the trail

Before handing back, spawn a `general-purpose` subagent on a different Claude model from the one that did the work (`opus` when the work ran on `sonnet`, `sonnet` when it ran on `opus`). Self-review is not a substitute. Tell it to write nothing. It reads the log and the run's transcript, then flags what the person should look at. Not a redo of the work. A scan for what is weak or risky.

- Decisions logged with weak or missing evidence.
- Verification skipped, or claimed without proof in the transcript (a "works" with no build result, test run, `/verify` report or screenshot that was looked at).
- Choices that look risky in hindsight (premature, scope creep, a symptom papered over).
- Gaps the person would miss on a skim.

Every reply for a run that produced a trail ends with an **Attention** section. Its first line is the reviewer's model (`reviewed by <model>`). Then each flag, pointing at specific rows or moments. "No flags" is a valid value. The model name is not optional.

## Reading the trail

Read top to bottom, follow the evidence pointers, spot-check. GitHub renders a committed TSV as a table. `column -s$'\t' -t decisions.tsv` renders it in a terminal.

## Composing this skill

Other skills and playbooks route their audit trail here instead of inventing one. Name this skill and let it own the format. Don't restate the columns.
