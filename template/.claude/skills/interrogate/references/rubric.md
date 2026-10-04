# Review rubric

Each reviewer applies the sections that fall in its lens. Not every section applies to every change. Use judgment. The lens that owns each section most is named in its heading.

## Correctness (every lens)

Does the code do what the intent says?

- Edge cases: empty collections, `nil`, boundary values, the first launch, an empty store, a store with thousands of rows.
- Error handling: is an error caught, propagated, or swallowed? `try?` on a save, a `catch {}` with no handling, and a `Result` nobody switches on all swallow.
- Force unwraps and `as!` on data that crosses a boundary (a fetch, a decode, a URL, user input).
- Off by one, integer overflow, `String.Index` and `count` on grapheme clusters, time zones and `Calendar` math across DST.
- State: a closure capturing a stale value, a `Task` that outlives its view, `self` captured strongly in a long-lived closure.
- Does the happy path work? Does the sad path work?
- Idempotency: what happens if this runs twice, or the app is killed halfway? If the answer is "it depends on what state was left", a reconciliation step is missing.
- Concurrency: if two actors or tasks can touch the same mutable state (a context, a file, a cache), is access serialized by structure (one actor, exclusive ownership, sequential phases) or by a convention that will not hold?

When you find a potential bug, trace the execution path. Do not just flag "this could be nil". Show the call chain that makes it nil.

## Root causes vs. symptoms (every lens)

Is the code fixing the actual problem or papering over a symptom?

Answering this often needs code beyond the diff. Read the callers, callees, type definitions and sibling modules with Read, Grep and Glob. Understand why the code exists before judging whether the change hits the right layer.

- A guard clause that masks a deeper invariant violation.
- A retry, a `DispatchQueue.main.asyncAfter` or a `Task.sleep` that hides a broken ordering contract.
- `MainActor.assumeIsolated`, `@unchecked Sendable` or `nonisolated(unsafe)` that silences a modeling error.
- A fix in module A that belongs in module B's contract.
- Instructions where structure would be better. If the fix is a comment saying "don't do X" or a convention someone must remember, ask whether a type, an access modifier, a test or a check could make the wrong thing impossible.

## Structural integrity (`design`)

Does the code fit the system it is part of?

- Boundary discipline: validation where data enters (a decode, a deep link, an intent parameter), then trusted inside.
- Abstraction level: a view mixing layout with fetching, formatting and persistence.
- Coupling: does the change add a dependency that makes the next change harder?
- Data model fit: do the types match the access patterns? The right structure makes downstream code obvious.
- Bolted on vs. integrated: if the requirement had been known from the start, would the code look like this?
- Legacy dual paths: a new API with the old one kept alive. With no external consumers, migrate the callers and delete the old path in the same change.

Do not penalize simple code for lacking abstraction. Premature abstraction is worse than duplication.

## Verification (`slop`, and every lens for its own claims)

Can you tell this code works from reading it?

- Are there tests? Do they test behavior or implementation details?
- If this is a bug fix, is there a test that fails without it?
- If it touches an integration boundary (Core Data, CloudKit, a network call, an intent), is the full path tested?
- Check the real thing, not a proxy. A test that asserts a mock was called, or a UI check that reads a cached flag instead of the screen, is a verification gap.
- For delegated or async work, does the code check the actual output, or trust a self-report?

## Complexity budget (`design`, `slop`)

Is the complexity justified by what the code does?

- Code that could be simpler without losing correctness or clarity.
- An abstraction (a protocol, a generic, a wrapper view) with one conformer or one call site.
- Configuration or parameters for cases that do not exist yet.
- Dead code, unused imports, vestigial parameters.
- Compatibility paths whose migration is finished. Delete the scaffolding.
- Does the experience justify the complexity? Every setting, control and option should earn its place. Half-finished features are worse than missing ones.

Simpler is better unless simpler is wrong. Three lines of duplication beat a premature abstraction.

## Security and privacy (`privacy-review`)

For each finding, trace the input path through the code and show it.

- Untrusted input (a deep link, a pasteboard read, a push payload, a shared file, model output) reaching a sink: a `WKWebView` script, an `NSPredicate(format:)` string, a file path, a URL opened without validation.
- Secrets in code, Info.plist, logs or error messages. `os_log` and `Logger` interpolations of user data without `privacy: .private`.
- Keychain items with a weaker accessibility class than the data needs.
- Time-of-check to time-of-use gaps in an authorization or entitlement check.
- Data leaving the device that the privacy manifest and the App Store privacy label do not declare.
