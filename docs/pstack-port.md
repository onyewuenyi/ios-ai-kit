# Porting pstack to iOS and Claude Code

ios-ai-kit 0.6 absorbs [pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT, © 2026 Lauren Tan; upstream commit `e43c7ee`, 0.15.9): its method, reframed for iOS development with Claude Code agents. pstack brings the method (playbooks, principles, design, review, correction). The kit brings the iOS evidence engine (a simulator per checkout, `/verify`, the AI judge, `pr.sh`, `merge.sh`, the lead). One product, one install.

This file is the contract every ported file follows, and the table that accounts for every pstack file.

## Reframing rules

**Platform: Claude Code only.**
- `Task` → the Agent tool. `subagent_type` names are the kit's agents (`ios-agent`, `review-lens`, `ui-verify`, `build-verify`, `comment-sicko`) or Claude Code's (`Explore`, `Plan`, `general-purpose`).
- Models: Claude only. pstack's multi-vendor runners (Grok, GPT) become Claude models through the Agent tool's `model` parameter: `opus` for judgment, design and the hardest code; `sonnet` for routine code and second opinions; `haiku` for mechanical work. "A second opinion is the same prompt against a different model" stays true, among Claude models. Per-role overrides live in `.claude/ios.env` (`MODEL_JUDGMENT`, `MODEL_CODE`, `MODEL_FAST`), set by `/ios-ai-kit:setup`, never in a Cursor rule.
- `AskQuestion` → `AskUserQuestion`. Cursor rules (`.mdc`) → `.claude/rules/*.md` or the CLAUDE.md block. Cursor built-ins (`create-skill`, `deslop`, `control-ui`, `control-cli`, babysit) → the kit's own skills (`authoring-a-skill` playbook, `/unslop` + `/no-comments`, `ui-verify` + `scripts/ai/sim.sh` + `xcui.py`, `/lead`).
- Cursor cloud and background agents → Claude Code cloud sessions (`scripts/ai/cloud.sh`), local worktrees (`scripts/ai/worktree.sh`), `/loop`, `run_in_background`, Monitor. Origin CLI → `gh`. Bugbot / agentic security review → GitHub review comments and Claude Code's code review; same skeptical triage.
- Transcripts (`/recall`, `/automate-me`, `/reflect`, `/correct`) are Claude Code's: `~/.claude/projects/<repo path with every non-alphanumeric as ->/*.jsonl`. Parse them the way `scripts/ai/friction.py` does.

**Domain: iOS.**
- Examples are Swift, SwiftUI, UIKit, Core Data, SwiftData, Swift Testing, XCTest, Xcode, Instruments. No TypeScript, Node, React or browser examples remain.
- Surfaces: the browser and Electron become the simulator and the device. Driving the app = `scripts/ai/sim.sh` (launch seams, deep links), `scripts/ai/xcui.py` (UI hierarchy assertions), the `ui-verify` agent, XCUITest. Screenshots, frame sheets and `sim.sh compare` are the visual evidence.
- Performance and forensics: Instruments and `xcrun xctrace` (Time Profiler, Allocations, Leaks, Hangs, Energy), `os_signpost`, MetricKit, `memgraph` / `leaks` / `vmmap` / `heap`, spindumps, sysdiagnose, `.ips` crash reports (`sim.sh crashes`), XCTest `measure`. Simulator numbers are Mac numbers: confirm on a device.
- Release and data: the kit's release gate, App Review guidelines, Core Data/SwiftData migrations, CloudKit.

**The kit is the evidence engine.** Ported text routes through it, never around it: `/verify` (and `history.py judge`), `pr.sh` to open or update a PR, `merge.sh` to land one, `prs.py` and `/lead` for PR state, `worktree.sh` for isolation, `cloud.sh` for delegation, `friction.py` for transcript evidence. Never `xcodebuild` with a simulator by name, never `simctl … booted`, never a push to the default branch.

**Voice.** pstack's: short declarative sentences, one thought each; no long dash; no colon as a mid-sentence connector; every claim carries its evidence or its label (measured, inferred, guess). Keep pstack's rigor and its specific rules; cut what only made sense in Cursor.

**Shape.**
- Every skill keeps the one-job markers the kit's test enforces: `**Job:**`, `**Not my job:**`, `**When there is nothing to report:**`. Principle skills are exempt; they keep pstack's shape (rule, why, pattern, test).
- Principles ship as one skill each (`principle-<name>`, `disable-model-invocation: true`), as pstack does. Evals will decide whether they move to reference files; nothing else may depend on them being skills (cite them by name; read them by path `.claude/skills/principle-<name>/SKILL.md`).
- Skill descriptions under 600 characters. Every `scripts/ai/…` path, flag, `/skill` and principle a file names must exist (`tests/standard.py` checks).
- A ported file credits nothing inline; the credit is in `NOTICE.md` and the README.

## Mapping

Every pstack file, and what it became. "Port" keeps the content and reframes it; "merge" folds it into a kit piece that already does the job; "drop" says why.

### Router and agents

| pstack | Kit | How |
|---|---|---|
| `poteto-mode/SKILL.md` | `ios-loop/SKILL.md` | Port: non-negotiables, principles index, autonomy, subagents, writing the reply, comments, playbook router. Keeps the kit's loop, MCP-or-shell, simulator rules. |
| `poteto-mode/references/bugbot-triage.md` | `ios-loop/references/review-triage.md` | Port: triage of review comments (GitHub, Claude Code review). |
| `poteto-mode/scripts/*` (`bootstrap.ts`, `check-plan.mjs`, `orch`, `watch-pr`, `worktree-audit.sh`) | `scripts/ai/` | Merge: `watch-pr` → `prs.py` + `/lead`; `worktree-audit.sh` → `worktree.sh prune` + `sim.sh`; `check-plan.mjs` → a plan check inside `multi-phase-plan.md`; `orch`, `bootstrap.ts` → `orchestrate.md` uses Agent + worktrees + `prs.py` instead of a Node orchestrator. |
| `agents/poteto-agent.md` | `agents/ios-agent.md` | Port: the default worker subagent, following `ios-loop`. |
| `agents/comment-sicko.md` | `agents/comment-sicko.md` | Port: read-only comment reviewer, Swift. |

### Playbooks (`ios-loop/playbooks/`)

| pstack | Kit | How |
|---|---|---|
| investigation | investigation | Merge both. |
| bug-fix | bug-fix | Merge both. |
| perf-issue | perf | Merge both, with `/benchmark-checklist`. |
| hillclimb | hillclimb | Merge both. |
| runtime-forensics | runtime-forensics | Port: hangs, leaks, spins, energy, from live Instruments, `memgraph`, `log stream`. |
| trace-forensics | trace-forensics | Port: `.trace`, `.ips`, spindump, sysdiagnose, memgraph handed over after the fact. |
| feature | feature | Merge both; data shape first; `/architect` for anything crossing a boundary. |
| refactoring | refactoring | Port. |
| prototype | prototype | Merge both (arena of variants in worktrees, `sim.sh compare`). |
| visual-parity | visual-parity | Port: pixel parity on the simulator at the kit's sizes. |
| authoring-a-skill | authoring-a-skill | Port: writing a SKILL.md for this kit and the one-job standard. |
| eval | eval | Port: `claude plugin eval` and A/B runs of a skill change. |
| babysit | babysit | Port, on `/lead`, `prs.py`, `worktree.sh pr`. |
| shipping | shipping | Port, on `merge.sh` and the AI judge. |
| autonomous-run | autonomous | Merge both. |
| orchestrate | orchestrate | Port: a standing program under one coordinator, Claude subagents and cloud sessions. |
| autopilot-full | autopilot-full | Port: a queue of PRs to merged, one owner each, each verified before merge (`/ship` per item). |
| autopilot-stack | autopilot-stack | Port: a verified stack the operator lands. |
| session-pickup, pause-safely | session-pickup, pause-safely | Port, replacing the kit's `handoff.md`. |
| multi-phase-plan | multi-phase-plan | Port. |
| worktree-cleanup | worktree-cleanup | Port, on `worktree.sh prune` and simulator cleanup. |
| opening-a-pr | opening-a-pr | Port, on `pr.sh` and the verify report. |
| (kit) ui-pass, schema-change, release, device-run, delegate | unchanged | iOS-only; delegate cross-links orchestrate and swarm. |

### Skills

| pstack | Kit | How |
|---|---|---|
| architect (+ references) | architect | Port: Swift sketches, Claude-model runners, design red flags with Swift examples. |
| arena | arena | Port: N attempts in worktrees, Claude models, base selection and grafting. |
| swarm | swarm | Port: coverage matrices and gauntlets with Claude subagents. |
| interrogate (+ references) | interrogate | Merge: the kit's lenses plus pstack's references; add a `design` lens. |
| figure-it-out | figure-it-out | Port. |
| correct | correct | Port, plus the rule table and friction's evidence. |
| benchmark-checklist | benchmark-checklist | Port for iOS: Instruments, Release builds, device vs simulator. |
| blast-radius | blast-radius | Merge: a skill over `scripts/ai/blast-radius.py`. |
| how (+ references) | how | Port: how a subsystem works, Swift and Xcode projects. |
| why (+ references) | why | Port: evidence for why something is the way it is (git history, PRs, issues, MCP sources available in Claude Code). |
| recall | recall | Port: rebuild context from Claude Code transcripts. |
| reflect (+ references) | reflect | Merge both. |
| automate-me | automate-me | Port: draft a personal mode skill from Claude Code transcripts. |
| show-me-your-work (+ scripts) | show-me-your-work | Port: the decision trail TSV. |
| tdd | tdd | Port: Swift Testing / XCTest. |
| teach | teach | Port. |
| technical-writing | technical-writing | Port. |
| unslop | unslop | Port. |
| bro | bro | Port. |
| no-comments | no-comments | Port, with `comment-sicko`. |
| typescript-best-practices (+ references) | swift-best-practices | Rewrite for Swift 6: value types, enums with payloads, exhaustive switch, Sendable and actors, `@MainActor` ownership, `@Observable`, Codable at the boundary, access control. |
| create-verification-skill, maintain-verification-skill | map | Merge: the kit verifies through `/verify` and `.claude/ios-screens.txt`; `/map` creates it and `/map refresh` maintains it. |
| setup-pstack | ios-ai-kit:setup | Merge: model roles (`MODEL_*`) in `.claude/ios.env`. |
| make-bot-ui | none | Drop: builds dashboards for Grok Bot webhooks; no Claude Code equivalent is needed for this workflow. A Claude artifact over the lead's digest is a possible later addition. |
| 24 principle skills | 24 principle skills, plus the kit's iOS principles | Port each; the kit's iOS-only principles (environment before code, extremes are the test, release is another app, additive data) become principle skills too. |

### Elsewhere

| pstack | Kit | How |
|---|---|---|
| `docs/guide/` (10 chapters) | `docs/guide/` | Port: the user guide, reframed. |
| `automations/benny` | none, for now | Deferred: Cursor automations triaging Slack bug reports. The Claude Code equivalent is a scheduled routine over GitHub issues; it needs an issue source the kit does not have yet. |
| `.cursor-plugin/plugin.json`, `assets/` | `.claude-plugin/` | Merge into the kit's manifest. |
