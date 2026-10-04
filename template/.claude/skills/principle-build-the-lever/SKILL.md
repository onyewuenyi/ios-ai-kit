---
name: principle-build-the-lever
description: "Apply to any non-trivial work, not just bulk work (edits, migrations, analyses, checks). Build the tool that does it or proves it (a script, a generator, a Swift test, a scripts/ai check, or a skill your Claude subagents follow) instead of working by hand. The tool is the artifact a reviewer can rerun."
disable-model-invocation: true
---
# Build the Lever

When the work isn't trivial, build the tool that does it instead of doing it by hand.

**Why:** Two payoffs. Throughput, because a script, generator, or codemod does the work the same way every time and reruns for free. Confidence, because the tool is one artifact a reviewer can read and rerun to check the work. Hand-done changes can only be re-verified by redoing them. A deterministic script turns "trust me" into "run this".

**Pattern:** Default to building the lever. Skip it only when the task is trivial, a couple of obvious edits you can see at a glance.

- Do the first unit by hand to learn the recipe, then build the tool. Prove it by rerunning it on that unit and diffing against your hand-done version. Make the lever safe to rerun.
- A script for edits across Swift files (Python or a Swift script; then run `scripts/ai/format.sh` on what it touched, because edits made outside the editor skip the format hook). A generator for repetitive files (fixtures, `#Preview` variants, string catalogs). A dump-to-sqlite or `jq` query for analysis, over an `.xcresult` through `scripts/ai/xcresult.py`, over transcripts through `scripts/ai/friction.py`, over an eval report. A rerunnable check for verification (a test in the app's test target, a `scripts/ai/` script, a launch seam that `/verify` drives).
- A deterministic lever beats fan-out. If the tool can process every unit in one pass, run it yourself. Don't fan out Claude subagents to hand-apply what a script can do.
- When you fan work out to subagents through the Agent tool, write the lever as a skill they all read. The recipe, the verification contract, and the do-not-touch fences go in one artifact. Keep it outside the delegates' write scope so they can't quietly edit the contract.
- Applying this principle produces a file. If you cited it and there is no script, generator, test, or delegate skill in the diff, you didn't apply it.
- Commit the lever when the work outlives the session.

**Balance:** The bar is triviality, not repetition. A one-off still earns a lever when the lever is what makes the work checkable. Per `principle-laziness-protocol`, build the smallest script that does or proves the job, never a framework.

Distinct from `principle-encode-lessons-in-structure`, which makes a recurring instruction a durable guardrail. This is throughput and reviewability on the work in front of you. For scripting the verification itself, see `principle-prove-it-works`.
