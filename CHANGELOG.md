# Changelog

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
