# Multi-phase or multi-PR plan

**You own the plan, not the code. The plan is a checklist an owner runs box by box and the operator audits from the evidence.** The plan is the deliverable. Do not implement.

1. **Decide it needs a plan.** A change of one or two files with an obvious approach skips the plan. Say so and stop. **Check.** The change spans more than one PR, or the approach is genuinely open.
2. **Settle open questions by prototype before you write.** Run `playbooks/prototype.md` for each. Keep the branch, the SHA and the comparison images for Appendix A. Ask the operator only about a product or preference call no run can settle, with options and your recommendation (principle-never-block-on-the-human). **Check.** Every open question has a prototype result or a parked operator question.
3. **Explore in subagents.** `Explore` for wide reads, `ios-agent` for anything that runs a build, each with an explicit `model` (principle-guard-the-context-window). Each returns file pointers, conventions, test commands, seams and entry points, never inlined dumps. **Check.** You hold pointers, not file contents.
4. **Fill the skeleton.** Copy the skeleton below into `$STATE_DIR/plans/<slug>.md` (the repo's `.git/ios-ai/plans/`, shared by every worktree) unless the operator names a path. Fill every placeholder. Keep every heading and sub-block in the order shown. One section per PR, and one PR is one change with its own evidence (principle-sequence-verifiable-units). Name the execution playbook in **How to read this**. Choose between `playbooks/autopilot-full.md` and `playbooks/autopilot-stack.md` by the rule at the end of `playbooks/autopilot-stack.md`. A standing program takes `playbooks/orchestrate.md`. **Check.** No `<placeholder>` remains.
5. **Write it under `/technical-writing`, then `/unslop`.** The body is one Diátaxis mode, how-to. Appendices hold explanation and reference. Each heading states the task or the finding. **Check.** No long dash, no curly quote, no mid-sentence colon.
6. **Check the plan against the rules.** Spawn one fresh subagent (`model: haiku`, or `MODEL_FAST`) with the plan path and the plan rules below, and ask for exactly two outputs. One line per PR section with its box count per sub-block, then one line per violation as `<file>:<line>: <rule number> <what is wrong>`, then `<n> PR sections, <m> problems`. It reports and never edits. Fix every line it prints, then run it again (principle-encode-lessons-in-structure). **Check.** The last run prints `0 problems`.
7. **Hand back.** Post the plan path and the checker's last output, then stop. Execution starts on the operator's explicit go, under the playbook the plan names. **Check.** Nothing was implemented.

## Plan rules

The checker applies these to everything outside code spans and fenced blocks.

1. Prose has no long dash, no curly quote, and no colon followed by a space and more text.
2. The plan opens with one `# ` title. The intro between the title and `## How to read this` is under ten non-empty lines.
3. `## How to read this` contains "One box is one unit of work", "names the evidence", "Check a box only when its evidence exists", "playbooks/", and the verification rule sentence.
4. `## Program checklist` has these `###` headings in this order. Arm the program, Spawn owners, PR mechanics, Verdict and merge, Boot recipe. Its text contains "git show origin/main:", "/loop 1h" and "status message".
5. At least one PR section sits between `## Program checklist` and `## Close the program`.
6. Each PR section has these bold sub-blocks in exactly this order. Depends on., Files., Build., You see., Verify, unit., Verify, live., Verify, perf., Review gate., Merge.
7. **Depends on.** names something (a PR id or "None"). **Files.**, **Build.**, **You see.**, **Verify, unit.** and **Merge.** each hold at least one `- [ ]` box.
8. **Verify, unit.**, **Verify, live.** and **Verify, perf.** each open with the verification rule sentence.
9. **Verify, live.** says "Ten lanes on `<model>` at the PR head" with a real model name, and holds boxes numbered `Lane 1.` to `Lane 10.`, each naming a screenshot as "Save `<file>`" and a predicate as "Pass when".
10. **Verify, perf.** holds four boxes in this order. Metric., Probe., Baseline., Rule.
11. **Review gate.** is either "None." with no boxes, or boxes whose text mentions a screenshot, a video and the operator.
12. After `## Close the program` only `## Appendix` sections follow, and one of them is Prototype evidence.

## Verification

Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked (principle-prove-it-works). That sentence is the verification rule, and every verification block opens with it.

- **Live.** Ten lanes at the PR head drive the app on the simulator, per `/swarm`. Each lane is one box with a concrete scenario, the screenshot it saves and its pass predicate. Lanes drive the app through a seam (`scripts/ai/sim.sh launch <args>`), a deep link (`scripts/ai/sim.sh openurl <url>`), `scripts/ai/xcui.py` assertions or the `ui-verify` agent, at the default and the largest text size where layout is involved. Lanes run in sequence on one simulator or in parallel worktrees, at most two or three at once on one Mac. One lane is the **regression lane against trunk**. It runs the same load-bearing scenario on trunk and on the head. If trunk lacks the feature, the lane records that and gates the behavior the diff adds plus the end state the user waits for.
- **Perf.** Dual-sided. Trunk and head both produce the named metric, measured the same way (Instruments or `xcrun xctrace`, `os_signpost` intervals, XCTest `measure`), interleaved, median and worst over at least five runs (principle-explain-the-number). If trunk lacks the feature, isolate the work the diff adds and give it an absolute budget, plus one for the end state the user waits for. Never claim a ratio between unlike scenarios. Simulator numbers are Mac numbers. A perf claim that matters names its device run (`playbooks/device-run.md`).
- **Review gate.** A PR that changes an interaction waits for the operator's review in chat, with screenshots and a recording, before merge. A PR that changes no interaction writes `**Review gate.** None. <PR id> is not review-gated.` and no boxes under it.
- **Surfaces.** A PR that touches two surfaces (the app and a widget, the app and a script) gets lanes on both. A surface with no driver is a risk in Appendix C, and its live block still says how each lane drives it.

## Skeleton

````markdown
# <Program> plan

<Under ten lines. What changes, for whom, the rule the program enforces, and the PR ids in order.>

## How to read this

One box is one unit of work. Every box names the evidence that checks it. A nested box is a sub-step of the box above it. Check a box only when its evidence exists, such as a file, a log line, a screenshot, a test run or a SHA. The body is a how-to. The appendices explain and record.

The program runs `.claude/skills/ios-loop/playbooks/<execution playbook>.md`. <Who merges, and which PR ids are the operator's items that stop at merge-ready.>

Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

## Program checklist

### Arm the program

- [ ] State the protocol and this plan to the operator, then stop. Start execution only on the operator's explicit go.
- [ ] Read these from trunk at program start. Re-read them at every tick.
  - [ ] `git show origin/main:.claude/skills/ios-loop/playbooks/<execution playbook>.md`
  - [ ] `git show origin/main:.claude/skills/swarm/SKILL.md`
  - [ ] `git show origin/main:.claude/agents/ui-verify.md`
  - [ ] `git show origin/main:.claude/skills/ios-loop/playbooks/opening-a-pr.md`
  - [ ] `git show origin/main:.claude/skills/<each other skill the program uses>/SKILL.md`
- [ ] On the operator's go, arm the audit tick as `/loop 1h` with the tick prompt below. Never leave the cadence to memory.
- [ ] Use this tick prompt, verbatim. "Re-read the execution playbook from trunk. Audit the operation against it and fix drift in this tick. Probe every active lane and judge progress by side effects only. Stand down a stuck lane and dispatch its replacement now. Then post a short status message to the operator in chat only when the audit found a tracked change that no earlier status message reported, such as a PR opened, a code-ready head, a round launched or closed, a verdict, a merge, a stuck agent and the action taken, a blocker added or cleared, or a decision only the operator can make. Name every such change and nothing else. Do not repeat a table, the merged list, or an unchanged blocker. If the audit found none, end the turn with no reply text. Either way, log this tick's row in your decision trail. The row names the items reported, or none."
- [ ] On the operator's hold or stand-down, send every owner a zero-writes order at once.

### Spawn owners

- [ ] Spawn one owner per PR with the full lifecycle the execution playbook names.
- [ ] Follow this dependency graph. Start dependent work only after its parent merges, or base it on the parent branch when the execution playbook stacks.
  - [ ] <PR id> and <PR id> are independent and first. Both branch from `main`.
  - [ ] <PR id> after <PR id>.
- [ ] Hold the file boundaries. <PR id or class> touches only `<glob>`.
- [ ] Hold the review gate. <PR ids> change an interaction. They wait for the operator's review in chat with screenshots and a recording before merge.

### PR mechanics, for every PR

- [ ] Open the PR ready, never draft, with `scripts/ai/pr.sh` per **Opening a PR**. A stack child then targets its parent with `gh pr edit <n> --base <parent-branch>`.
- [ ] Run `scripts/ai/check.sh` before the PR-facing push.
- [ ] Run `/unslop` and `/no-comments` on the diff before review.
- [ ] Triage every review comment per `.claude/skills/ios-loop/references/review-triage.md`.
- [ ] Merge the default branch into the branch before the code-ready report and babysit. Keep that base in fix rounds. Merge it again only at merge prep, on a conflict with trunk, or on a CI failure caused by a change on trunk. Never rebase, never force-push.

### Verdict and merge, for every PR

- [ ] At the code-ready head SHA and at each later push that changes the patch, run the swarm per `.claude/skills/swarm/SKILL.md`. One gates lane (`scripts/ai/verify.sh` with the AI judge). The ten live lanes from the PR's **Verify, live** block. The perf lane from its **Verify, perf** block. Two or more audit lanes (`review-lens`), each with its own lens, that read the diff and the receipts and distrust the PR body. The root audits the receipts in the merge-ready report before the verdict.
- [ ] Clean only when every lane is `PASS`. Findings go back to the owner, including a defect a lane filed as a note. A new head gets a fresh swarm and a fresh verdict, except for results that stay valid under the patch-id rule in `.claude/skills/ios-loop/playbooks/shipping.md`.
- [ ] <The merge or append rule from the execution playbook, with the patch-id rule from shipping.>

### Boot recipe, for every live lane

Each live lane runs at the PR head in its own worktree with its own simulator.

- [ ] `scripts/ai/worktree.sh pr <n>`, then confirm `git rev-parse HEAD` is the head SHA under test.
- [ ] `scripts/ai/build.sh`, `scripts/ai/sim.sh install`, `scripts/ai/sim.sh guard`.
- [ ] <The seam or deep link that reaches the state, with `scripts/ai/sim.sh launch <args>`. Name the read-only diagnostics.>
- [ ] Save every screenshot with `scripts/ai/sim.sh shot .build/swarm/<pr-id>/lane-<n>/<slug>.png` and return the paths with the report.

## <Task as a verb phrase> (<PR id>)

**Depends on.** <PR id, or None.>

**Files.**

- [ ] Edit `<path>`.
- [ ] Create `<path>`.
- [ ] Delete `<path>`.

**Build.**

- [ ] <One change. Name the symbol and the file.>

**You see.**

- [ ] <One observable result, with the exact log line or screen state.>

**Verify, unit.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

- [ ] <Test file and the case it gains.> Run `scripts/ai/test.sh -only-testing:<Target/Suite/test()>`.

**Verify, live.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked. Ten lanes on `<model>` at the PR head, per the boot recipe.

- [ ] Lane 1. Regression lane against trunk. Run <the same load-bearing scenario> at trunk and head. If trunk lacks the feature, record that and gate <the behavior the diff adds plus the end state the user waits for>. Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 2. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 3. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 4. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 5. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 6. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 7. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 8. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 9. <Scenario.> Save `<slug>.png`. Pass when <predicate>.
- [ ] Lane 10. <Scenario.> Save `<slug>.png`. Pass when <predicate>.

**Verify, perf.** Tests alone are not sufficient verification. A PR is verified only when its unit, live, and perf boxes are all checked.

- [ ] Metric. <What is measured at both trunk and head. If trunk lacks the feature, also name the diff-added work and the end-to-end state the user waits for.>
- [ ] Probe. <The Instruments template, `xctrace` command, signpost or XCTest `measure`, run at trunk and at the head, interleaved. Both sides must produce the metric.>
- [ ] Baseline. Record the trunk <value> first.
- [ ] Rule. <Head against trunk, with the number that fails. If the scenarios differ, add absolute budgets for the diff-added work and the user-visible end state instead of an invalid ratio.>

**Review gate.** The operator reviews before merge.

- [ ] Copy lane <n> screenshots into `<media path>/<pr-id>-review-<slug>.png`.
- [ ] Record a 30 to 60 second video of the change with `scripts/ai/sim.sh record <media path>/<pr-id>-review.mov 45`.
- [ ] Post the screenshots and the video in chat. Stop at merge-ready. Wait for the operator.

**Merge.**

- [ ] Root's clean verdict at the exact head SHA.
- [ ] Review comments triaged.
- [ ] Default branch merged in after the verdict, patch-id unchanged, `/verify` passed at the new head.
- [ ] <The owner lands its own PR with `scripts/ai/merge.sh <n> --yes`, or the root appends it to the base-branch stack and the operator lands it bottom-up.>

## Close the program

- [ ] Every box above is checked with its evidence.
- [ ] Reply to the operator with the report the execution playbook names.

## Appendix A. Prototype evidence

<Each open question a prototype answered, with the branch, the SHA and the comparison image paths. Each question that stays unproven.>

## Appendix B. Alternatives rejected

<Each approach weighed and why it lost.>

## Appendix C. Risks

<Each risk with the PR it lands in and what the owner watches.>

## Appendix D. Links and reading list

<Docs to read before editing. Which PRs get `/how` and `/interrogate`. The trail per `/show-me-your-work`.>
````

**Reply:** the plan path, the PR ids with their dependencies and the review-gated set, what the prototypes proved and what stays unproven, and the checker's last output.
