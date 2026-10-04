---
name: ship
description: Take one idea all the way to a merged pull request. States the outcome and how to check it, branches from the default branch, implements through the matching ios-loop playbook, makes the changed screen part of the visual matrix, runs /verify with the AI judge on the screenshots, fixes until every gate passes, opens the PR with the report, and merges it with merge.sh once it is verified at its head. Use for /ship "<idea>", "build and ship", "take this to a merged PR".
argument-hint: "[--no-merge] <the idea, and how you will know it works>"
disable-model-invocation: true
---

# Ship

**Job:** turn one idea into a merged pull request whose every gate passed and whose screens an AI judge looked at.

**Not my job:** merging anything this run did not build · lowering a gate, skipping a failing test or editing `.claude/judge-notes.md` to make a defect pass · pushing to the default branch · changing the GitHub ruleset · a second idea in the same PR (ship it separately).

**When there is nothing to report:** the PR link, "merged", and the gate table.

Invoking `/ship` is the person's consent to merge THIS change once it is proven. It is never consent to merge anything else.

## Steps

1. **Outcome and check.** Write two lines: what changes for the person using the app, and the observation that proves it (a label a screen must show, a behavior a test asserts, a number). Ask one question only if the idea is ambiguous in a way neither the code nor a quick prototype can settle (`principle-never-block-on-the-human`).
2. **Start clean.** `git fetch`, then `git switch -c claude/<topic> origin/<default branch>`. If the checkout holds someone else's uncommitted work that would come along, use `scripts/ai/worktree.sh new <topic> origin/<default branch>` instead and work there.
3. **Build it** through the matching playbook in `.claude/skills/ios-loop/` (feature, bug-fix, ui-pass, refactoring, …): name the data shape first (`principle-model-the-domain`), use the `/architect` skill when the change crosses a function boundary, unit-test the logic, `scripts/ai/build.sh` after each step, one logical change per commit.
4. **Make it visible to the gate.** If the change touches a screen that `.claude/ios-screens.txt` does not list (the reach gate names the affected screens), add a line with the seam that reaches it and an `expect:` label that proves the outcome from step 1 (the `/map` skill shows how). A change the visual gate cannot see cannot be judged.
5. **Verify.** `VERIFY_INTENT="<the outcome and check from step 1>" scripts/ai/verify.sh`. It runs every gate, then the AI judge on each screenshot sheet (default, dark, largest text size), and records the verdicts. A FAIL is the next piece of work: fix it at the root (`principle-fix-root-causes`), commit, verify again. Three attempts per failing gate, then stop, open the PR as a draft (`scripts/ai/pr.sh --draft`) and report what is left. Never merge around a failure.
6. **Propose.** Commit everything, then `scripts/ai/pr.sh --title "<the outcome>"`. The description is the /verify report, with the judge's verdict per screen.
7. **Land.** With `--no-merge` (an autopilot owner, or the person wants to look first), stop here and report the PR as merge-ready. Otherwise `scripts/ai/merge.sh <PR number> --yes`. It merges only if the PR is merge-ready verified at its exact head (gates passed, screens judged, mergeable, checks green, no open threads), waits for running checks, then deletes the branch and updates the local default branch. If it refuses, its reason is the next piece of work (back to step 5); never work around it.

**Reply:** the outcome in one sentence for the person using the app; the PR link and "merged" (or why not); the gate table; the AI judge's verdict per screen with the sheet paths; what was not verified here (device-only behavior).
