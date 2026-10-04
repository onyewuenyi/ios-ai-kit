# Recipes and pitfalls

Prompts worth copying, then the mistakes everyone makes once. Swap in your own screens and finish conditions. The recipes are deliberately informal. That's how they get typed in practice, and the skills read intent fine.

## Understand an unfamiliar subsystem

```text
use /how first to understand how the app restores state after a relaunch. then use /why to figure out why it broke in the last release.
```

Mechanics first, history second. Each skill's report tells you which sources it searched, so you know what the answer is grounded in.

## Get a second opinion on a design

```text
ask /arena for a second opinion on this thread and our approach
```

Your current design becomes one candidate among several, and the synthesis tells you whether the panel found something better or confirmed what you had. Cheap insurance before a costly commitment, like a new Core Data model version.

## Settle a layout with pictures, not words

```text
/ios-loop two or three layouts for the empty task list. build each in its own worktree, compare them side by side at default and AX5, and recommend one.
```

The Prototype arena playbook ends in one labelled image from `scripts/ai/sim.sh compare`. You judge a picture, not a description of one.

## Check independent slices in parallel

```text
/swarm check every screen in .claude/ios-screens.txt in dark mode and at AX5. one worker per screen. one report.
```

Each worker owns one screen. The parent waits for every slice and returns one `PASS`, `ISSUES` or `BLOCKED` report instead of raw worker dumps.

## Review a branch skeptically

```text
/interrogate the whole branch, but skeptically. don't change anything yet. no nitpicks unless it's an actual bug or regression in behavior.
```

The qualifiers do real work. "don't change anything yet" keeps it read-only, and the nitpick rule pre-filters the noise so `Act on` findings are worth your time.

## Fix a bug through a failing test

```text
/ios-loop repro the duplicate row first. if there's a cheap test path, /tdd it. then fix and rerun.
```

"if there's a cheap test path" matters. Forcing a test through a mocked persistent container proves less than a launch seam and a screenshot, and the playbook is allowed to say so.

## Chase a hang

```text
/ios-loop the app freezes for about two seconds when i open a task with 40 attachments. repro on the simulator, capture a Hangs trace, find what's on the main thread, fix it, show me before and after.
```

The Runtime forensics playbook reads the trace before it forms a theory. It confirms the number on a device before it reports a win, because simulator numbers are Mac numbers.

## Prepare an App Store submission

```text
/ios-loop get this ready for App Review. run the release gate, fix every blocker in scope, and list what only i can do in App Store Connect.
```

The Release playbook runs `scripts/ai/verify.sh --release` and audits the built bundle, not the source. Export compliance, the privacy manifest, usage strings and launch-argument seams fail there, not in a Debug build.

## Ship a small idea end to end

```text
/ship the settings screen shows the app version and build number at the bottom. it must read correctly at AX5.
```

One idea, one PR, merged once `/verify` and the AI judge pass at its head. [Verify and ship](./06-verify-and-ship.md) has the whole road.

## Clear the PR pile

```text
/loop /lead
```

The lead sorts every open PR by who has to act, fixes what needs no decision on each PR's own branch, and says nothing unless something needs you.

## Keep a run honest while you're away

```text
i'm going to bed, keep going autonomously until every migration test passes. do not stop. keep a decision log i can audit in the morning. open the pr with pr.sh, don't merge.
```

The full contract is on the [overnight page](./07-overnight.md). The short form works once the task and finish condition are already in the conversation.

## Redirect a drifting run

Steering prompts are one line.

```text
i said the goal is to repro. i did not ask for a fix yet.
```

```text
apply prove it works. show me the sheet at AX5, not the build log.
```

```text
/unslop that, no long dashes
```

You rarely need more words. You need the right name, and [the principles page](./08-principles.md) is the vocabulary.

## Get the reply in plain words

```text
/bro
```

That's the whole prompt. [`/bro`](../../template/.claude/skills/bro/SKILL.md) restates the last message like one human talking to another, no jargon, shorter. Use it when a reply is technically thorough and you still don't know what it said.

## The pitfalls

- **Enumerating skills in the prompt.** "use /how then /architect then /arena" reorders steps the playbook already sequences. State the goal and constraints. Name a skill only to override a default.
- **A vague finish condition.** "make it better" gives `/loop` nothing to check. Give a command, a screen state or a number that can pass or fail.
- **Parallel agents in one checkout.** They overwrite each other's files and install over each other's builds, and the diff becomes archaeology. Say "own worktree per attempt" and the isolation, simulator included, is free.
- **Driving a simulator by name or by `booted`.** With two sessions running, either one picks the wrong device. The kit addresses its simulator by UDID through `scripts/ai/sim.sh`, and the guard hook blocks the ambiguous forms.
- **Believing a crash before checking the environment.** A simulator whose runtime can no longer spawn processes makes every launch "crash". Run `scripts/ai/doctor.sh` and `scripts/ai/sim.sh guard` first.
- **Using `/arena` for coverage.** `/arena` repeats one design or code brief, then picks a base and grafts the best parts. `/swarm` partitions slices or declared race arms and aggregates one report.
- **Accepting every review comment.** Bots and humans both file real catches and noise in one list. `/interrogate` and `/lead` sort findings with reasons, and you can override either way.
- **Putting a model in the prompt instead of `.claude/ios.env`.** It lasts one call and reaches no teammate. [Setup](./01-setup.md) covers the roles.
- **Reporting success off a green build.** A build proves it compiles. Ask for the gate table, the judged sheets, the value read back after a relaunch, or the trace, and expect the evidence in the reply.
- **Trusting a screenshot nobody looked at.** A captured sheet is not a verdict. The visual gate stays at `JUDGE` until the AI judge or a person records one.
- **Writing a judge note to make a FAIL pass.** `.claude/judge-notes.md` is for deliberate design conventions. A note that excuses a real defect turns the gate off without telling anyone.
- **Editing the shipped Core Data model version.** It corrupts every existing store on update. A change is a new model version, a superset of the last.
- **Pushing to `main`.** The guard hook, the cloud gate and GitHub's ruleset all refuse it. `scripts/ai/pr.sh` is the road.
- **Writing a `SKILL.md` freehand.** Route it through the Authoring a skill playbook so validation and review happen.

That's the guide. If you skipped ahead, go back to [setup](./01-setup.md) and run one real task. The habits stick from use, not from reading.

Back to the [guide index](./README.md).
