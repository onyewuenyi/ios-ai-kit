---
name: swarm
description: Fan out N parallel Claude subagents, drain them, and return one report. Shapes are coverage matrices (every screen at every text size, every lens, every OS), races (N workers on one brief, first pass or best of), gauntlets (one change through many independent checks) and exploration partitions (a codebase split into slices). Use for /swarm, "swarm this", or any parallel coverage, race, gauntlet or exploration.
argument-hint: "[the goal] [N] [first pass | rank all | best-of]"
disable-model-invocation: true
---

# Swarm

**Job:** run N independent workers against one goal and return one consolidated report in which every required slice has an evidenced result or a named gap.

**Not my job:** synthesizing competing attempts into one artifact (`/arena`) · following delegated work to merged PRs (`/lead`) · splitting a coupled change across workers (the delegate playbook in `ios-loop` keeps coupled code in one session).

**When there is nothing to report:** "PASS on every slice", with the table of slices and the evidence each one recorded.

Fan out N parallel workers. They cover separate slices, race the same brief, or both. You wait, aggregate, and return one report.

## Start

Open a todo list with one entry per phase before launching anything.

1. Frame
2. Fan out
3. Aggregate
4. Report

## Phase A: Frame

1. **State the done predicate** and the report the swarm must return.
2. **Choose the shape.**
   - **Coverage matrix:** the slices are the cells of a grid (screen × text size × appearance, file × lens, test plan × OS). Every cell needs a result.
   - **Exploration partition:** a codebase or a question split into disjoint slices (by module, by folder, by feature), one worker each.
   - **Gauntlet:** one change, many independent checks, each a worker (a build, the tests, a blast radius, a visual pass, a privacy audit).
   - **Race:** N workers on an identical brief. Declare the rule before spawning: `first pass` (stop the others with TaskStop once one proves the predicate), `rank all`, or `best-of`.
   - Mixed shapes are fine. Name each part.
3. **Set N** from the user or derive it from the shape. N is total workers, not a concurrency limit.
4. **Pick the worker model** through the Agent tool's `model`. Default `sonnet` (`MODEL_CODE` in `.claude/ios.env` overrides it). Use `haiku` (`MODEL_FAST`) for mechanical sweeps (grep a pattern, read a file per slice), `opus` (`MODEL_JUDGMENT`) when each slice needs judgment. If the Agent tool rejects a model, use `sonnet` and say so. For a model race, name each arm's model up front.
5. **Give each worker its own writable output** when it writes. A worker that builds or drives a simulator gets its own worktree (`scripts/ai/worktree.sh new swarm-<slug>-<n>`), so it has its own DerivedData and simulator. Read-only workers share the checkout.
6. **Pin what is measured.** When workers verify or measure commits, each brief names the exact SHAs. A measurement brief also names the method (sample count, what one sample is, the order). The worker records both in its result. Measurements follow `/benchmark-checklist`.

## Phase B: Fan out

Spawn all N in one message, one Agent call each, with `run_in_background: true` and the step 4 model. Pick `subagent_type` by the work:

- `Explore` for read-only search slices.
- `review-lens` for a lens of a review gauntlet.
- `ui-verify` for screens on a simulator, `build-verify` for a build or test slice.
- `ios-agent` for slices that change code, in their own worktree.
- `general-purpose` otherwise.

Work that needs no Xcode and should outlive this session (docs, scripts, String Catalogs, a Foundation-only audit) can go to a cloud session instead: `scripts/ai/cloud.sh "<brief>"`. Its result arrives as a PR that `/lead` follows, not in this report, so use it only for slices whose deliverable is a PR.

Every brief stands alone. Include the goal, the scope, the exact slice or race arm, the worktree path if any, how to verify, and what to report. Results use `PASS`, `ISSUES` or `BLOCKED`, with evidence (a `file:line`, a test id, a screenshot path, a number with its method). A worker that can prove a defect reports `ISSUES` and lists every issue it can prove, not only the first.

If a worker drops out, proceed with N-1 and note it.

## Phase C: Aggregate

Read the results. Check the evidence, not the summary. Open the screenshot and read the cited line. Drop a result that does not record the SHAs and method its brief names, and respawn that worker once. After a second miss, record a gap. A gap is not a pass.

- **Coverage and partitions:** every required slice needs a result.
- **Gauntlets:** the change passes only if every check passes.
- **Races:** apply the rule declared up front.

Do not paste raw worker output. Keep a compact result table, one-line evidenced issues, and explicit gaps or dropouts. Remove any worktrees the swarm created with `scripts/ai/worktree.sh remove <path>`, which also deletes their simulators.

## Phase D: Report

Return one consolidated report in chat.

**Reply:** the shape and N, the result table (slice, worker model, PASS / ISSUES / BLOCKED, evidence), the issue one-liners, the gaps and dropouts, and the race rule when used.
