---
name: interrogate
description: Adversarial review of an iOS diff through independent lenses (concurrency, persistence and data safety, lifecycle and state, UI at the extremes, accessibility, privacy and App Review, performance, slop, design), one reviewer agent per lens and a second Claude model on the riskiest, with every finding verified and judged before it is reported. Use for /interrogate, "tear this apart", "stress test this change", "find blind spots", or before shipping a contested design.
argument-hint: "[diff target: branch, commit range, or paths] [lenses]"
disable-model-invocation: true
---

# Interrogate

**Job:** find the ways this diff fails the person using the app or the next person changing it, and report only the findings that survive verification and judgment.

**Not my job:** applying fixes unless asked · style nits · reviewing beyond the diff and what it touches · questioning the intent itself · using any model outside Claude.

**When there is nothing to report:** "No verified findings", with the lenses run and the two riskiest spots each one checked.

The signal comes from three places. Independent lenses, each looking for one class of failure. Model diversity, the same lens asked of a second Claude model. Verification, where a finding that cannot name a concrete input producing a wrong result is dropped. Then you judge what is left as the lead reviewer, a pragmatic senior engineer, not a neutral aggregator.

The deliverable is a verdict. Do not apply changes.

## 1. Scope and intent

- **Diff:** the argument if given, else `git diff` of uncommitted work, else `git diff $(git merge-base HEAD origin/HEAD)...HEAD` (the branch's work).
- **Intent:** one paragraph from the user's words, the commits, the PR description (`gh pr view` if one exists) and the code. Reviewers judge the execution against it, never the intent itself. If you are unsure of the intent, ask before spawning.

## 2. Pick the lenses

Choose the 3 to 5 that the diff can actually fail on. All nine on a one-file copy change is noise.

| Lens | Looks for |
|---|---|
| `concurrency` | Actor isolation and `Sendable` violations, tasks outliving their view, missing or ignored cancellation, an `await` that re-enters on stale state, main-actor blocking I/O, races between two async writers |
| `persistence` | Context/thread affinity, object lifetime after deletes, faults in loops, unsaved or unchecked saves, migrations that are not supersets, destructive paths without backup, CloudKit/sync assumptions |
| `lifecycle` | `scenePhase` and background transitions, state lost or duplicated on relaunch, sheets presented from the wrong context, navigation state after a pop, work started in `onAppear` that re-runs |
| `ui-extremes` | Truncation and clipping at accessibility sizes, iPad and small-device layout, keyboard overlap, fixed sizes, animations on first layout, Reduce Motion |
| `accessibility` | Unlabelled controls, gestures without spoken actions, content hidden for the eyes but read aloud (and the reverse), announcements, transient UI that disappears before it is spoken |
| `privacy-review` | Usage strings, privacy manifest agreement, data leaving the device beyond what the app says, launch seams escaping DEBUG, in-process pickers, App Review guideline risks, untrusted input reaching a sink (a URL scheme, a `WKWebView`, a predicate format string), secrets in code or logs |
| `performance` | Work in `body`, O(n²) per render, main-thread decoding, over-broad observation invalidating whole trees, unbounded caches |
| `slop` | Dead code and unused helpers or scripts left behind, debug residue (prints, temporary flags, commented-out code), comments that narrate the diff instead of the why, tests weakened or deleted to pass, a new pattern beside an existing one that does the same job |
| `design` | The design red flags in `.claude/skills/architect/references/design-red-flags.md` (shallow module, information leakage, temporal decomposition, pass-through, split ownership, two ways to do one task, importable internals, hand-synced lists) and the code-quality lens in `references/code-quality-review.md`: a missed simplification, spaghetti growth, a file pushed past 1,000 lines, logic in the wrong layer |

Every lens also applies the hunting rules in [`references/rubric.md`](references/rubric.md) inside its own class of failure: trace the execution path, fix the cause not the symptom, check the real thing.

## 3. Spawn one reviewer per lens

In one message, one Agent call per lens, `subagent_type: "review-lens"`, run in parallel. Build each prompt from [`references/reviewer-prompt.md`](references/reviewer-prompt.md): the lens name, the intent paragraph, the diff command to run (not the diff inlined), the project's rules file path (CLAUDE.md) so project invariants count, and the reference paths the template names for that lens. Ask each for at most 5 findings.

**Second opinion.** For the one or two lenses where a miss would hurt most (usually `persistence` or `concurrency`, or `design` for a new subsystem), send the SAME prompt a second time in the same message with the Agent tool's `model` set to a different Claude model from the reviewer's default (`sonnet` or `fable` beside the default `opus`; `MODEL_JUDGMENT` in `.claude/ios.env` overrides the default). Different models miss different things. A defect both find independently is the strongest signal this skill produces. One only a single model finds still gets verified in step 4 like any other.

## 4. Verify before judging

For each returned finding, confirm it yourself. Read the cited lines and the call chain. Where cheap, reproduce: a unit test through `scripts/ai/test.sh -only-testing:…`, a seam run through `scripts/ai/sim.sh launch`, a grep. Classify:

- **Confirmed:** you reproduced it, or the code unambiguously produces the failure.
- **Plausible:** the mechanism is real but you could not trigger it. Say what would.
- **Rejected:** the concrete scenario does not hold. Say why in one line.

Merge duplicates. Different lenses and models describe one defect differently. Note who raised it. Two lenses or two models finding the same defect independently is strong signal. Say so. Note disagreements too. One reviewer flagging what another explicitly cleared is context for the verdict.

## 5. Judge

Read [`references/lead-judgment.md`](references/lead-judgment.md). You have context the reviewers lacked: what was tried and rejected, what is scaffolding, what the next PR does. Put every Confirmed or Plausible finding in one bucket:

- **Act on.** Real issues affecting correctness, data safety, privacy or maintainability given the actual goals. They would block a real PR. More than five means you are not filtering hard enough.
- **Consider.** Legitimate, but you are not sure they outweigh the cost of addressing them now. Worth the user's attention.
- **Noted.** Technically valid but not actionable now.
- **Dismissed.** Wrong, nitpicky, hypothetical, or missing context. Rejected findings from step 4 land here too.

## 6. Verdict

### Intent
> The step 1 paragraph.

### Reviewers
One bullet per reviewer: lens, model, number of findings.

### Act on
Ranked by harm to the person using the app. For each: `file:line`, the failure scenario, Confirmed or Plausible, which lenses and models raised it, the suggested fix.

### Consider
For each: the finding, who raised it, the tradeoff.

### Noted
A brief list.

### Dismissed
One line each, with why. This is the trust mechanism. It lets the user override your judgment.

### Agreement map
Where lenses and models agreed, where they diverged, and what the pattern says.

Do not apply fixes unless asked.
