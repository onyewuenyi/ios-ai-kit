# Authoring or changing a skill

**You own the skill's voice.** A skill is a prompt every future session pays for. Keep only prose that changes a decision.

1. **Decide it earns a skill.** A workflow you keep hitting and no skill or playbook captures earns one. A one-off belongs in the task. A step sequence inside the loop belongs in `playbooks/` as a playbook. A rule with a trigger belongs in a principle skill. A worker that needs its own tools or context belongs in `.claude/agents/`. Search the existing skills, playbooks and agents first, and extend one before adding one. **Check.** Name the evidence that the workflow recurs (the sessions that hit it, or a `python3 scripts/ai/friction.py` proposal), or stop here.
2. **Write the frontmatter.** `name` matches the directory. `description` says what the skill does and when to use it, with the phrases a user types, in under 600 characters. Add `disable-model-invocation: true` when the skill has side effects or only runs on `/name`, and on every principle skill. Add `argument-hint` when it takes arguments. **Check.** The description reads as a trigger, not a summary, and its length is under 600.
3. **State the one job.** The body opens with three markers, each one line.
   - `**Job:**` the done state, in one sentence.
   - `**Not my job:**` the anti-jobs, separated by `·`. Name the dangerous neighbors explicitly (merging, pushing to the default branch, hand-editing `*.pbxproj`, deleting user data).
   - `**When there is nothing to report:**` the exact quiet answer, usually one line.

   Principle skills are exempt. They keep the shape rule, why, pattern, test. **Check.** All three markers are present, and each anti-job is something a reader could plausibly mistake for the job.
4. **Write the steps.** Numbered steps, each ending in a check, and a final `**Reply:**` line that names only what is unique to this skill. Tell the agent to do the thing and skip the reason. Explain only when the rule is confusing without one. Point at structural sources (a `scripts/ai/` script, `.claude/ios-screens.txt`, a Swift type, a test) instead of restating them (principle-encode-lessons-in-structure). Delegate to another skill or playbook by path. Examples are Swift, SwiftUI, Core Data, Swift Testing, XCTest and Instruments. Voice is short declarative sentences, no long dash, no colon as a mid-sentence connector. **Check.** Run `grep -n $'\xe2\x80\x94' <file>` and find nothing, then delete every sentence whose removal changes no decision.
5. **Wire every reference.** Every `scripts/ai/` path, every flag, every `/skill`, every agent and every principle the skill names must exist. A new playbook needs a row in the `ios-loop` router table. In the ios-ai-kit checkout run `python3 tests/standard.py`. It checks the markers, the description length, dangling scripts, `/skill` names, script flags and the router. **Check.** It prints `0 failed`.
6. **Test the behavior when the skill is structural.** A skill that changes what an agent does (which script it runs, which gate it respects, when it stops) gets an A/B run per `playbooks/eval.md`. A purely stylistic skill skips this with `skip: subjective`. **Check.** The eval's per-case table shows the variant at or above the baseline, or the skip is recorded.
7. **Open the PR** per `playbooks/opening-a-pr.md`. **Check.** The PR link exists.

When in doubt, delete. Match tone to scope. A workflow you keep hitting that no skill captures is a proposal for a new skill, not a paragraph in this one.

**Reply:** what the skill does in one line, its trigger and its one job, the design decisions that were not obvious, the `tests/standard.py` result, the eval result or the reason it was skipped, and the PR link.
