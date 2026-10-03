# ios-ai-kit

A Claude Code setup for iOS repositories in which "done" is proven on a real simulator. It uses only tools that ship with macOS and Xcode 27 (`xcodebuild`, `simctl`, `xcresulttool`, `swift-format`, `xcrun mcpbridge`, AVFoundation), plus Claude Code's own project config. Everything it adds is committed to the repo, so every teammate's Claude behaves the same way.

## Install into any iOS project

```bash
python3 ~/Projects/ios-ai-kit/install.py /path/to/YourApp    # detects project/workspace, scheme, bundle id, deployment target
cd /path/to/YourApp && scripts/ai/bootstrap.sh               # once per Mac: toolchain, Apple's skills, simulator, smoke test
```

**Re-run `install.py` to upgrade.** It's idempotent:
- Kit-owned files are updated: `scripts/ai/*`, `.claude/hooks/*`, the `ios-loop` and `verify` skills, and the two agents.
- Team-owned files are only created when missing: `.claude/ios.env`, `.claude/ios-screens.txt`, the PR template and `docs/ai-workflow.md`.
- Existing files are merged, never overwritten:
  - **`.claude/settings.json`:** permissions are unioned, an existing swift-format hook is respected, and rules from earlier kit versions that turned out wrong are removed.
  - **`CLAUDE.md`:** a marked block is replaced in place.
  - **`.mcp.json`, `.gitignore`, `.worktreeinclude`:** merged.
- **A `.swift-format` matching the code's indentation** is created when missing, so formatting never imposes another style.

## What it gives the repo

| | |
|---|---|
| **`/verify`** | Six gates, written up as a PR-ready report. 1 format. 2 build with **no new warnings** (the baseline is recorded from a clean build on first run). 3 tests, read from the `.xcresult`. 4 no launch-argument read outside `#if DEBUG`. 5 blast radius. 6 the **visual matrix**: each screen in `.claude/ios-screens.txt` at default, dark and AX5, plus **UI-hierarchy assertions** (`expect:` / `absent:`, matched against accessibility labels) through Xcode's device interaction. 7, with `--release`, the **release gate** (`release.sh`): the Release build, or a real `.xcarchive`, audited for submission blockers (export compliance, icon, launch screen, iPad orientations, privacy manifests and required-reason APIs, usage strings, debug residue, launch-argument seams). |
| **Stop hook** | A turn that changed code can't end on a broken build: format lint plus an incremental build, cached per change. It blocks once, and never loops. |
| **Guard hook** | Denies a simulator destination with no runtime, and `simctl … booted` when more than one simulator is booted. Asks before erasing every simulator or editing a committed Core Data model version. |
| **Cloud gate** | Cloud sessions run unattended to a pushed `claude/*` branch and an open PR; every other push, merge or approval-needing step is refused with a reason instead of stalling on a prompt. Silent locally. See **Security model**. |
| **One simulator per checkout** | Created on first use, recorded with its owning path, addressed by UDID. Worktrees, including Claude Code's own `--worktree`, never share a device. `destroy` refuses to delete another checkout's simulator. |
| **`ios-loop` skill** | The development loop, Xcode MCP versus shell (with Xcode 27's measured behavior), bug fixes, two-pass UI work, parallel worktrees, and routing work to cloud sessions. |
| **UI assertions** | `xcui.py` launches the build the kit already made, by UDID, then attaches a *device-only* Xcode interaction session to read the live UI hierarchy. It doesn't use `InstallAndRun`: on a large project, Xcode dropped that session mid-build and kept the simulator locked to it. |
| **Agents** | `build-verify` (Haiku) returns only `file:line: message`. `ui-verify` judges the screenshots and drives Xcode's device interaction. |
| **Scripts** | `scripts/ai/{build,test,check,verify,visual,release,sim,doctor,bootstrap,worktree,format}.sh`, plus `xcui.py`, `xcresult.py`, `blast-radius.py`, `audit-bundle.py`, `debug-fences.py`, and `frames.swift` / `compare.swift`. |

## Tested

`tests/run.sh` runs 17 hook cases, 45 cloud-gate cases, 18 installer and ownership cases, and syntax checks on stock `/bin/bash` 3.2 and python3. It was proven live on a brand-new app (Plantly) and on Project Ezra, a real app with about 1,070 tests:

- **Bootstrap:** from a fresh install to a passing smoke test.
- **`/verify`:** all gates.
- **The visual gate:** caught a blank empty state that every mechanical gate passed. On Ezra, it found two text-clipping bugs at the largest text size.
- **The release gate:** fails a fresh app on 3 real submission blockers, and passes Ezra on every check.
- **The Stop hook:** live in Claude Code, it blocked a broken build and showed the exact error.
- **Parallel worktrees:** two test runs at once, each on its own simulator.
- **Xcode device interaction:** start a session, install and run, assert the hierarchy, in both directions.

## Security model

Three layers; each says what it does NOT guarantee.

1. **Permission rules and the guard hook** (`.claude/settings.json`, `guard.py`): pushes, `rm -rf` and `.pbxproj` edits ask a human; secrets are denied to reads; ambiguous simulator targets are denied. They run first, everywhere. They do not stop a human who approves the wrong thing.
2. **The cloud gate** (`cloud-gate.py`, a `PermissionRequest` hook). It runs only where a prompt would otherwise appear, and only in a cloud session (`CLAUDE_CODE_REMOTE=true`), where nobody is there to answer and an unanswered prompt stalls the session forever. It approves, for one call, a command made only of `git add/commit/status/diff/log/show/fetch/rev-parse`, `git push` of explicit `claude/*` refspecs to `origin` (flags limited to `-u`, `-q`, `-v`), `gh pr create/view/list/checks`, and `tail/head/wc/grep`. Everything else is refused with a reason the session acts on: the default branch, force, delete, `--all/--tags/--mirror`, a bare `git push`, `gh pr merge`, chained commands, substitution, heredocs, redirects to files, `git -C/-c`, env prefixes, every non-Bash prompt. Its parser fails closed; locally it prints nothing. It is enforced by Claude Code, not by GitHub: GitHub's proxy for cloud sessions does not limit which branches a push updates.
3. **GitHub's own lock** (`scripts/ai/protect-main.sh`, run by the owner): a ruleset on the default branch that refuses force pushes and deletion for every actor, plus `--require-pr` to refuse direct pushes. `doctor.sh` reports whether it is in place. Needs a public repo or GitHub Pro/Team.

`tests/cloud_gate.py` holds the table (45 cases: the exact command a real cloud session stalled on, and every refusal above), each run through the hook process as a cloud session and again locally.

## Requirements and limits

- **Machine:** macOS with Xcode 27 selected, and python3 (ships with Xcode's command-line tools).
- **Trust the repo once:** open Claude Code in it interactively and accept the workspace trust dialog. Until then, headless runs ignore the committed permission rules (hooks still run).
- **Xcode MCP:** the path needs Xcode running. The first `XcodeOpenWorkspace` asks you to approve the agent. Without Xcode, assertions are reported as skipped, never as passed.
- **Simulator only:** device-only behavior (push delivery, CloudKit between accounts, camera, performance on old hardware) is listed in the report as not verified.
