# Build the change and clean the diff

The build playbooks share one discipline. Say what you observed, and let the playbook demand the evidence. This page shows what to put in the prompt for each common build task, then the cleanup habit that keeps diffs reviewable.

## Prompt each build playbook with what you know

A bug prompt states the symptom and asks for a reproduction first.

```text
/ios-loop the app hangs for about a second when the task list opens with 500 tasks. repro first, then fix and verify.
```

A feature prompt states the behavior and what must not change.

```text
/ios-loop add swipe-to-snooze on task rows. the existing swipe-to-delete stays exactly as it is. verify both swipes and the largest text size.
```

A refactoring prompt pins behavior before structure moves.

```text
/ios-loop move the task filters out of TaskListView into a FilterModel, zero behavior change. capture the screens first and prove they're unchanged after.
```

A perf prompt states the measurement, not a vibe.

```text
/ios-loop cold launch to first frame is 1.8s in a Release build on this fixture. trace it with Instruments, fix the measured cause, show me before and after.
```

A schema prompt names the model change and the data it must keep.

```text
/ios-loop add a "snoozedUntil" date to Task. new model version, lightweight migration, and an existing store opens with every task intact.
```

Each of these routes to its playbook (Bug fix, Feature, Refactoring, Perf, Schema change), and the playbook supplies the steps you didn't type. Reproduce with a rate before fixing. Name the data shape before implementing. Pin behavior before restructuring. Profile a Release build before optimizing, and remember that simulator numbers are Mac numbers, so a device confirms them. Add a model version before touching a field, never edit the shipped one.

For a hang or a leak you can watch happen, the Runtime forensics playbook works from the live app (Instruments' Hangs and Allocations, `memgraph`, `log stream`). For a `.trace`, an `.ips` crash report, a spindump or a sysdiagnose someone hands you, it is Trace forensics. Neither guesses before reading the faulting thread.

For sustained improvement of one number, there is the Hillclimb playbook. Give it the metric, a target, and a floor on attempts, such as on-device model latency or the scroll hitch ratio. It loops one hypothesis at a time with a frozen measurement harness, keeps wins, and reverts everything else.

## Write the failing test first with `/tdd`

When a bug has a cheap local test path, the whole prompt can be two words.

```text
/tdd implement
```

In context, that is enough. [`/tdd`](../../template/.claude/skills/tdd/SKILL.md) writes the smallest Swift Testing (or XCTest, where the target uses it) test that fails for the intended reason, runs it with `scripts/ai/test.sh -only-testing:<Target>/<Suite>/<test>()` to watch it fail, then writes the fix and reruns. "Nothing ran" counts as a failure, not a pass. If a test would need a mocked `NSPersistentCloudKitContainer` or a UI test that waits on animations, the skill says so and uses the closest executable check instead, such as a launch seam and a screenshot. Don't force a test where the running app is stronger evidence.

## Let the Swift rules load themselves

`swift-best-practices` has no slash command in your workflow. It loads whenever the agent touches a `.swift` file and turns the type-system principles into concrete Swift 6 rules. Enums with payloads instead of parallel booleans. Exhaustive `switch` with no `default` over your own enums. Value types by default. `Sendable` and actors for shared state, and one clear `@MainActor` owner for UI state. `@Observable` over `ObservableObject`. `Codable` validation at the boundary, trusted types inside. Apple's exported skills (`swiftui-specialist`, `swiftui-whats-new-27`) still win on any API question.

Formatting is not a rule you remember. `swift-format` runs on every Swift edit, and the Stop hook will not let a turn end on a broken build. It shows the exact error instead.

## Clean before you commit

The Opening a PR playbook cleans the diff before each commit and runs [`/unslop`](../../template/.claude/skills/unslop/SKILL.md) over the PR description and commit bodies. Code slop gets the same treatment from the slop lens of `/interrogate`. Narrating comments, a `guard` for a state the types already rule out, a dead `#available` branch below your deployment target, a `print` left behind, and edits unrelated to the task all go.

For prose, `/unslop` takes a target and any extra rules you have.

```text
/unslop the changelog entry, no long dashes
```

You'll develop your own shorthand. The skill reads intent fine from terse prompts like `unslop that, tighten it`.

## Strip the comments with `/no-comments`

Comments need their own pass, and not from the agent that wrote them. An author defends its comments the way you would defend yours. So before review, hand them to fresh eyes.

```text
/no-comments the diff
```

[`/no-comments`](../../template/.claude/skills/no-comments/SKILL.md) spawns the `comment-sicko` agent, a read-only reviewer with a short keep list. It keeps license headers, `///` doc comments on a public API, links that explain what code can't, and behavior forced by something you can't reshape (an Apple framework bug with its Feedback number, a required-reason API declaration). Everything else goes. A surprise in your own code gets no such pass. The comment comes back as a refactor flag, and `/no-comments` fixes the flags it accepts at the root cause. When a comment claims a constraint, like "must stay on the main thread", the skill offers to encode the claim as a type (`@MainActor`), a test, or a lint. Either way, the comment comes out.

Keep the division of labor straight. The slop lens finds slop in the code, `/unslop` cleans it out of prose, and `/no-comments` hands the comments to a reviewer who didn't write them.

**Pitfall.** Cleanup is not optional polish. A diff with narrating comments and defensive dead weight reads as unfinished to reviewers, and the extra code is where the next bug hides. If the diff feels padded, say `clean the diff` before you commit, not after review calls it out.

Next is [Verify and ship](./06-verify-and-ship.md).
