# Make it yours

`ios-loop` is one way of working. The machinery underneath, playbooks, routing, model roles, the gates, works just as well wearing yours. This page covers generating a personal mode, turning a session's lessons into structure, correcting a skill that misbehaved, authoring a focused skill, and testing a skill change before you trust it.

## Generate your own mode with `/automate-me`

```text
/automate-me
```

You don't describe your style, because [`/automate-me`](../../template/.claude/skills/automate-me/SKILL.md) reads it out of your history. It mines your recent Claude Code transcripts for this repo, the `.jsonl` files under `~/.claude/projects/`, for repeated preferences. How you like replies, delegation, verification, Swift, prose and process. Then it asks you which patterns are really you. It drafts `.claude/skills/<your-name>-mode/SKILL.md` through the Authoring a skill playbook, runs the draft through `/unslop`, and opens a PR with `scripts/ai/pr.sh`, so you review it like any other change.

Run it again whenever your habits drift.

```text
/automate-me update my mode skill with everything since its last edit
```

Update mode mines only the history since the skill last changed. It keeps rules you haven't contradicted, revises the ones with new evidence, and adds sections only for genuinely new patterns.

## Turn a session's lessons into structure with `/reflect`

Right after a task that taught you something, run this.

```text
/reflect that took way too long. capture what we learned so the next run doesn't repeat it.
```

[`/reflect`](../../template/.claude/skills/reflect/SKILL.md) collects every moment the session was corrected, believed something false, or caught a defect late. It routes each lesson to the strongest mechanism that would have prevented it. A type first, then a failing test, a hook, a script, a line in `.claude/ios-screens.txt`, a playbook step, and a project rule last. It sorts the proposals into `Accepted`, `Rejected` and `Backlog`, and waits for your approval before anything changes. Approve a proposal only if it would change a future decision. One weird session is an anecdote, not a rule.

## Fix a skill that got it wrong with `/correct`

When a skill or playbook led the agent astray, say so right there.

```text
/correct ios-loop told it to run the full test suite for a one-line copy change. that's ten minutes for nothing.
```

[`/correct`](../../template/.claude/skills/correct/SKILL.md) finds the instruction that caused the behavior, checks the transcripts for whether it happened before, and proposes the smallest edit to that skill, through a PR of its own. It uses the same evidence `/friction` reads.

## See what keeps costing time with `/friction`

```text
/friction
```

[`/friction`](../../template/.claude/skills/friction/SKILL.md) reads this repo's transcripts and verify history for the patterns no single session notices. Read-only commands no rule allows, rejected calls, repeated hook refusals, Stop-hook build failures, recurring compiler errors, flaky tests, and gates whose median time grew. You pick which to fix. Each accepted fix lands with a test, through a PR. `/lead` runs it quietly once a weekday.

## Author a focused skill

When you already know the workflow you want to capture, ask for it.

```text
/ios-loop write a skill for checking a Core Data migration against a store saved by the previous app version
```

Writing a skill matches the Authoring a skill playbook. It writes the `SKILL.md` to this kit's standard. A description under 600 characters, and the three one-job markers, `**Job:**`, `**Not my job:**` and `**When there is nothing to report:**`. Every `scripts/ai/` path, flag and `/skill` it names must exist, and `tests/standard.py` checks all of it. Then it ships the skill through the Opening a PR playbook. Agent-facing prose has a higher bar than human prose, because an unhelpful sentence becomes an instruction some future agent follows. Let the playbook hold that bar rather than writing a `SKILL.md` freehand.

One special case has its own tool. Proving app behavior is `/verify`'s job, and what it looks at is `.claude/ios-screens.txt`. So when the need is "teach the agent to drive this screen", run `/map` to add the screen, or `/map refresh` to repair the list, instead of writing a verification skill. [Verify and ship](./06-verify-and-ship.md) covers both.

## Write docs to a standard with `/technical-writing`

Skills aren't the only prose you ship. For docs, READMEs, release notes, App Store text, PR descriptions and commit messages, there is one more skill.

```text
/technical-writing review the README changes
```

[`/technical-writing`](../../template/.claude/skills/technical-writing/SKILL.md) applies a layered standard with one goal, prose a tired engineer understands on the first read. It picks the document's mode first (tutorial, how-to, reference or explanation), then works sentence by sentence. Who does what, one thought per sentence, nothing readable two ways. Use it to review what you or an agent just wrote, or name it up front when you ask for a doc.

## Test a skill change blind

A skill edit affects every future session, so test it like the experiment it is.

```text
/ios-loop run the eval playbook on this skill change. same task for both variants, candidates stay blind.
```

The Eval playbook is built around one failure mode, the observer effect. An agent that knows it's being evaluated behaves differently. So candidate agents get an organic-looking task in sanitized directories, never the words "eval" or "candidate", and never each other's existence. One judge on a different Claude model scores all outputs under neutral labels, and chain-following gets graded from which files each candidate actually read, not from what it claims. For a repeatable suite, the playbook writes it as a `claude plugin eval` run, so the next change to the same skill reruns it.

Read every output yourself before accepting the verdict. If you disagree with the judge, suspect the rubric before you suspect your judgment.

**Pitfall.** Don't edit a skill mid-task because it's misbehaving. Fix it in its own PR (`/correct` does exactly that) and keep the task moving. A skill edit that ships tangled into feature work is invisible to review and impossible to evaluate.

Next is [Recipes and pitfalls](./10-recipes-and-pitfalls.md).
