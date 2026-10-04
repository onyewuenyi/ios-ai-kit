# Architect runner prompt

The orchestrator passes this file to every candidate runner in Phase B and fills in the variable inputs around it: the task, the Phase A grounding, the runner's working directory (its own worktree from `scripts/ai/worktree.sh new`, or a per-runner folder in the scratchpad), and the path to write outputs. What matters is independence between candidates.

You are producing one candidate design in architect's parallel exploration. Read `.claude/skills/architect/SKILL.md` in full first. That is the workflow you are inside. Output a candidate design package: a Swift type sketch, function and protocol signatures, a module map, and a prose rationale shaped per [`rationale-template.md`](rationale-template.md). Read [`design-red-flags.md`](design-red-flags.md) before you start, and screen your own candidate against it.

Do not build the app or drive a simulator. If your sketch is Swift files, they must type-check as stubs. Never edit outside your working directory.

Apply this discipline. The orchestrator compares candidates on these axes to pick a base.

- **Caller's usage first.** Write the usage and two or three real call sites (a view, a test, an intent) before the types, then derive the type sketch from them. The usage is the spec. Reconcile the sketch to the usage, not the reverse.
- **Data structures first.** Get the core types right and the code becomes obvious. Prefer value types and enums with payloads over classes with flags. Trace each dominant access pattern through the proposed structure. If the answer is "we'll add an index or a cache later", the structure is wrong.
- **Interface depth.** Compare the capability hidden behind the public surface with the size of that surface. Prefer a simple interface that pulls complexity into the callee, even when the implementation becomes less simple. Never put `NSManagedObject`, `PersistentModel`, a `Codable` DTO or a `URLResponse` on the public API. Parse into domain types behind the interface.
- **Isolation is part of the shape.** Name the actor every type lives on. `@MainActor` for what the UI reads, an `actor` or a `@ModelActor` for what does I/O, `Sendable` values across the boundary. If two actors might both write, ask "what happens?" If the answer is not "nothing", default to per-actor state with a merge at the read boundary, per `principle-separate-before-serializing-shared-state`.
- **One owner per piece of state.** A SwiftUI view owns state or reads it, never both for one value. Derive instead of sync.
- **Make boundaries visible.** `fatalError("not implemented")` bodies, `// TODO:` pseudocode for tricky logic, doc comments stating intent and invariants. A reader should trace data from input to output by reading types and signatures alone.
- **Encode invariants in types.** Hard-to-misuse types beat runtime checks, which beat prose comments, per `principle-encode-lessons-in-structure`. An exhaustive `switch` with no `default` makes a new case fail the build.
- **Validate at boundaries, trust types inside,** per `principle-boundary-discipline`. Business logic as pure functions a Swift Testing `@Test` can call without a simulator. The shell (views, intents, the app delegate) stays thin.
- **Idempotent state transitions,** per `principle-make-operations-idempotent`. Ask what happens if the operation runs twice, the app is killed halfway, or CloudKit replays the change.
- **Short call chains.** If tracing the flow needs more than three files, flatten the hierarchy, per `principle-laziness-protocol` and `principle-minimize-reader-load`.

You are one of several runners, each on a different Claude model. Produce the best design your model can make. Do not hedge against the others. Differences between candidates are the signal used to pick a base and graft. Converging on a safe-looking middle defeats the exploration.

Return the paths of your sketch and rationale, and one paragraph naming the alternatives you considered and rejected.
