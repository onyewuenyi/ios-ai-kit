---
name: principle-foundational-thinking
description: "Apply before writing logic, when choosing core Swift types and data structures, sequencing scaffold-vs-feature work, asking which actors and tasks share state. Get the data structures right so the views, stores and tests downstream become obvious."
disable-model-invocation: true
---

# Foundational Thinking

**Structural decisions** protect option value. **Code-level decisions** protect simplicity.

**Data structures first.** Get the data shape right before writing logic. Define core types early (the domain `struct`s and `enum`s, the Core Data or SwiftData model), trace every access pattern (what the list reads, what the detail writes, what sync merges), and choose structures that match the dominant paths. The persisted model is the most expensive shape to change later, per `principle-additive-data`.

At code level, DRY the structure, not every line. Types and data models should converge. Three similar statements still beat a premature abstraction or a protocol with one conformer. Prefer explicit over clever. Test behavior and edge cases, not line counts.

**Concurrency corollary.** Before sharing state between actors, tasks or contexts, ask "what happens if another one modifies this concurrently?" If not "nothing", isolate it. See `principle-separate-before-serializing-shared-state`.

**Scaffold first.** If something helps every later phase, do it first. Ask "does every subsequent phase benefit from this existing?" CI, `swift-format`, the test target and its fixtures, shared types, launch seams for `/verify`, and `.claude/ios-screens.txt` are scaffold. Sequence for option value. Setup comes before features, tests before fixes. Keep commits small and single-purpose.

Each increment should land a coherent abstraction or deepen one that exists. Do not spread a new capability across callers as special-case coordination.

Subtraction comes before scaffolding. Remove dead code first, then lay foundations.
