---
name: arena
description: Spawn N parallel attempts at the same task on Claude models, each in its own worktree with its own simulator, read every candidate, pick a base, graft the strongest parts of the others into it, and verify the result. Use for /arena, "arena this", "throw it in the arena", or when one attempt at a non-trivial artifact (a design sketch, a tricky fix, a view) would lock in the wrong shape.
argument-hint: "[the task] [N]"
disable-model-invocation: true
---

# Arena

**Job:** turn N independent attempts at one task into one synthesized artifact that is better than the best single attempt, and say what came from where.

**Not my job:** splitting work into different slices (`/swarm`) · a fork a screenshot settles alone (the prototype playbook in `ios-loop`) · merging or opening the PR (`scripts/ai/pr.sh`, then the owner) · averaging candidates that disagree because the task was vague.

**When there is nothing to report:** "The candidates converged", the shared shape, and the verification result. No graft was needed.

Fan out N parallel attempts at the same task. Read every candidate end to end. Pick the strongest as the base. Graft the best ideas from the others into it. Verify the synthesized result.

## Start

Open a todo list with one entry per phase before launching anything.

1. Frame
2. Fan out
3. Cross-judge
4. Pick
5. Graft
6. Verify

## Phase A: Frame

The N candidates receive the same prompt, so the prompt is the contract.

1. **State the artifact** each candidate produces: a design package, a patch on a branch, a SwiftUI view, a test suite, a doc.
2. **Derive the rubric.** State what success looks like for this task, then turn it into 3 to 6 concrete gradeable criteria ("fits at the largest accessibility size with no clipping", "no `@unchecked Sendable`", "the store keeps one writer", "`scripts/ai/test.sh` passes"). The rubric is the picker's tool in Phase D. Candidates see only the task.
3. **Pick the runners.** Claude models through the Agent tool's `model` parameter. Default: one each on `opus`, `sonnet` and `fable`. `.claude/ios.env` may override seats with `MODEL_JUDGMENT` (the `opus` seat), `MODEL_CODE` (the `sonnet` seat) and `MODEL_FAST`. If the Agent tool rejects a model, run that seat on `opus` and say so. Spawn more when the arena covers several design directions. Use the same model N times when the work is generation-bound rather than judgment-sensitive.
4. **Isolate each candidate,** per `principle-separate-before-serializing-shared-state`.
   - **Anything that builds or runs:** `scripts/ai/worktree.sh new arena-<slug>-<n>` per candidate. Each worktree gets its own branch, its own DerivedData (`.build/dd`) and its own simulator on its first `scripts/ai/build.sh`, so builds and installs never collide. Never share a simulator between candidates.
   - **Prose or a sketch only:** a per-candidate folder in the scratchpad.
   - Run `scripts/ai/worktree.sh list` after creating them, and pass each candidate its absolute path.

## Phase B: Fan out

Spawn all N in one message, one Agent call each, with `run_in_background: true`, `subagent_type: "ios-agent"` for code (it follows the `ios-loop` skill) or `general-purpose` for prose, and the seat's `model`.

Every prompt stands alone. It holds the task, the path to the shared grounding, the candidate's absolute worktree or folder, and these rules:

- Work only inside your worktree. Use absolute paths. Build and test there with `scripts/ai/build.sh` and `scripts/ai/test.sh`, which pick that worktree's simulator.
- Drive the simulator only through `scripts/ai/sim.sh` from your worktree, never `booted` or a device name.
- Commit on your branch. Do not push. Do not open a PR.
- Produce the artifact and a short rationale that names the alternatives you considered and what you rejected.
- Report the branch, the commit, the gate results you ran, and anything not verified.

If a candidate fails to produce output, proceed with N-1 and note the dropout in the synthesis record.

## Phase C: Cross-judge

After all candidates complete, spawn one read-only judge on a Claude model different from the one you are running on (`opus` if you are not, else `sonnet`). Use `subagent_type: "Plan"`, which cannot edit. It sees the rubric and the candidates by label and path (`git -C <worktree> diff <base>...HEAD`, or the folder), scores each criterion, and recommends a base with its reasons. It runs while you read in Phase D. Never spawn it while candidates are still writing.

## Phase D: Pick a base

Read every candidate end to end before picking.

- Score each candidate against the rubric criterion by criterion, not on holistic feel.
- Run the evidence the rubric names on each candidate's own worktree. A UI candidate gets screenshots captured identically (same seed, same launch seam, `large` and the largest accessibility size), side by side with `scripts/ai/sim.sh compare out.png a=<a.png> b=<b.png> c=<c.png>`. Look at the image.
- Compare with the cross-judge. Agreement confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding.

Pick the base a future maintainer can extend most easily without breaking invariants. When two feel tied, prefer the cleaner boundary or the smaller API, per `principle-laziness-protocol`.

Record the pick and the reason in a short synthesis note alongside the base, including the cross-judge's verdict.

## Phase E: Graft

Walk each losing candidate once more and name what is worth porting into the base. The signal is usually one or two things per candidate, not most of it.

Fold each graft in by hand on the base's branch, per `principle-redesign-from-first-principles`. Never cherry-pick a whole commit or paste mechanically. The result has to stay coherent under one mental model.

Record what was grafted, from which candidate, and what was rejected and why.

When the N candidates converge on one shape, that is a strong agreement signal. Note it and ship the consensus shape. No graft is needed. When they diverge wildly, Phase A was under-specified. Reframe and re-run rather than averaging the divergence.

## Phase F: Verify

The synthesized artifact faces the same scrutiny as any other output, per `principle-prove-it-works`. For code, that is `/verify` on the base worktree, and `python3 scripts/ai/history.py judge PASS|FAIL` after you look at its visual sheets.

If verification surfaces a problem the arena did not catch, either Phase A was wrong (reframe and re-run) or one candidate caught it and you missed the graft (back to Phase E). Do not paper over it.

Then clean up. `scripts/ai/worktree.sh remove <path>` for each losing worktree, which also deletes its simulator. Keep the base until its PR is open.

## Outputs

One synthesized artifact on one branch. One short synthesis note beside it, naming the base, the grafts (with source candidate), the rejections, the dropouts, and the verification result.

**Reply:** the base and why, the grafts by source, the rejections, the dropouts, the cross-judge's verdict, the verification result, and the branch or path of the result.
