---
name: principle-minimize-reader-load
description: "Apply when reviewing or shaping Swift code that's hard to trace. Count the layers between a question and its answer and the hidden state a reader must hold (singletons, environment objects, mutable stores); collapse one-caller wrappers and one-conformer protocols, and shrink mutable scope."
disable-model-invocation: true
---

# Minimize Reader Load

Maintainability is the work a reader must do to understand code. Track two axes.
1. **Layers to trace.** How many indirections sit between the question and the answer.
2. **State to hold.** How much hidden or mutable context the reader must keep in their head.

**Why:** Code is read far more than it is written. Line counts, cyclomatic complexity, and "clean architecture" are proxies. Reader load is the thing that matters. The two axes are independent. A single view file with fifteen `@State` properties synced by `onChange` can be as hard to reason about as a six-layer view, view model, use case, repository, service, store stack. Guard both. This is the human analog of `principle-guard-the-context-window`. Working memory is finite for readers too.

**The pattern:**
- **Collapse layers** that cost more than they save. Wrappers with one caller, protocols with one conformer and no test double, view models that forward every property of a model, speculative indirection that was never needed. Inline them.
- **Make adjacent layers change the abstraction.** A layer that repeats the same methods and arguments adds reader load without compression. Collapse pass-through layers.
- **Demand interface compression.** A broad interface that hides little complexity makes readers learn both the surface and the implementation. Prefer boundaries that hide meaningful decisions.
- **Shrink state scope.** Prefer pure functions (returns over mutations), locals over properties, a view's own `@State` over a shared `@Observable` store, an injected dependency over a singleton or a global. Derive instead of sync. A computed property needs no `onChange` to stay correct.
- **Name the invariant at the boundary,** not in every consumer, so the reader learns it once.
- Before adding a layer or a piece of state, ask whether it reduces reader load somewhere else by at least as much.

**The test:** Can a new reader answer "where does X come from?" and "what can change X?" in under 30 seconds? If not, cut layers or cut state.
