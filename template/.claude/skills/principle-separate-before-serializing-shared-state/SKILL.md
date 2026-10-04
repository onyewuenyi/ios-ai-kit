---
name: principle-separate-before-serializing-shared-state
description: "Apply when concurrent actors might write the same state (Swift tasks and actors, Core Data contexts, UserDefaults keys, files, a branch, a simulator, a checkout shared by two Claude sessions). Eliminate the sharing first with one owner per piece of state; serialize structurally (an actor, @MainActor, a single writer) only when one shared target is a real invariant."
disable-model-invocation: true
---

# Separate Before Serializing Shared State

When concurrent actors might share mutable state, first ask whether they need the same mutable object. If not, eliminate the sharing. When sharing is real, enforce serialization structurally. Isolation the compiler checks (an `actor`, `@MainActor`, `Sendable`), sequential phases, exclusive ownership, a lock file for scripts. Instructions, conventions and comments ("only call this from the main thread") are not concurrency control.

**Why:** Concurrent writes to shared state create race conditions that are intermittent, hard to reproduce, and expensive to debug. Swift 6 strict concurrency turns many of them into compile errors, but only for state you have given an owner.

**Pattern:**
1. **Identify shared mutable state.** A class instance two tasks mutate, a managed object touched off its context's queue, a `UserDefaults` key two features write, a file two processes write, a branch two sessions push to, a simulator two sessions install on.
2. **Default: eliminate the shared write target.** Ask whether these actors need one canonical object or are publishing independent facts. Give each actor its own owned value, key, context, file, branch, or simulator, and merge only at the read or reporting boundary.
   - Two features writing their own `lastRunAt` field into one shared settings dictionary is still shared mutation. Two keys, or two small stores, are not.
   - One background `NSManagedObjectContext` per writer, merged into the view context, beats many writers on one context.
   - Value types (`struct`, `enum`) passed across tasks share nothing. Prefer them to a shared reference that needs a lock.
   - Two Claude sessions in one checkout share the working tree, DerivedData and the simulator. Give each its own worktree (`scripts/ai/worktree.sh`), which gives each its own `.build/dd` and simulator, and stage by path, never `git add -A`.
3. **Only when one shared write target is a real invariant, serialize access structurally.** One owner per piece of state. UI state is `@MainActor`. A shared cache or store is an `actor`, or a type whose only mutable state is behind one. A Core Data context is used only inside its own `perform`. Treat "we need a lock" (`NSLock`, `os_unfair_lock`, a serial `DispatchQueue`) as a design smell to check, not as the default answer. `@unchecked Sendable` and `nonisolated(unsafe)` are claims the compiler cannot check; each needs the reason it is true next to it.

`principle-foundational-thinking` asks the same question earlier, when the types are chosen.
