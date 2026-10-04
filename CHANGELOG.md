# Changelog

## 0.6.0 (2026-10-03)

One idea to a merged PR, with an AI judge on the screenshots, and pstack ported to Claude Code and iOS. `tests/run.sh` now runs 530 cases.

- **`/ship "<idea>"`** runs the whole road: outcome and check, a branch from `origin/main`, the matching playbook, the changed screen added to the visual matrix, `/verify`, `pr.sh`, then `merge.sh`. Invoking it is consent to merge that one change; `--no-merge` stops at merge-ready.
- **An AI judge on the visual gate.** `scripts/ai/judge.py` sends each sheet to a separate, read-only Claude call with a fixed checklist, the intended change (`VERIFY_INTENT`, else the branch's commit subjects) and the app's conventions from `.claude/judge-notes.md`. The model only judges: the script requires a PASS or FAIL with evidence for every screen and records it through `history.py judge`, and anything else leaves the commit unverified. Bracketed on a real app: known-good sheets PASS, a known clip at the largest text size FAILs on the exact clipped words. `VISUAL_JUDGE=human` keeps judging by eye.
- **`scripts/ai/merge.sh <n> --yes [--wait <secs>]`** merges only a PR that `prs.py --check` calls merge-ready at its exact head, waits for running checks, confirms GitHub merged it, deletes the branch and fast-forwards the local default branch. Refused in cloud sessions and without `--yes`. `MERGE_METHOD` picks merge, squash or rebase.
- **pstack, ported** ([pstack](https://github.com/poteto/pstack) 0.15.9 by Lauren Tan, MIT; the full map is `docs/pstack-port.md`):
  - `ios-loop` is now the router pstack's poteto-mode is: non-negotiable triggers, a principles index, autonomy, subagents by Claude model role, how to write the reply, and 28 playbooks.
  - 28 `principle-<name>` skills (pstack's 24 in Swift, plus environment before code, extremes are the test, release is another app, additive data). They load only when cited. `principles.md` is retired.
  - New playbooks: refactoring, runtime forensics, trace forensics (Instruments, `.ips`, memgraph, MetricKit), visual parity, authoring a skill, eval, babysit, shipping, orchestrate, autopilot-full, autopilot-stack, multi-phase plan, opening a PR, worktree cleanup, session pickup and pause safely (replacing handoff). Bug fix, feature, perf, hillclimb, investigation, prototype and autonomous merged both versions.
  - New skills: `/how`, `/why`, `/architect` (with the eight design red flags in Swift), `/arena`, `/swarm`, `/figure-it-out`, `/correct`, `/benchmark-checklist`, `/blast-radius`, `/recall`, `/automate-me`, `/show-me-your-work`, `/tdd`, `/teach`, `/technical-writing`, `/unslop`, `/bro`, `/no-comments`, `swift-best-practices`. `/interrogate` gains a design lens and a lead judgment; `/reflect` merged both versions.
  - Agents: `ios-agent` (the default for playbook subagents) and `comment-sicko`.
  - `docs/guide/`: ten chapters, from setup to overnight runs.
  - Model roles in `.claude/ios.env`: `MODEL_JUDGMENT`, `MODEL_CODE`, `MODEL_FAST` (and `JUDGE_MODEL`); `/ios-ai-kit:setup` offers them.
- **Runs on macOS's own Python 3.9:** every kit Python file had used 3.10 type syntax at runtime, so `/usr/bin/python3` failed on `kit.py`. `tests/run.sh` now compiles and imports every module under it.
- **`/friction`** also reads sessions from sibling worktrees made by `worktree.sh` (it had admitted only `.claude/worktrees`).
- **The installer** derives the kit-owned list from the template, so a new skill can never be left un-upgraded, and removes retired files.
- **`tests/standard.py`** exempts principles from the one-job markers (they must be `disable-model-invocation`), checks every `principle-<name>` a doc cites, and covers references and the guide.

## 0.5.2 (2026-10-03)

An audit of the core flow: three read-only reviews (every doc and skill against the scripts, the Python, the shell), 48 findings verified, each fix with a test. `tests/run.sh` now runs 339 cases.

- **The visual gate tells the truth.** Captured sheets read `JUDGE` until someone looks; `scripts/ai/history.py judge PASS|FAIL "<what was seen>"` records the verdict, and only a judged pass counts as verified for `pr.sh`, the lead, the status line and the bearings. A `--no-tests` run never counts. The lead could previously call a UI PR merge-ready on sheets nobody opened.
- **Holes in the cloud gate closed:** a `#` could hide the rest of a command; `<(…)`, `>(…)` and `>|` passed as arguments; `head`/`grep` could read any file standalone; `git fetch --upload-pack` ran commands.
- **The guard stops breaking daily work:** `git stash push`, `git grep push`, `git commit -m push` on main are not pushes; `heads/main`, `@` and computed refs are.
- **Work that could be lost, no longer:** `worktree.sh pr` never resets an existing local branch; `pr.sh` on a detached HEAD never moves main; `remove` lets git refuse before the simulator goes; an untracked `.swift` makes a verify run dirty.
- **Silent exits named:** a second `.app` product, a gate that prints nothing, a build log without `error:`, a deleted Swift file in the Stop check, an apostrophe in a screens comment, an empty `expect:`, a failed screenshot, `export` lines in `ios.env`, paths with spaces.
- **First run and upgrades:** the installer prints only what changed and each next step as a bare command (a sentence had been pasted as a command); an existing `ios.env` seeds detection, a stale scheme there warns instead of aborting; kit hooks are replaced in place on upgrade; a rule the team removed stays removed; the screens template documents `#seen` and is stamped on install.
- **The lead:** also lists teammates' PRs that request your review; a cloud task whose PR exists is remembered as resolved; `LEAD_PUSH=1` pushes through `pr.sh`; `ui-verify` no longer uses `DeviceInteractionInstallAndRun` (the measured hang).
- **Docs:** `sim.sh record` runs for its whole duration, so every doc shows the background form; the PR template mirrors `report.md`; dangling names fixed (`install.sh`, `/doctor prompt-audit`, a principle title, a flag); `tests/standard.py` now also checks every `/skill`, principle title and script flag a doc names.

## 0.5.1 (2026-10-03)

Friction found by running the workflow on a real app and its real PRs, each fix with tests:

- **Gates check the whole branch.** Format and reach took only uncommitted changes, so a branch whose work was committed (before `pr.sh`, and every PR the lead verifies) checked nothing and passed. They now take everything since the branch left the default branch.
- **A busy build folder means wait or skip.** `build.sh` and `test.sh` wait for another xcodebuild on the same DerivedData; the Stop check skips. No more "database is locked" read as a failed build.
- **The guard reads written text as text.** A heredoc fed to `cat` or `tee` is not a push; one fed to `bash` still is.
- **`pr.sh` keeps a PR's description true:** a kit-written description is replaced by a fresh `/verify` report; a hand-written one is never touched.
- **Verified survives docs-only commits:** a PR verified before commits that touch no app code still counts as verified, and says so.
- **`worktree.sh prune`** returns merged and closed PRs' worktrees and simulators; `/lead` runs it.
- **A status line** (opt-in: `install.py --statusline`, or `/ios-ai-kit:setup`): branch, HEAD's verify state, PRs that need you.
- Smaller: `worktree.sh` leaves no stray temp file; `prs.py` names a missing GitHub remote; `doctor.sh` names the scope a leftover ios-stack was installed at; a Markdown note does not make a verify run dirty.

## 0.5.0 (2026-10-03)

Ideas from the Grok "Engineering Lead" and "Dr Eggbot" bots and from pstack, built as Claude Code only, and ios-stack folded in (now retired).

- **The lead.** `/lead` and `/loop /lead` own every open PR until it is merged, abandoned or taken back: `prs.py` sorts PRs into needs-you, needs-work, healthy and done, quiet unless something changed; the lead does the needs-work on each PR's own branch (`worktree.sh pr <n>`), verifies cloud-authored PRs on the Mac, and never merges, force-pushes or posts without opting in.
- **Delegation.** `cloud.sh` hands no-Xcode units to cloud sessions with a fixed footer and tracks them; the `delegate` playbook splits work into verifiable units.
- **Verify history.** Every gate and failing test of every `/verify`, per commit, in git's common dir (shared by worktrees, survives `rm -rf .build`); `history.py` reads it. `pr.sh` trusts a report only when it names the commit being proposed on a clean tree.
- **Healthchecks.** SessionStart bearings (only what is off, under a second); `/friction` over the repo's transcripts and verify history, applied only where the owner picks, each with a test; `doctor.sh` caches its warnings and flags a still-enabled ios-stack.
- **From ios-stack:** thirteen playbooks and `principles.md` under `ios-loop` (now a router), `/interrogate` with a read-only `review-lens` agent and a new slop lens, `/reflect`, and `/map` with `screens-drift.py` (the visual gate refuses a screen whose seam is gone).
- **The one-job standard.** Every agent and skill states its job, its anti-jobs and its quiet answer; `ui-verify` gets an explicit tools list (it could edit before); `tests/standard.py` enforces it plus no dangling or orphan scripts.
- **Installer.** `docs/ai-workflow.md` is a managed block (an unedited earlier version is replaced, an edited one is kept and named); `.claude/ios.env` upgrades add a comment only with the keys it describes; the kit's Python never writes `__pycache__` into a project, and installs gitignore it.

## 0.4.0 (2026-10-03)

Every change reaches the default branch through a pull request (`pr.sh`, the guard's deny, `protect-main.sh` requiring PRs by default); the cloud gate lets cloud sessions finish to a PR unattended; doctor checks trust and `gh` sign-in; the kit ships as a plugin with `/ios-ai-kit:setup` and a marketplace manifest.
