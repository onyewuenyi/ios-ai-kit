# Code quality review

The `design` lens applies this in addition to the design red flags. It is a strict standard on implementation quality, maintainability, abstraction quality and codebase health.

Above all, be ambitious about code structure. Do not stop at local cleanup. Search for "code judo" moves: restructurings that preserve behavior while making the implementation dramatically simpler, smaller, more direct.

## Core prompt

Start from this baseline:

> Perform a deep code quality audit of this change.
> Rethink how to structure and implement it to improve code quality without changing behavior.
> Improve abstractions and modularity, remove tangled control flow, improve succinctness and legibility.
> Be ambitious. If a clear path to a better implementation restructures some of the codebase, propose it.
> Be thorough and rigorous. Measure twice, cut once.

## Dimensions

Apply the ones that are relevant.

0. **Be ambitious about structural simplification.** Do not stop at "this could be a bit cleaner". Look for reframings that make whole branches, helpers, modes, conditionals or layers disappear. A view model whose only job is mirroring a store, a `switch` that a computed property on the enum replaces, a coordinator that a `NavigationStack` path already models. If you can delete complexity rather than rearrange it, push hard for that.

1. **Do not let a change push a Swift file from under 1,000 lines to over 1,000 lines without a strong reason.** Prefer extracting a subview, an extension in its own file, or a type. If the diff crosses the threshold, ask whether the file should be decomposed first. Waive only for a compelling structural reason where the file stays clearly organized.

2. **Do not allow spaghetti growth in existing code.** Be suspicious of new ad hoc conditionals, scattered special cases, or one-off branches inserted into unrelated flows: an `if isOnboarding` in a shared row view, a feature flag checked in five views. Treat "odd `if` statements in random places" as a design problem, not a style nit. Push the logic into a dedicated type, a state enum, or a modifier.

3. **Bias toward cleaning the design, not just accepting working code.** If behavior can stay the same while the structure becomes cleaner, push for the cleaner version. Prefer simplifications that remove moving pieces over refactors that spread the same complexity around.

4. **Prefer direct, boring, maintainable code over clever code.** Treat brittle or magic behavior as a problem: a generic that hides a simple data-shape assumption, a result builder or property wrapper for one use, `AnyView` to unify branches. Flag thin wrappers and pass-through helpers that add indirection without clarity.

5. **Push on type and boundary cleanliness.** Question needless optionals, `Any`, `as!`, and stringly typed keys when a clearer type could exist. Prefer explicit value types and enums with payloads over dictionaries and flag combinations. If a branch leans on a silent fallback (`?? ""`, `default:` in a switch over your own enum) to paper over an unclear invariant, ask whether the boundary should be explicit.

6. **Keep logic in the canonical layer and reuse existing helpers.** Call out feature logic leaking into shared views or the persistence layer, and storage details leaking into views. Prefer the existing formatter, store method or modifier over a bespoke one. Push code toward the right module instead of normalizing drift.

7. **Treat needless sequential orchestration and non-atomic updates as design smells when the cleaner structure is obvious.** Independent `await`s run one after another could be `async let` or a task group. Related writes that can leave state half applied (two saves, a model update and a file write) should be one transaction. Do not chase micro-optimizations, but flag orchestration that makes the code brittle.

## Output expectations

Report structural regressions and missed simplifications first, then spaghetti and branching complexity, then boundary, type and file-size concerns, then smaller modularity and legibility issues.

## Approval bar

Do not approve merely because behavior seems correct. These are presumptive blockers unless the author can justify them: the change keeps a lot of incidental complexity when a code-judo move would delete it; it pushes a file past 1,000 lines; it adds ad hoc branching that tangles an existing flow; it scatters feature checks across shared code; it adds a needless abstraction, wrapper or cast-heavy contract; it duplicates an existing helper or puts logic in the wrong layer when there is a clear canonical home.

## Tone

Be direct, serious and demanding about quality. Do not be rude. Do not soften major maintainability issues into mild suggestions. If the code makes the codebase messier, say so. If it missed an obvious dramatic simplification, say that too.
