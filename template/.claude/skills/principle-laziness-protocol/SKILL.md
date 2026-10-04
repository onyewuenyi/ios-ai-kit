---
name: principle-laziness-protocol
description: "Apply when refactoring, evaluating diff size, or tempted to add a protocol, a wrapper, a layer, or thread a new flag through views, models and persistence. Bias toward deletion and the smallest change that solves the problem; prefer a derived value to a stored one and an enum to parallel booleans."
disable-model-invocation: true
---

# Laziness Protocol

Aim for the most result with the least code and complexity. The best diff deletes something.

- **Prefer deletion.** When asked to refactor or improve, look for removals before additions. Prefer removing the cause to adding a guard.
- **Maintain a flat call hierarchy.** Avoid deep call chains. A rich interface that hides substantial work is not a deep call chain. If answering a question requires tracing through more than 3 files or layers (view, view model, service, repository, store), flatten it.
- **Consolidate decisions.** Do not repeat the same choice in several places. Put it behind one source of truth and pass the result as a simple value.
- **Derive instead of store.** A computed property cannot drift. A second `@State` or stored property kept in step by `onChange` will. Prefer an enum to parallel booleans.
- **Minimize the diff.** Make the smallest change that solves the problem. Fewer lines beat "elegant" boilerplate.
- **Match the codebase's idioms.** A new pattern (a new dependency container, a new navigation scheme, a new persistence wrapper) needs a reason stated in the reply.
- **Question the threading.** If a task asks you to pass a new signal through view initializers, the environment, the Core Data model, sync and telemetry, stop and look for a more direct path.
- **Sweat the small leaks.** Remove tiny pass-throughs, representation leaks, and duplicated choices before they spread. Small leaks compound into permanent coordination costs.

**The test:** If a human developer would find the code exhausting to maintain, it is a bad solution.

See `principle-subtract-before-you-add` for the order of work, and `principle-minimize-reader-load` for the reader's side.
