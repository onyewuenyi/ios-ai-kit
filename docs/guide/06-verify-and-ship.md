# Verify the result and ship it

"It compiles" is not evidence. "The tests pass" is not much more. The Prove It Works principle makes the agent check the real artifact before it reports success, and on iOS the real artifact is the app running on a simulator, at the text size and appearance a real person uses. The kit's job is to make that checkable without a conversation. This page covers the whole road from an idea to a merged PR, then each stop on it.

Picture a test pilot flying a prototype over a real course. You hold the stopwatch. The ground crew films every pass and ticks a checklist. The terminal at the end says `verify: PASS`, and the film is attached.

## The whole road

```text
idea
  │  /ship "<the idea and how you'll know it's done>"
  ▼
ios-loop playbook ── builds in its own worktree and simulator
  │
  ▼
/verify ── gates 1-5 (format, build with no new warnings, tests, seams, reach)
  │        gate 6 captures every screen at default, dark and AX5
  │        the AI judge reads every sheet ── PASS / FAIL / no verdict
  ▼
scripts/ai/pr.sh ── opens the PR, the verify report is its body
  │
  ▼
scripts/ai/merge.sh ── lands it once it is merge-ready
```

`/ship` drives one idea down that whole road. `/lead` picks up any PR already on it.

## Ship one idea with `/ship`

```text
/ship let people pin a task to the top of the list. pinned tasks survive a relaunch. verify on the list and detail screens.
```

[`/ship`](../../template/.claude/skills/ship/SKILL.md) is `/ios-loop` with the end of the road included. It runs in seven steps.

1. It writes two lines, what changes for the person using the app and the observation that proves it.
2. It starts clean, on a `claude/<topic>` branch from the default branch, or in its own worktree when your checkout holds other uncommitted work.
3. It builds through the matching playbook (Feature, here), one logical change per commit.
4. It makes the change visible to the gate. A changed screen that `.claude/ios-screens.txt` does not list gets a line, with an `expect:` label that proves the outcome from step 1. A change the visual gate cannot see cannot be judged.
5. It runs `/verify` with that outcome as the judge's intent. A FAIL is the next piece of work, with three attempts per gate. After that it opens a draft PR and reports what is left.
6. It opens the PR with `pr.sh`.
7. It lands the PR with `merge.sh`.

Invoking `/ship` is your consent to merge this one change once it is proven. It is never consent to merge anything else. It never lowers a gate, skips a failing test, or writes a judge note to make a defect pass. You get one message at the end, with the outcome, the PR link and "merged", the gate table, and the judge's verdict per screen.

Use `/ios-loop` when you want to review before anything lands. Use `/ship` when the finish condition in your prompt is the review you need.

## State the finish condition up front

Put what done means in the first prompt, in whatever words fit.

```text
/ship add a weekly summary widget. the small and medium sizes both render with sample data, the empty state says so in words, and tapping it opens the summary screen. show me the evidence.
```

Now the agent has checks it can run, not a mood to satisfy. When the reply comes back, it should carry the gate table, the sheets it judged, and a "Not verified here" list. If a check couldn't run, a good reply says "inconclusive". Treat a confident reply without evidence as a red flag.

Match the check to the change.

- A UI change walks the changed flow on the simulator and judges the screens at default, dark and the largest text size.
- A persistence change writes a value, relaunches, and reads it back.
- A Core Data migration opens a store saved by the previous model version.
- A perf change compares before and after Instruments traces from a Release build.
- A notification, CloudKit or camera change says plainly that only a device proves it, and the Device run playbook says how.

For a small diff you don't fully trust, [`/blast-radius`](../../template/.claude/skills/blast-radius/SKILL.md) finds what else it could break. It runs `scripts/ai/blast-radius.py` to list every screen the change reaches, picks the one fact the change is safe because of, and proves it by running code instead of writing an essay about it.

## Run the gates with `/verify`

```text
/verify
```

[`/verify`](../../template/.claude/skills/verify/SKILL.md) runs every gate even after one fails, and writes `.build/verify/report.md`.

1. **Format.** `swift-format` lint over everything the branch changed.
2. **Build** with no new warnings. The baseline is recorded from a clean build on the first run.
3. **Tests,** read from the `.xcresult`, not the log.
4. **Seams.** No launch-argument read outside `#if DEBUG`, so no test seam ships to the App Store.
5. **Reach.** Every screen the change can affect, so the next gate looks at the right ones.
6. **Visual.** Each screen in `.claude/ios-screens.txt`, captured at default, dark and AX5 side by side, plus assertions on the live UI hierarchy through Xcode's device interaction.
7. **Release,** with `--release`. The Release build audited for submission blockers (export compliance, the privacy manifest and required-reason APIs, usage strings, launch-argument seams, debug residue).

A failure in this change's scope gets fixed, with at most three attempts per gate. A failure outside it gets reported, never hidden. No test is ever weakened, skipped or deleted to get a pass.

## Let the AI judge look at the screens

Gate 6 captures. It does not decide. A screenshot nobody looked at proves nothing, so the visual gate reads `JUDGE` until a verdict exists.

`scripts/ai/judge.py` supplies that verdict. It sends every sheet, and what the change was meant to make visible, to a separate Claude call on your `MODEL_JUDGMENT` model. The judge returns PASS or FAIL per screen, each with what it saw, and the script checks that answer before it believes it. A valid answer is recorded with `python3 scripts/ai/history.py judge`, and only a PASS makes the commit count as verified for `pr.sh`, `/lead` and the status line. An invalid answer, or no answer, leaves the gate at `JUDGE`, never at PASS.

The judge fails a screen for defects a person would hit. Primary text clipped at the largest size, controls drawn over each other, a light-only color in dark mode, a blank area where an empty state belongs, or the intended change missing from a screen it should affect. It does not fail a design choice. When it keeps failing something you meant, write the convention in `.claude/judge-notes.md` ("rows show one title line at the default size, two at accessibility sizes"). A note there must never excuse a real defect.

You can always overrule it, or judge by eye instead with `VISUAL_JUDGE=human` and then `history.py judge PASS|FAIL "<what you saw>"`.

## Keep the screen list honest with `/map`

The visual gate is only as good as `.claude/ios-screens.txt`. Each line names a screen, the DEBUG launch arguments that reach it, and the accessibility labels it must and must not show.

```text
task-list-empty | -SeedEmpty | expect: No tasks yet | absent: Loading
```

If the list is empty or the gate checks nothing useful, run this.

```text
/map
```

[`/map`](../../template/.claude/skills/map/SKILL.md) works from the code, not from you. It finds the seams the app reads, the deep links it handles, and what a first launch writes. It picks the three to six surfaces a person spends their time on, plus the states that break most often, then probes each one's live labels through Xcode. If the app has no seams at all, it offers a minimal DEBUG-only `LaunchSeams.swift` and asks before adding it. It proves every line once with `scripts/ai/visual.sh` before handing the list over.

Apps change and screen lists rot. When a screen moves or a label changes, run `/map refresh`. The visual gate already refuses a line whose seam the app no longer reads, and flags labels nobody has confirmed in 60 days.

## Open the PR with `pr.sh`

```text
/ios-loop open the pr. small ordered commits, evidence in the description.
```

The Opening a PR playbook works from a worktree, orders the work into small commits that each say why, cleans the diff, unslops the prose, and runs `scripts/ai/pr.sh`. That script is the only road to `main`. It pushes a non-default branch and opens the PR with `/verify`'s report as the description. Commits made on `main` move onto a new `claude/<topic>` branch first, and your `main` goes back to `origin/main`, so nothing is lost and nothing lands directly. Run it again after more commits and it updates the same PR. Five narrow PRs beat one fat one, and stacked follow-ups beat a growing branch.

## Drive open PRs to merge-ready with `/lead`

An open PR starts collecting blockers immediately. Checks fail, reviewers comment, `main` moves. Hand that churn to [`/lead`](../../template/.claude/skills/lead/SKILL.md).

```text
/lead
```

The lead reads every open PR you authored through `scripts/ai/prs.py` and sorts each into four buckets. **Needs you** holds the merge-ready, the stalled, review requests and fixes waiting to be pushed. **Needs work** holds conflicts, failing checks, review threads and app code not verified at its head. **Healthy** is counted and never listed. **Done** is reported once.

It does the needs-work itself, on each PR's own branch, through `scripts/ai/worktree.sh pr <n>`. It steers the existing branch and never starts a fresh one. That includes running `/verify` on PRs a cloud session opened, which only a Mac can do. Its triage of review comments is skeptical, because humans and bots file real catches and noise in the same list. A real finding gets a fix. One it disagrees with goes to you with the reason, instead of a silent change. When all you want is status, ask smaller.

```text
/lead 123
```

Leave `/loop /lead` running on a workday. It paces itself, about every 10 minutes while checks run and every 60 when all is healthy, and stays quiet unless something needs you. The Babysit playbook is the same loop focused on one PR you name.

## Land it with `merge.sh`

Green is not the same as safe. A PR is merge-ready when `/verify` passed at its exact head commit with the screens judged, it is mergeable, its checks are green, and no review thread is open. `scripts/ai/merge.sh <n> --yes` lands a PR only in that state. While checks are still running it waits. Anything else, a failing check, a conflict, an open thread, an unverified head, stops it with the reason, and that reason is the next piece of work. After the merge it deletes the branch, fast-forwards your local default branch, and prunes the merged worktree.

`--yes` means a person asked for this PR to land. `/ship` passes it for the change it built and for nothing else. `/lead` never does, so a merge-ready PR from the lead's digest waits for you. Cloud sessions never merge at all. A Mac verifies and a Mac merges. Because `merge.sh` reads the verify history and the digest, it trusts evidence, not a claim in the conversation.

For a stack, ask for the Shipping playbook.

```text
/ios-loop land the stack.
```

It verifies each PR independently before landing anything, one fresh agent per PR proving the behavior on its own simulator. Then it lands only the contiguous verified run from the bottom, one PR at a time through `merge.sh`, and reports the first PR that breaks the chain. A verified PR sitting above an unverified one waits, because landing it would pull the gap in underneath.

## What a simulator can't prove

Every report ends with "Not verified here". Push delivery, CloudKit between two accounts, the camera, background launch timing and performance on an older phone are device-only. The kit lists them instead of passing them. The Device run playbook turns that list into steps for a person with a phone.

Next is [Run work while you sleep](./07-overnight.md).
