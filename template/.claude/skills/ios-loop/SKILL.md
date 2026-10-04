---
name: ios-loop
description: The iOS development loop and playbook router for this repo. Build, test, run and verify on this checkout's own simulator, route the task to its playbook (bug fix, feature, refactor, perf, forensics, UI pass, schema, release, PR babysitting, autonomous runs), cite the principles that shaped each decision, and prove the change with screenshots or Xcode's device interaction. Use when building, running, testing or debugging the app, for "does it work", "fix this bug", "build this feature", a UI pass, parallel work, or a cloud-session question.
---

# iOS loop

**Job:** take one change from idea to a proven, proposed PR on this checkout's own simulator.

**Not my job:** merging · pushing to the default branch · editing `*.pbxproj` by hand or build settings the task did not ask for · following a PR after it opens (`/lead` does) · reviewing someone else's diff (`/interrogate`).

**When there is nothing to report:** the gate results and the PR link, nothing more.

Every change goes through the same loop, one logical change per build. Your claim that something works is not evidence: a build result, a test run, a hierarchy assertion or a screenshot you looked at is.

## Non-negotiables

Each trigger names the skill or playbook it routes to. In the reply, name each principle that shaped a decision and the choice it changed. Cite only principles whose `principle-<name>` skill you read this session.

- Nontrivial change, an architecture decision, or "are we sure?" → `/how` first.
- About to ask the person "which approach" or "what should this do" → classify it first. A fact you could observe by running something (behavior, layout, timing, whether an eval separates) is not theirs to answer: settle it with `playbooks/prototype.md`. Ask only a real product or preference call (`principle-never-block-on-the-human`).
- Any code → name the data shape first (`principle-model-the-domain`).
- Code crossing a function boundary → `/architect` before implementing.
- Parallel fan-out → `/swarm` (coverage, races, gauntlets, partitions). A design or code bakeoff → `/arena`.
- Contested design, or a risky diff before it ships → `/interrogate`.
- Nontrivial multi-step → write the throughput checkpoint (`playbooks/feature.md`, step 3).
- Any prose (the reply, a doc, a PR body, a commit message) → `/unslop`; docs and PR bodies also `/technical-writing`.
- Before review → `/no-comments`. Before commit → the `slop` lens of `/interrogate` on your own diff when it is more than a few lines.
- A screen changed → prove it on the simulator, never on the code alone (`principle-prove-it-works`). A bug → reproduce it yourself on the surface the person saw.
- A number you measured (a speedup, a regression, an eval score) → `/benchmark-checklist` before you report or act on it.
- Any PR-status request ("check on PR 12", "get it green") → `playbooks/babysit.md`, or `/lead` for every open PR. Asked to land a green stack → `playbooks/shipping.md`. One idea to a merged PR → `/ship`.
- A broken skill or script mid-task → fix it in its own PR. Never work around it silently.
- Long, autonomous or multi-phase work → a decision trail with `/show-me-your-work`.
- The same correction twice → `/correct`, or `/reflect` at the end of a session.

## Principles

Read the `principle-<name>` skill in full before you cite it. Each line says when it applies.

**Core**
- `principle-laziness-protocol`. Sizing a diff, or tempted by a new abstraction or layer. The smallest change that solves it.
- `principle-foundational-thinking`. Before logic: the types, the persisted model, scaffold before feature.
- `principle-redesign-from-first-principles`. A new requirement in an old design. Redesign as if it had been there from day one.
- `principle-attack-the-premise`. Two fixes that share one premise failed the same check. Census the actors, then question the premise.
- `principle-subtract-before-you-add`. Before an addition or rewrite. Remove dead weight first; never the person's data.
- `principle-minimize-reader-load`. Code that is hard to trace. Collapse one-caller wrappers and forwarding view models.
- `principle-outcome-oriented-execution`. A planned migration. Converge on the target; no throwaway compatibility states.
- `principle-experience-first`. Product or scope tradeoffs. The person's experience over implementation convenience.
- `principle-exhaust-the-design-space`. A new interaction with no precedent. Two or three variants, compared side by side.
- `principle-build-the-lever`. Nontrivial work. Build the script, generator or test that does or proves it.

**Architecture**
- `principle-model-the-domain`. Stateful or branchy logic. An enum, reducer or typed model instead of scattered conditionals.
- `principle-boundary-discipline`. Validation, decoding, errors, framework adapters. Guards at the boundary, pure logic inside.
- `principle-type-system-discipline`. Designing a type or signature. Illegal states unrepresentable, wrapped identifiers, exhaustive switches.
- `principle-make-operations-idempotent`. Launch, migration, seeding, sync, background tasks. The same end state after a crash or a retry.
- `principle-migrate-callers-then-delete-legacy-apis`. A new internal API with old callers. Migrate and delete in one wave.
- `principle-separate-before-serializing-shared-state`. Two actors, contexts or sessions writing one thing. Remove the sharing first.

**Verification**
- `principle-prove-it-works`. Before "done". The real app on the simulator, not "it compiles".
- `principle-fix-root-causes`. Debugging. Reproduce with a rate; trigger, masking condition, symptom.
- `principle-sequence-verifiable-units`. Multi-step work. Small units, each ending in a check.
- `principle-test-behavior-not-implementation`. Writing or keeping a test. Call it as its users do; assert literal values.
- `principle-explain-the-number`. Before trusting a measurement. Find its limiter; rule out that it measured something else.

**Delegation and meta**
- `principle-guard-the-context-window`. Large outputs, long files, fan-out. Bulk goes to subagents; pass paths, not payloads.
- `principle-never-block-on-the-human`. Tempted to ask about reversible work. Do it, show it, let them steer.
- `principle-encode-lessons-in-structure`. Writing the same instruction twice. A type, test, hook or gate instead.

**iOS**
- `principle-environment-before-code`. A crash, hang or nonsense error. Doctor, guard and the installed binary before the code.
- `principle-extremes-are-the-test`. Any screen. The largest text size, dark, the small phone and the iPad, empty and huge data.
- `principle-release-is-another-app`. Anything that ships. DEBUG seams, entitlements and the archive are proven on the Release build.
- `principle-additive-data`. Models, stores, sync, deletes. Additive versions, migration proven on a real old store, back up before a destructive path.

## Autonomy

**Just do it.** Reversible work proceeds without asking: edits, builds, tests, simulators, worktrees, local commits, a PR through `scripts/ai/pr.sh`.

**Always pause** for what cannot be taken back: a merge (except `/ship`, whose invocation is consent for that one change), a force push, deleting the person's data or a branch with unmerged work, a CloudKit schema deploy, an App Store submission, a message to another person.

**Session overrides.** "Don't stop", "going to bed", "run until done" → `playbooks/autonomous.md`, and keep going.

**No is an acceptable answer.** Asked whether to do something, give your real judgment. Candor over agreement.

## Subagents

- **`ios-agent` for every subagent a playbook step spawns** (code-writing delegates, helpers). Routed skills (`/how`, `/why`, `/interrogate`, `/arena`, `/swarm`, `/reflect`) set their own agent types; respect them. Read-only work goes to `Explore`, builds to `build-verify`, screens to `ui-verify`, review to `review-lens`.
- **Models are Claude models,** chosen with the Agent `model` parameter by role from `.claude/ios.env`. `MODEL_JUDGMENT` (default `opus`) for design, review and the hardest changes; `MODEL_CODE` (default `sonnet`) for ordinary code; `MODEL_FAST` (default `haiku`) for mechanical edits and sweeps. An empty role keeps the default.
- **Defaults for every Agent call.** `run_in_background: true` when you have other work, file paths instead of pasted context, and an isolated worktree for anything that builds (one simulator each).
- **You own every subagent's work.** Read its diff and write your own summary. A second opinion is the same prompt on a different Claude model; agreement is high signal.
- **Fresh subagents by default.** A fix round, a retry or the next item goes to a fresh subagent with the consolidated brief (the original task, every later directive, the prior report and branch). Resume an existing one only when the work needs state that lives there: its uncommitted changes, its running simulator.

## Writing the reply

Write it clean while drafting; a cleanup pass afterwards does not remove these patterns.

- Short declarative sentences. One thought each.
- No long-dash character. No colon as a mid-sentence connector; a colon before a list is fine.
- Terse never drops content. Every section the playbook's **Reply** names stays.
- Lead with what changes for the person using the app, then what the next engineer inherits.
- Never fabricate a link, path or citation. Link only what you produced or read this session.
- Every claim carries its evidence or its label in the same sentence: measured, inferred or guess. Never hand the person a check you could run.

## Comments

The same rule as the reply. Keep a comment only for a non-obvious *why* the code cannot show. No phase-narrating comments in tests or scripts; the assertion message documents the step.

## The loop

1. **Context.** `CLAUDE.md` is loaded. Run `scripts/ai/doctor.sh` if anything looks off. A broken simulator runtime or a stale toolchain looks exactly like an app bug.
2. **Locate and propose.** Grep and Glob find the files. State the smallest diff you plan, and why, before editing.
3. **Edit.** Edit and Write for existing files. A NEW file: with synchronized folders, Write it into the target's folder and it compiles; with explicit groups, add it through `XcodeWrite` (or in Xcode) so it gets target membership. Never hand-edit `*.pbxproj`.
4. **Build.** Run `scripts/ai/build.sh`. It prints only errors, new warnings and one summary line; the full log is in `.build/build.log`. For huge failures, hand the build to the `build-verify` agent.
5. **Fix.**
   - Fix the minimal cause and rebuild.
   - When an API is in doubt, consult Apple's exported skills (`swiftui-specialist`, `swiftui-whats-new-27`, …) or `DocumentationSearch`. Never guess.
   - When an error makes no sense, `rm -rf .build/dd` and rebuild before believing it.
6. **Test.**
   - Run `scripts/ai/test.sh [-only-testing:Target/Suite/test()]`. It reads the `.xcresult`, not the log.
   - A Swift Testing function id needs `()`.
   - "Nothing ran" is a failure, not a pass.
7. **Verify on the surface.**
   - Use the `ui-verify` agent. It prefers Xcode's device interaction (taps, plus assertions on the UI hierarchy) and falls back to `scripts/ai/visual.sh`, which takes screenshots at default, dark and the largest text size.
   - Run `python3 scripts/ai/blast-radius.py <files>` to list every screen the change reaches, and verify those, not just the one you edited.
8. **Gate.** `/verify` runs every gate. "Done" means it passed, and the report lists what was not verified.
9. **Commit.** One commit per logical change. The message says why, not only what.
10. **Propose.** Run `scripts/ai/pr.sh`. It never pushes to the default branch: commits made there move onto a new branch, which it pushes and opens as a PR, with `/verify`'s report as the body when it is fresh. A second run after more commits updates the same PR. Leave the merge to the owner.

## Xcode MCP or shell

- **Use the Xcode MCP tools (`mcp__xcode__*`) for:**
  - structured builds and tests: `BuildProject`, `GetBuildLog`, `RunSomeTests`;
  - previews: `RenderPreview`;
  - docs: `DocumentationSearch`;
  - project edits that keep target membership: `XcodeWrite`, `XcodeMV`, `XcodeRM`, `AddInfoPlist`, `AddEntitlement`;
  - device interaction.
- **Measured behavior (Xcode 27.0):**
  - `XcodeOpenWorkspace` opens the project. The first open is what asks the person to approve the agent.
  - Address the project by the `workspaceIdentifier` that `XcodeListWorkspaces` or `XcodeOpenWorkspace` returns. A path is rejected.
  - There is no `XcodeListWindows`. Match by `workspacePath` in `XcodeListWorkspaces`.
  - `DeviceInteractionStartWorkspaceSession` accepts `deviceIdentifier` = this checkout's UDID (`scripts/ai/sim.sh udid`). Always pass it, so Xcode never picks another session's device.
  - Taps, typing and captures go through `DeviceInteractionSynthesize`, and Xcode requires them to run in a subagent: use `ui-verify`.
  - End every session with `DeviceInteractionEndSession`.
- **Fixed checks:** `scripts/ai/xcui.py --udid … --container … --bundle … --args=<launch args> --expect "<label>"` asserts labels in the live UI hierarchy in one command. `/verify` runs it for every `expect:` in `.claude/ios-screens.txt`.
- **Everything also works from the shell.** Worktrees and parallel sessions use the shell scripts, or open their own workspace in Xcode.

## Simulators

- **Each checkout has its own simulator,** created on first build and recorded in `.claude/ios.local.env`.
- **Address it by UDID:**
  - `scripts/ai/sim.sh udid | install | launch <args> | shot <png> | size <category> | appearance dark | record <out.mov> <seconds> | frames <in.mov> <out.png> | compare <out.png> <a.png> <b.png…> | guard | crashes <epoch>`.
  - Never use `booted`, and never a bare device name. The guard hook blocks both when they're ambiguous.
- **Before believing a crash or a hang,** run `scripts/ai/sim.sh guard` (a plain launch must stay alive) and `scripts/ai/sim.sh crashes <epoch>`. Some traps write no report, so also check `sim.sh alive`.
- **Motion:** `record` runs for its whole duration, so start it in the background, then launch: `scripts/ai/sim.sh record out.mov 8 & sleep 1; scripts/ai/sim.sh launch -Flag; wait`. Then `scripts/ai/sim.sh frames out.mov sheet.png` gives a numbered strip; read it frame by frame.

## Playbooks

A task that is more than one obvious edit gets a playbook. Open a todo list whose first items are the playbook's steps, copied verbatim (paths relative to this skill), before any task-specific items. A skipped step stays as `skip: <reason>`. Every playbook that changes code ends with `playbooks/opening-a-pr.md`.

A large or cross-cutting effort, or work the person steps away from, goes to `/figure-it-out` even when a narrower playbook fits; so does a task no playbook fits. A standing multi-day program goes to Orchestrate.

| Playbook | When | File |
|---|---|---|
| Investigation | A read-only question: how does X work, why is Y so, should we do X or Y | `playbooks/investigation.md` |
| Bug fix | A defect to reproduce, root-cause and fix | `playbooks/bug-fix.md` |
| Feature | New or changed behavior, from a named data shape | `playbooks/feature.md` |
| Refactoring | Structure changes, behavior does not: rename, extract, move, dedupe | `playbooks/refactoring.md` |
| UI pass | Design, layout, motion or accessibility audit of a surface (pass 2 of UI work) | `playbooks/ui-pass.md` |
| Prototype arena | A fork a screenshot or a run can settle: throwaway variants, compared side by side | `playbooks/prototype.md` |
| Visual parity | Pixel-exact equivalence: a restyle or a port that must look the same | `playbooks/visual-parity.md` |
| Perf | A measured slowness: launch, scroll, hitch, memory, energy | `playbooks/perf.md` |
| Hillclimb | Move one metric against a baseline over many attempts | `playbooks/hillclimb.md` |
| Runtime forensics | Diagnose a live hang, spin, leak or glitch with Instruments; the deliverable is a diagnosis | `playbooks/runtime-forensics.md` |
| Trace forensics | Diagnose a captured `.trace`, `.ips`, spindump, memgraph or MetricKit report | `playbooks/trace-forensics.md` |
| Schema change | Core Data or SwiftData model, migration, CloudKit schema | `playbooks/schema-change.md` |
| Release | Archive, audit, submit, TestFlight, App Review prep | `playbooks/release.md` |
| Device run | Anything only a physical device can prove | `playbooks/device-run.md` |
| Authoring a skill | Writing or changing a skill, playbook, agent or CLAUDE.md rule | `playbooks/authoring-a-skill.md` |
| Eval | A/B a skill or prompt change before promoting it | `playbooks/eval.md` |
| Opening a PR | The end of every playbook that changes code | `playbooks/opening-a-pr.md` |
| Babysit | One PR or stack to merge-ready: conflicts, threads, checks | `playbooks/babysit.md` |
| Shipping | Verify a green stack per PR and land the verified run | `playbooks/shipping.md` |
| Delegate | Work bigger than one change, split across sessions | `playbooks/delegate.md` |
| Multi-phase plan | Work that spans phases or stacked PRs; the plan is the deliverable | `playbooks/multi-phase-plan.md` |
| Autonomous run | "Run until done", overnight, `/loop` until a predicate | `playbooks/autonomous.md` |
| Autopilot-full | A queue of independent ideas, each `/ship`ped to merged | `playbooks/autopilot-full.md` |
| Autopilot-stack | A queue built and verified as one stack the owner lands | `playbooks/autopilot-stack.md` |
| Orchestrate | A standing project for one coordinator: many PRs, many subagents, days | `playbooks/orchestrate.md` |
| Session pickup | Resuming another session's work from a branch, transcript or cloud URL | `playbooks/session-pickup.md` |
| Pause safely | Stopping in-flight work so a cold session can resume it | `playbooks/pause-safely.md` |
| Worktree cleanup | Reclaiming disk: merged worktrees, their simulators and DerivedData | `playbooks/worktree-cleanup.md` |

## Parallel work

- **Splitting a request across sessions:** `playbooks/delegate.md`. Every unit is tracked to a merged PR by `/lead`.
- **Limits:** two or three sessions at once. Each gets its own worktree (`claude --worktree <name>`, or `scripts/ai/worktree.sh new <name>`), its own `.build/dd` and its own simulator, all automatic.
- **Worktree contents:**
  - Worktrees start from your current HEAD (`worktree.baseRef: "head"`).
  - Gitignored files the build needs are listed in `.worktreeinclude`.
- **Cleanup:** remove with `scripts/ai/worktree.sh remove <path>`, which also deletes that worktree's simulator.

## Cloud sessions (no Xcode there)

**Route to the cloud** (`scripts/ai/cloud.sh "<task>"`: it adds the no-Xcode footer and `/lead` tracks the session to a merged PR) only work that needs no Xcode:
- docs, README, changelog;
- scripts and CI config;
- String Catalog edits;
- audits and triage of pasted logs;
- mechanical refactors that a local build will then check;
- Foundation-only package logic.

**In a cloud session:**
- never run `xcodebuild` or `simctl`;
- say "not compiled with Xcode";
- list every unverified item;
- commit, push your own branch with `git push -u origin claude/<name>` (explicit remote and branch), and open a PR with `gh pr create`.
- Nobody is there to answer a permission prompt, so the cloud gate answers: it approves exactly that publish shape, and refuses anything else (pushing to the default branch, force, delete, merge, `rm -rf`, an edit that needs approval) with a reason. Follow the reason; never retry the same thing in another form. Anything you could not do goes in the report as not done.

**Back on the Mac:** that branch runs `/verify` before it merges.

## Reporting

Every reply that claims a change works names its evidence: the gate results, screenshot or frame-strip paths, test counts. It also says what was NOT verified: device-only behavior such as real notification delivery, push, camera or performance on older hardware.
