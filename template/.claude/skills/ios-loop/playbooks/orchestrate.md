# Orchestrate

**You own the program, never the code. Author briefs, drain the queue, keep the frontier green, decide.** For a whole project handed to one standing coordinator session. It runs over days, spans many PRs and dozens of subagents, and the owner checks in twice a day instead of every five minutes. One task driven to a predicate is `playbooks/autonomous.md`. A handful of independent units is `playbooks/delegate.md`. A queue where each PR has its own owner through merge is `playbooks/autopilot-full.md`. Route here only when the work outlives any single agent.

Ceremony scales with the program. On cheap near-identical units, collapse it as each section says.

Three rules carry the rest.

- Completions are queue events, not interrupts.
- Every spawn carries the standing orders verbatim.
- The brief is the product. A vague brief fails quietly, because a worker cannot ask you a question.

## Roles and placement

- **Coordinator (this session).** Local, on the Mac. Frames, authors briefs, drains the inbox, owns the owner's report, makes judgment calls. It never authors or edits code. Conflict resolution, base merges and code changes are always units. Landing a verified PR is bookkeeping the coordinator does itself, through `scripts/ai/merge.sh` per `playbooks/shipping.md`, and only under a landing grant in the standing orders.
- **Local worker.** The Agent tool with `isolation: "worktree"` and `run_in_background: true`. Each gets its own worktree, DerivedData and simulator automatically. This is the default for anything that builds, runs the simulator, reads transcripts or needs this Mac's signing. A Mac runs two or three simulator-heavy workers at once, so that is the in-flight cap for local units.
- **Cloud worker.** `scripts/ai/cloud.sh "<brief>"` for a unit that needs no Xcode (docs, scripts, String Catalogs, audits, mechanical refactors a local build will check, Foundation-only logic). It cannot build, so its PR is not done until a local verifier runs `/verify` at its head. Launching a cloud session needs the owner's yes, so the program's framing asks for it once for the whole program.
- **Verifier.** A fresh local subagent that did not write the unit, on a different Claude model from its worker (`opus` against `sonnet`, or the reverse). One writer per worktree or branch (principle-separate-before-serializing-shared-state).
- **Models.** `MODEL_CODE` for routine units, `MODEL_JUDGMENT` (default `opus`) for the hardest code and every judgment, `MODEL_FAST` for mechanical work, all from `.claude/ios.env`, passed as the Agent tool's `model`.

Depth stays coordinator and worker. When a program outgrows what one coordinator can drain, split it into tracks, each its own program under its own coordinator session in its own worktree (`scripts/ai/worktree.sh new <track>`, then `claude` there), sharing the store. Cut tracks per project. Build, landing and verification are common cuts, not a required shape.

## The store

Create `$STATE_DIR/orchestrate/<project-slug>/`. `$STATE_DIR` is the repo's `.git/ios-ai/`, shared by every worktree and never committed. Cloud workers cannot read it, so their briefs inline what they need or point at repo paths. Every file has exactly one writer, the coordinator. Plain TSV and Markdown, readable without any tool.

- `preferences.md` is the standing-orders register. Numbered lines, one constraint each (model policy, verification bar, landing grant, forbidden paths, escalation policy). Paste it verbatim into every spawn. When you catch yourself restating an instruction, append the line before you act (principle-encode-lessons-in-structure).
- `overview.md` is the durable PR and issue record. Append. Never rewrite it per event.
- `units.tsv` has one row per unit. Id, track, state, route (local or cloud), branch, PR, head SHA, brief path. Update rows in place.
- `frontier.json` is the computed merge frontier, per Stack safety.
- `ledger.tsv` is the verification ledger, per Verification.
- `inbox.tsv` holds completion pointers (time, agent, unit, status, report path). `gates.md` parks owner gates (question, options, default on no answer).
- `decisions.tsv` is the trail, per `/show-me-your-work`.
- `status.md` is derived from `units.tsv` and `ledger.tsv` at each drain, never hand-maintained.

## The brief

Your prompts to agents are your only product. Every spawn carries all of it. A field you cannot fill is a unit you have not scoped yet.

```
GOAL         one sentence, the outcome, executable by a stranger with no chat access
SCOPE        paths this unit may write; paths it may not; its worktree or branch
CONTEXT      pointers to files and PRs; upstream reports pasted in full when this unit
             depends on them, because workers cannot see siblings
ACCEPTANCE   checkable criteria, one per line (a test passes, a screen shows X at AX5)
VERIFY       exact commands (scripts/ai/build.sh, scripts/ai/test.sh -only-testing:…,
             scripts/ai/verify.sh, a seam for scripts/ai/sim.sh launch), plus known traps
TIMEBOX      rough cap on runtime; on expiry, return partial findings and stop
FORBIDDEN    no push to the default branch, no force-push, no rebase, no merge, no hand
             edit of *.pbxproj, no simctl booted, no fixes outside scope, plus unit bans
REPORT       status, branch, head SHA, PR, gate results, what you actually ran,
             deviations, "Not verified here", suggested follow-ups
STANDING     <preferences.md pasted verbatim>
```

Size the brief to the unit. A one-command unit gets the template collapsed to a paragraph that still names goal, scope, the verify command and the report shape. A cloud brief goes through `cloud.sh`, which appends the no-Xcode footer. A dependency is a context relay, not just ordering. Missing fields are a refuse-to-spawn condition. Audit one sampled brief per wave, alongside the wave, never as a gate in front of it. A failing brief stops the next refill and fixes the template. Never chain a resume onto an old brief. Spawn fresh with consolidated scope (the original brief, every later directive, the prior report and branch).

## Steps

1. **Frame.** State the done predicate as something countable ("all 40 units merged, each ledger-verified `sim-verified` or better"). Quantify scope (units, rough effort, expected PRs, wall-clock budget). If one agent could finish inside that budget, stop and run `playbooks/autonomous.md` instead, with no store and no register. Schedule landing against the budget. By about 70% of it, stop spawning and land what is verified. A contested decomposition or a one-way door goes through `/arena` before the pilot. Present the framing once, including the cloud and landing grants it needs. Reversible prep proceeds without waiting. **Check.** The predicate is countable and the owner has seen the framing.
2. **Install the store.** Create the files above, open the trail per `/show-me-your-work`, write the standing orders before any spawn, and seed `frontier.json` from `python3 scripts/ai/prs.py --json` and `gh pr list --json number,headRefName,baseRefName,headRefOid`. **Check.** `preferences.md` exists and every open PR the program owns has a `units.tsv` row.
3. **Pilot.** Push one unit through the whole path. Brief, worker, verification, ledger row, PR, merge. The pilot exists to falsify the brief template, the verify recipe and the unit size while that costs one agent instead of thirty. Fix the contract from pilot evidence before any fan-out. On programs of near-identical cheap units, the first unit is the pilot, run as a normal unit, and fan-out starts the moment it lands. **Check.** The pilot unit is merged with a ledger row at its merged head, or the contract changed because of what it showed.
4. **Scale.** Spawn a rolling window of workers up to the in-flight cap (two or three local, more in the cloud), refilling as each finishes. Blocking batches pay for the slowest child of every batch. Recompute ready work after each drain. Relay upstream reports into downstream briefs. Siblings talk only through you. **Check.** In-flight count never exceeds the cap, and every running agent has a `units.tsv` row.
5. **Drain** at every drain point, per Queue and drain. **Check.** The inbox is empty after the drain and `status.md` is regenerated.
6. **Land continuously.** Integration starts with the first verified unit and runs alongside the remaining waves, through `playbooks/shipping.md`. Keep the frontier green before upper work. Advance `frontier.json` only on a merge or a reported new head SHA. **Check.** Every merged PR has a ledger row for its merged head SHA.
7. **Close.** Drain the final inbox, reconcile every spawned agent to a terminal row (done, abandoned, zombie-reconciled), confirm the predicate on the real artifact (principle-prove-it-works), confirm every landed PR has a verdict for its merged head, audit the trail per `/show-me-your-work`, and encode recurring corrections into `preferences.md` or the brief template. Leave the store intact. It is the postmortem. **Check.** The predicate count from `units.tsv` matches `gh pr list --state merged` for the program's PRs.

## Queue and drain

- On a completion notification, append a row to `inbox.tsv` and return to what you were doing. Never review a diff inline. A completion that needs review becomes a verifier unit.
- Drain in batches at four points. The end of a critical section, a frontier wake (`/loop` in dynamic mode, with a long heartbeat fallback), a track rollup, and before an owner report. Arrivals during a drain wait for the next one.
- Critical sections you finish first. Authoring a brief, a base merge, a conflict decision, writing a gate, updating the ledger or the frontier.
- Each drain classifies every pointer (landed, needs-verify, failed, zombie, noise), updates `units.tsv` and `ledger.tsv`, regenerates `status.md`, then spawns the next wave in one message.
- Account for every spawned child. Each one arrived, was respawned, or had its scope explicitly absorbed. Silently redoing a missing child's work hides both the wasted spend and the coverage gap.
- A drain turn ends with three lines. Counts against the states, what changed, gates open.

## Stack safety

- The frontier is computed, never narrated. Recompute `frontier.json` from `gh` after every merge and base change. Ordered PR list, branches, head SHAs, a generation number, the lowest unmerged PR.
- Workers never merge, rebase or force-push. A base that moved is merged into the branch (`git merge origin/<base>`) by the unit that owns the branch, as its own unit.
- Babysitters follow `playbooks/babysit.md`, one per PR or stack, scoped to one frontier generation. They report conflicts in a stack rather than resolving them.
- Closing or retargeting a PR goes through the coordinator only. Closing a base PR orphans every PR above it.
- One retro check follows merged PRs for reverts, post-merge CI breaks and orphaned follow-ups.

## Verification

Scale verification to the unit. When VERIFY is a single cheap command, the worker runs it and reports the output, and the coordinator spot-checks the receipts against `python3 scripts/ai/history.py last <sha>`. A dedicated verifier is for units whose verification is expensive, judgment-laden or high blast radius (anything visual, persistence, sync, concurrency, release settings). A verifier whose whole product would be rerunning one command is ceremony.

`ledger.tsv` has one row per verdict, keyed by PR number plus head SHA. The verdicts, strongest first.

- `device-verified`. Proven on a physical device per `playbooks/device-run.md`.
- `sim-verified`. `scripts/ai/verify.sh` passed with the visual judged, and the behavior was driven on the simulator.
- `unit-test-verified`. Tests cover the behavior, nothing was driven.
- `build-only`. It compiles. Not enough for behavioral work.
- `verifier-blocked`. Not a pass. Respawn when the environment heals (`scripts/ai/doctor.sh`).
- `verifier-failed`. Gets a fix unit, not a re-verify.

CI green is an input to a verdict, not a verdict. A worker may self-report, and a verifier overrides it on the same key. A new head SHA voids the row. The ledger answers "was this verified", not memory and not the transcript.

A unit is done only when its output is outside the agent. The worker pushed its branch, the verifier wrote its ledger row, the receipts are in the store. Work that exists only in a dead worktree was never done.

## Liveness and failure

- Never resume an agent to check on it. Probe read-only. The ledger, `units.tsv`, `python3 scripts/ai/prs.py --json`, `git ls-remote origin <branch>`, the cloud session link `/lead` tracks.
- A silent death gets a synthetic postmortem row in the inbox (unit, failure mode, last evidence, options). Replan on evidence as it arrives. Never wait for full quiescence.
- Retry by mode. Context or turn cap, respawn with smaller scope. Network drop, retry as is. Tool error, retry on a different model. Environment (a simulator that cannot spawn, a stale toolchain), `scripts/ai/doctor.sh` before any retry. Unknown, retry once. Two retries, then abandon the unit and replan around it.
- A zombie that returns hours late reconciles against the current frontier and ledger before anything is accepted. Salvage unique findings through a fresh unit, never a blind merge.
- When continued spawning would produce garbage across the program (bad upstream output, broken acceptance, dead infrastructure), write a stop line at the top of `preferences.md`, let in-flight work finish, fix the cause, clear it.
- Bound your own retries the same way. After a few consecutive tool failures, write a terminal handoff per `playbooks/pause-safely.md` and end the run.
- After this session ends or restarts, local background agents are gone and cloud sessions are not. Re-read the standing orders and `units.tsv`, recompute the frontier, reattach cloud work by branch and PR, respawn local units from their stored briefs plus current state, drain, resume.

## Escalation

Reaches the owner, batched into `status.md` rather than per item. Irreversible actions (deleting user data, deploying a CloudKit schema to Production, an App Store Connect upload, closing someone else's PR), genuine product or preference calls no experiment settles, a standing order that contradicts observed reality, and a program-level dead end that survived a replan. Park each as a `gates.md` entry before asking, and route work around it (principle-never-block-on-the-human).

Never reaches the owner. Frontier nudges, base merges, retries, CI flake triage, review-thread triage, format fixes, scope the brief already forbids, and "should I keep going". When in doubt, act and log.

Mid-run discoveries fix only what blocks the frontier. Everything else parks as a follow-up. At this fan-out a small scope leak multiplies into PRs nobody asked for.

**Reply:** at checkpoints and at close, the predicate and the count against it from `units.tsv` and `ledger.tsv`, the tracks and what each landed, the frontier (PR list with head SHAs), a verdict summary, what was abandoned and why, the gates awaiting the owner (the only asks), the store path and the trail path, with PR links. Numbers come from the tables, not from narrative.
