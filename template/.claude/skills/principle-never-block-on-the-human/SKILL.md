---
name: principle-never-block-on-the-human
description: "Apply when tempted to ask 'should I do X?' on reversible work. Proceed, present the result, let the human course-correct after the fact; if running something would settle the question, run it. Use AskUserQuestion only for genuine product calls, and confirm only irreversible or outward actions (merge, push, App Store Connect, CloudKit Production, user data)."
disable-model-invocation: true
---

# Never Block on the Human

The human supervises asynchronously. Agents must stay unblocked. Make reasonable decisions, proceed, and let the human course-correct after the fact.

**Why:** Every permission pause stalls the pipeline and makes the human the bottleneck. Code changes on a branch are reversible and reviewable, so a wrong decision usually costs less than blocking.

**Pattern:**
- **Proceed, then present.** Do the work, show the result. Don't ask "should I do X?" Do X, explain why.
- **Settle forks by running them.** Most forks are not the owner's. If running something would settle it (a layout, a timing, whether an eval separates), run it. Build the variants, capture them with `scripts/ai/sim.sh compare`, and present the evidence.
- **Ask only real product calls.** Use `AskUserQuestion` for a genuine product or preference decision. One decision per question, your recommendation first, the evidence attached (a comparison image, a preview, a number).
- **Park, don't wait.** When a product decision blocks one branch of work, park that branch with the options and your recommendation, and continue everything that does not depend on the answer.
- **Make the system self-healing.** When you notice a problem, log it and fix it in the next round.

**Boundaries:**
- **Reversible actions proceed without blocking.** Edits, builds, simulator runs, tests, local commits, opening or updating a PR with `scripts/ai/pr.sh`.
- **Irreversible or outward actions still require confirmation.** Merging, pushing anywhere but your own branch, force-pushing, deleting user data or simulators you did not create, uploading to App Store Connect, deploying a CloudKit schema to Production, launching a cloud session, and anything that sends user content off the device.
- **Product direction** comes from the human. *Execution* should not block. When the owner asks "should we", answer with a judgment. "No, this does not earn its place" is a valid answer.
