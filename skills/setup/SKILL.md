---
name: setup
description: Install or upgrade ios-ai-kit in the current iOS repo — committed Claude Code config (permissions, the guard, Stop, cloud-gate and bearings hooks, the kit's skills and agents), scripts/ai/*, a per-checkout simulator — then bootstrap and report the owner-only steps left. Use for "set up ios-ai-kit", "install the iOS workflow", "upgrade the kit".
disable-model-invocation: true
---

# Set up ios-ai-kit in this repo

**Job:** install or upgrade the kit in this repo and say exactly what is left for the owner.

**Not my job:** running `protect-main.sh` without a yes (it changes GitHub settings) · accepting the trust prompt or signing in for the owner · pushing to the default branch · editing app code.

**When there is nothing to report:** "ios-ai-kit is current; doctor reports nothing left."

The kit's files live next to this skill: the installer is `../../install.py` relative to this skill's base directory (the line "Base directory for this skill" above gives the absolute path).

1. **Check the repo.** Run `git rev-parse --show-toplevel` and `git status --short`. Stop and say so if this is not a git repo or has no `.xcodeproj`/`.xcworkspace`. If the tree has uncommitted changes, tell the person and continue only on their word: the install writes files beside them.
2. **Install (idempotent, also the upgrade).** `python3 <base>/../../install.py "$(git rev-parse --show-toplevel)"`. Show the detected line (project · scheme · bundle id · iOS · file style) and every `added`/`updated`/`merged`/`extended` line. If the detection is wrong, re-run with `--scheme <name>` or `--container <path>`; the installer seeds its defaults from an existing `.claude/ios.env` on later runs.
3. **Bootstrap this Mac.** `scripts/ai/bootstrap.sh`: toolchain check, Apple's Xcode skills exported, this checkout's simulator, smoke test. It fails loudly; report what failed and its fix, never work around it.
4. **Doctor.** `scripts/ai/doctor.sh`, and report every `WARN`/`FAIL` line.
5. **Owner-only steps.** List the ones `doctor.sh` still reports, in this order, each with its one action, from the "First run" section of `docs/ai-workflow.md`:
   - trust the folder (run `claude` here once and choose Yes): Claude cannot do this for them;
   - `gh auth login`, if the GitHub CLI is not signed in;
   - `scripts/ai/protect-main.sh` (GitHub refuses direct pushes, force pushes and deletion of the default branch): offer to run it, and run it only on a yes, since it changes the repository's settings;
   - `/web-setup` or the Claude GitHub App, for cloud sessions;
   - Xcode ▸ Settings ▸ Intelligence ▸ Xcode Tools on, and approve the agent the first time `/verify` opens the project.
6. **Offer the status line** (one question): the branch, HEAD's verify state and the PRs that need you, always under the prompt. On a yes: `python3 <base>/../../install.py "$(git rev-parse --show-toplevel)" --statusline` (this Mac only; it never replaces a status line already set).
7. **Propose the install.** The new files go in through a pull request like every other change: commit them on a branch (`git switch -c claude/ios-ai-kit`, `git add` by path, commit). If `gh auth status` succeeds and the repo has an `origin`, run `scripts/ai/pr.sh`; otherwise leave the commit on that branch and name `gh auth login` then `scripts/ai/pr.sh` as the owner's next step. Never push to the default branch.
