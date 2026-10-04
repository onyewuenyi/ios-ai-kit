---
name: no-comments
description: "Spawn the comment-sicko agent over a Swift diff, delete the comments it rightly condemns, fix the code those comments were excusing, and offer a type, test or hook for any constraint a comment claimed. Use for /no-comments, before review, or when a diff is full of narration, workaround notes or suppressions."
disable-model-invocation: true
---

# No comments

**Job:** leave the scoped Swift code with no comment that prose could replace with code, and no workaround a comment was excusing.

**Not my job:** comments outside the scope · rewriting code the scope does not touch · a style pass (`/unslop` covers prose, swift-format covers layout) · keeping a comment because deleting it feels risky.

**When there is nothing to report:** "No comments to kill in scope", with the number of comments comment-sicko read.

Spawn `comment-sicko`. Act on the findings you accept. Defer to its fresh eyes.

## Scope

Use the caller's files or diff. Otherwise use the current change against the base branch, default `main`, including the working tree: `git diff main...HEAD` plus `git diff HEAD`. Swift files, plus any `.h`, `.m` or `.metal` files the change touches.

## Steps

1. **Spawn the agent.** One Agent call with `subagent_type: comment-sicko`. It cannot run git, so pass the scope as the diff text, or as the list of files with the changed line ranges. Do not restate its rules.
2. **Inspect its report.** Reject a flag outside the scope, a kill of a comment that meets a keep clause, a misstated `MUST KILL` reason, and a flag that treats deliberate, kept code as guilty. A reshape flag on a surprise in our own code stays actionable. Do not restore those comments. A keep survives only with proof that it is about something we cannot change (an Apple framework or OS bug, a vendor SDK, a server contract, App Review). Audit what it missed. Scan the scope for `// swiftlint:disable`, `// swift-format-ignore`, and comments excusing `@unchecked Sendable`, `nonisolated(unsafe)`, `@preconcurrency`, `try!`, `as!` or a force unwrap. A suppression that waives correctness, data safety or thread safety is an actionable `MUST KILL`. For every `UNPROVEN` item and every thin `IMPORTANT` or `do not remove` keep, run `/how` or `/why` on its symbol first. If a kill is ambiguous after that, kill it. If a keep is refuted or still ambiguous, kill it. If you reject the report as a whole, rerun the agent once with the failure named. If you reject the second report too, report the scope as open and fail `/no-comments`.
3. **Delete the accepted kills.** Edit the comments out, nothing else. Run `scripts/ai/format.sh` on the touched files.
4. **Fix the trivial `MUST KILL` flags directly.** Delete a dead path, drop a parameter, call the real API, rename the symbol so it says what it does. If any fix needs a new shape, run `/architect` once for the accepted set and the code around it. Stop at the sketch. `/architect` shapes, step 5 builds.
5. **Fix the root cause, in scope.** Implement the smallest root-cause fix inside the scope and remove every workaround that was named. If the root cause is out of scope, land the smallest in-scope fix and report the rest open. **principle-fix-root-causes** and **principle-redesign-from-first-principles** guide the intent only. Neither one licenses widening the scope or fixing instances outside it. Never bolt on a symptom guard.
6. **Encode the constraints.** A constraint comment says `do not remove`, `do not change the wording`, or `talk to X before changing`. Leave a keep about something we cannot change. For the rest, offer the cheapest enforcement in scope. A type that makes the wrong state unrepresentable, a test (including a grep test for an absence), a runtime precondition, a hook. Wait for the person's approval. An unattended run or an eval needs the caller's approval up front. If approved, encode it, prove it fires, then delete the comment. Otherwise delete the comment, report the constraint as open, and sketch the work that would enforce it.
7. **Prove nothing broke.** `scripts/ai/build.sh`, then `scripts/ai/test.sh` for the touched targets. A change that only deleted comments needs the build alone.

## Reply

The deletion count, any comments restored and why, reruns of the agent, the `/architect` sketch if one was made, the fixes, the encodings offered and made, the constraints left unenforced, and other open work. Then the build and test results.
