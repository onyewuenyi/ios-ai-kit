# ios-ai-kit

A Claude Code workflow for iOS repositories in which "done" is proven on a real simulator and every change reaches `main` through a pull request. It uses only tools that ship with macOS and Xcode 27 (`xcodebuild`, `simctl`, `xcresulttool`, `swift-format`, `xcrun mcpbridge`, AVFoundation), the GitHub CLI, and Claude Code's own project config. Everything it adds is committed to your repo, so every teammate's Claude, and every cloud session, behaves the same way.

## Get it

**From the Claude Code plugin marketplace (recommended).** In Claude Code:

```
/plugin marketplace add onyewuenyi/ios-ai-kit
/plugin install ios-ai-kit@ios-ai-kit
```

Then, inside your iOS repo, run **`/ios-ai-kit:setup`**. It installs the kit into the repo, bootstraps this Mac, runs the doctor, lists the steps only you can take (below), and proposes the new files as a pull request. Run it again to upgrade.

**From GitHub.**

```bash
git clone https://github.com/onyewuenyi/ios-ai-kit ~/ios-ai-kit
python3 ~/ios-ai-kit/install.py /path/to/YourApp   # detects project/workspace, scheme, bundle id, deployment target
cd /path/to/YourApp && scripts/ai/bootstrap.sh     # once per Mac: toolchain, Apple's skills, simulator, smoke test
```

`git pull` in the clone and re-run `install.py` to upgrade.

Both routes install the same files. The plugin carries only the `setup` skill; the workflow itself lives in your repo (a plugin cannot ship permission rules, and a teammate or cloud session that never installed the plugin must get the same behavior).

## First run: the steps only you can do

The kit automates everything it can. These steps need a person, a browser, or a decision about your accounts. `scripts/ai/doctor.sh` checks each one it can see and prints the fix, so you can run it any time to see what is left.

| When | Step | Why it can't be automated | `doctor.sh` checks it |
|---|---|---|---|
| Once per Mac | Install Xcode 27 and select it: `sudo xcode-select -s /Applications/Xcode.app` | Needs your Apple ID and an admin password | yes |
| Once per Mac | `brew install gh && gh auth login` | Signs in to your GitHub account in a browser | yes |
| Once per repo, per Mac | Run `claude` in the repo once and choose **Yes** on "Do you trust the files in this folder?" | Claude Code has no flag for it, and Claude may not change its own permissions. Until then the committed permission rules are ignored (hooks still run) | yes |
| Once per repo (owner) | `scripts/ai/protect-main.sh` | Changes your repository's settings on GitHub. It adds a ruleset: changes reach the default branch only through pull requests, no force push, no deletion, for everyone including you and any agent. `--allow-direct-push` keeps only the last two | yes |
| Once per repo (owner) | `/web-setup` in Claude Code, or install the Claude GitHub App on the repo | Grants GitHub access to cloud sessions in a browser | no |
| Once per Mac (optional) | Xcode ▸ Settings ▸ Intelligence ▸ Model Context Protocol ▸ **Xcode Tools** on, and approve the agent when Xcode asks the first time `/verify` opens the project | An Xcode setting and an approval dialog only you can click. Without it, UI assertions are reported as skipped, never as passed | Xcode running: yes |

## How a change reaches `main`: always a pull request

1. Work and commit as usual, on any branch, even `main`.
2. `/verify` runs the gates and writes the report.
3. `scripts/ai/pr.sh` opens the pull request with that report as its description. Commits made on `main` move onto a new `claude/<topic>` branch first and your `main` goes back to `origin/main`, so nothing is lost and nothing reaches `main` directly. Run it again after more commits and it updates the same PR.
4. You review and merge on GitHub. Claude asks before `gh pr merge` and never merges its own PR.

A direct push to the default branch is refused three times over: the guard hook (with the reason and `pr.sh` as the way forward), the cloud gate in cloud sessions, and GitHub's ruleset from `protect-main.sh`, which is the one that holds for every tool and every person.

## The lead: work is done when it is merged

Starting work is not done; an open PR is not done. **`/lead`** reads every open PR you authored (`scripts/ai/prs.py`, a deterministic digest) and sorts it:

| Bucket | What lands there | Who acts |
|---|---|---|
| **Needs you** | ready to merge (verified at its head, green, mergeable, no open threads) · stalled · your review requested · fixes waiting to be pushed · a cloud task that never opened a PR | you, with the one command to run |
| **Needs work** | conflicts · failing checks · review threads · app code not verified at its head | the lead, on that PR's own branch |
| Healthy | checks running, a fresh draft | nobody: counted, never listed |
| Done | merged, closed or abandoned since you last looked | reported once |

It does the needs-work itself (`scripts/ai/worktree.sh pr <n>` checks out the PR's existing branch in its own worktree and simulator: it steers, it never respawns), including running `/verify` on cloud-authored PRs, which only a Mac can do. When a PR is merged or closed, `scripts/ai/worktree.sh prune` gives back its worktree, simulator and DerivedData (keeping, and naming, any with unpushed work). It never merges, closes, force-pushes or posts outside your terminal; `LEAD_COMMENT`, `LEAD_PUSH` and `LEAD_REBASE` in `.claude/ios.env` opt in. Leave **`/loop /lead`** running on a workday: it paces itself (about 10 minutes while checks run, 60 when all is healthy) and stays quiet unless something needs you.

## Delegating to cloud sessions

`scripts/ai/cloud.sh "<task>"` hands one unit that needs no Xcode (docs, scripts, String Catalogs, audits, mechanical refactors, Foundation-only logic) to a Claude Code cloud session: it adds a fixed footer (no xcodebuild, push your own branch, open a PR with a "Not verified here" list, never touch the default branch), Claude Code asks before it runs (an ask rule: it sends code off the Mac and costs money), and records the session so `/lead` follows it to a merged PR. `--branch <head>` continues an existing PR instead of opening a new one. The `delegate` playbook splits bigger requests into verifiable units and routes each to the cloud, a local worktree or the current session. Cloud sessions finish unattended because of the cloud gate (see **Security model**).

## Healthchecks

- **Session-start bearings** (a `SessionStart` hook): only what is off, in a few lines: commits on the default branch that never went through a PR, uncommitted work, HEAD unverified or failing, PRs that need you (from the lead's cached digest, with its age), doctor warnings, a stale healthcheck. Git and files only, under a second, silent when all is well.
- **`/friction`**: what keeps costing this repo's sessions time, read from its Claude Code transcripts and verify history: exact read-only commands no rule allows, rejected calls, repeated hook refusals, Stop-hook build failures, recurring compiler errors, flaky tests, gates whose median grew, and on Mondays oversized outputs, re-read files and token use. You pick; each accepted fix lands with a test, through a PR. `/lead` runs it quietly each weekday.
- **Status line** (opt-in per developer: `python3 install.py <repo> --statusline`, or `/ios-ai-kit:setup` and say yes): `⎇ claude/topic · ✓ verified 3171e3c · 2 PRs need you · 3 uncommitted`, always under the prompt. Git and files only, about 0.1 s; written to the gitignored `.claude/settings.local.json` and never over a status line you already have.
- **Verify history:** every gate and failing test of every `/verify`, per commit, shared by all worktrees (`python3 scripts/ai/history.py last | flips | stats`). It is how the lead knows a PR is verified at its head and how friction finds flakes.

## Playbooks, review and lessons

- **Playbooks:** `ios-loop` routes every non-trivial task to one whose steps end in evidence: bug fix, feature, UI pass, prototype arena (variants in worktrees, compared side by side), investigation, perf, hillclimb, schema change, release, device run, delegate, autonomous run, handoff. `principles.md` holds the eleven principles behind them, each with its trigger.
- **`/interrogate`:** one read-only reviewer per lens the diff can fail on (concurrency, persistence, lifecycle, extremes, accessibility, privacy and App Review, performance, slop), a second Claude model on the riskiest, and only findings it verified.
- **`/reflect`:** turns a session's lessons into the strongest structure that would have prevented them: a type, a test, a hook, a script, a screen line, a playbook step, a rule.
- **`/map`:** builds and refreshes `.claude/ios-screens.txt` from the app's own seams and its live accessibility labels; the visual gate refuses a screen whose seam the app no longer reads.

Every agent and skill states its job, what is not its job, and its one-line answer when there is nothing to report; `tests/standard.py` enforces it, along with "no script referenced that does not exist, no script that nothing uses".

## What it gives the repo

| | |
|---|---|
| **`/verify`** | Gates written up as a PR-ready report. 1 format. 2 build with **no new warnings** (the baseline is recorded from a clean build on first run). 3 tests, read from the `.xcresult`. 4 no launch-argument read outside `#if DEBUG`. 5 blast radius. 6 the **visual matrix**: each screen in `.claude/ios-screens.txt` at default, dark and AX5, plus **UI-hierarchy assertions** (`expect:` / `absent:`, matched against accessibility labels) through Xcode's device interaction. The sheets read `JUDGE` until someone looks; `history.py judge PASS|FAIL` records the verdict, and only then is the commit verified. 7, with `--release`, the **release gate**: the Release simulator build audited for submission blockers (advisory for signing; `scripts/ai/release.sh <App.xcarchive>` audits a real archive) (export compliance, icon, launch screen, iPad orientations, privacy manifests and required-reason APIs, usage strings, debug residue, launch-argument seams). Ends by offering `pr.sh`. |
| **`/lead`, `prs.py`** | Every open PR sorted by who has to act; the lead does the needs-work on each PR's own branch. |
| **`cloud.sh`** | One no-Xcode unit to a cloud session, tracked to a merged PR. |
| **Bearings, `/friction`, verify history** | What is off at session start; what keeps costing time; every gate of every run. |
| **Playbooks, `/interrogate`, `/reflect`, `/map`** | Evidence-ending playbooks; adversarial review; lessons into structure; an honest screen list. |
| **`pr.sh`** | The only way to `main`: branch if needed, push, open or update the PR, body from `/verify`. |
| **Stop hook** | A turn that changed code can't end on a broken build: format lint plus an incremental build, cached per change. It blocks once, never loops, and stays silent where there is no Xcode (cloud sessions). |
| **Guard hook** | Denies a push to the default branch, a simulator destination with no runtime, and `simctl … booted` when more than one simulator is booted. Asks before erasing every simulator or editing a committed Core Data model version. |
| **Cloud gate** | Cloud sessions run unattended to a pushed `claude/*` branch and an open PR; every other push, merge or approval-needing step is refused with a reason instead of stalling on a prompt. Silent locally. See **Security model**. |
| **One simulator per checkout** | Created on first use, recorded with its owning path, addressed by UDID. Worktrees, including Claude Code's own `--worktree`, never share a device. `destroy` refuses to delete another checkout's simulator. |
| **`ios-loop` skill** | The development loop, Xcode MCP versus shell (with Xcode 27's measured behavior), bug fixes, two-pass UI work, parallel worktrees, routing work to cloud sessions, and the PR step. |
| **UI assertions** | `xcui.py` launches the build the kit already made, by UDID, then attaches a *device-only* Xcode interaction session to read the live UI hierarchy. It doesn't use `InstallAndRun`: on a large project, Xcode dropped that session mid-build and kept the simulator locked to it. |
| **Agents** | `build-verify` (Haiku) returns only `file:line: message`. `ui-verify` judges the screenshots and drives Xcode's device interaction. `review-lens` reviews a diff through one lens, read-only. |
| **Scripts** | `scripts/ai/{build,test,check,verify,visual,release,sim,doctor,bootstrap,worktree,format,pr,protect-main,cloud}.sh`, plus `prs.py`, `history.py`, `friction.py`, `screens-drift.py`, `statusline.py`, `xcui.py`, `xcresult.py`, `blast-radius.py`, `audit-bundle.py`, `debug-fences.py`, `kit.py`, and `frames.swift` / `compare.swift`. |

**Upgrading is idempotent.** Kit-owned files are replaced (`scripts/ai/*`, `.claude/hooks/*`, every kit skill and agent, the Swift rule); change them in the kit, not in a repo. Team-owned files are only created when missing (`.claude/ios-screens.txt`, the PR template); `.claude/ios.env` gains new keys and never loses values; `docs/ai-workflow.md` is a managed block, refreshed around your own text. `.claude/settings.json` is merged (permissions unioned, an existing swift-format hook respected, wrong rules from earlier versions removed), `CLAUDE.md` gets a marked block replaced in place, and `.mcp.json`, `.gitignore` and `.worktreeinclude` are merged. A `.swift-format` matching the code's indentation is created when missing.

## Security model

Four layers; each says what it does NOT guarantee.

1. **Permission rules** (`.claude/settings.json`): pushes, `gh pr merge`, `rm -rf` and `.pbxproj` edits ask a human; secrets are denied to reads. They do not stop a human who approves the wrong thing, and they apply only once the folder is trusted.
2. **The guard hook** (`guard.py`, PreToolUse): denies a push to the default branch, and ambiguous simulator targets, everywhere. It fails open on its own errors.
3. **The cloud gate** (`cloud-gate.py`, a `PermissionRequest` hook). It runs only where a prompt would otherwise appear, and only in a cloud session (`CLAUDE_CODE_REMOTE=true`), where nobody is there to answer and an unanswered prompt stalls the session forever. It approves, for one call, a command made only of `git add/commit/status/diff/log/show/fetch/rev-parse`, `git push` of explicit `claude/*` refspecs to `origin` (flags limited to `-u`, `-q`, `-v`), `gh pr create/view/list/checks`, and `tail/head/wc/grep`. Everything else is refused with a reason the session acts on: the default branch, force, delete, `--all/--tags/--mirror`, a bare `git push`, `gh pr merge`, chained commands, substitution, heredocs, redirects to files, `git -C/-c`, env prefixes, every non-Bash prompt. It never overrides a deny rule and never grants beyond the one call; its parser fails closed; locally it prints nothing. Prefix and on/off: `CLOUD_BRANCH_PREFIX`, `CLOUD_PUBLISH` in `.claude/ios.env`.
4. **GitHub's ruleset** (`scripts/ai/protect-main.sh`): the only layer that holds for every tool and person, because GitHub enforces it. Needs a public repo, or GitHub Pro/Team for a private one; the script says so if not.

`scripts/ai/pr.sh` pushes without a prompt (it is one of the kit's own scripts, which the rules allow), and it can only push a non-default branch.

## Tested

`tests/run.sh` runs every suite with no simulator build (339 cases: the guard, the cloud gate, `pr.sh`, verify history, gate scope, the PR digest, delegation, bearings and the status line, friction, screen drift, the one-job standard and the installer), plus syntax checks on stock `/bin/bash` 3.2 and python3. `claude plugin validate .` passes for the plugin and the marketplace manifest. Proven live on a brand-new app and on a production app with about 1,230 tests:

- **Bootstrap:** from a fresh install to a passing smoke test.
- **`/verify`:** all gates. The visual gate caught a blank empty state every mechanical gate passed, and two text clips at the largest text size.
- **The release gate:** fails a fresh app on 3 real submission blockers.
- **The Stop hook:** blocked a broken build in a live session and showed the exact error.
- **Cloud sessions:** one ran to an open PR with no prompt; one told to push to `main` left it untouched and pushed its own branch.
- **Parallel worktrees:** two test runs at once, each on its own simulator.
- **Xcode device interaction:** start a session, launch, assert the hierarchy, in both directions.

## Migrating from ios-stack

ios-stack, the earlier plugin, is retired: everything worth keeping moved here. Its playbooks and principles are in `ios-loop`; `/ios-stack:interrogate` and `/ios-stack:reflect` are `/interrogate` and `/reflect`; `create-verify-skill` became `/map` (one verify path, the kit's `/verify`); its session bearings became the SessionStart hook; its evidence ledger became the verify history. Its turn-end guard, statusline, crash monitor and builder/verifier agents were dropped (the Stop hook, `sim.sh crashes` and `ui-verify` cover them). Uninstall it once the kit is installed: `claude plugin uninstall ios-stack --scope <user|project|local>`, the scope it was installed at (`doctor.sh` names it): both together run two sets of session and Stop hooks, and `doctor.sh` warns while it is still enabled.

## Requirements and limits

- **Machine:** macOS with Xcode 27 selected, python3 (ships with Xcode's command-line tools), the GitHub CLI for `pr.sh` and `protect-main.sh`.
- **Simulator only:** device-only behavior (push delivery, CloudKit between accounts, camera, performance on old hardware) is listed in the report as not verified.
- **Cloud sessions have no Xcode:** they do docs, scripts, String Catalogs and mechanical refactors, say "not compiled with Xcode", and their branch runs `/verify` on a Mac before it merges.
