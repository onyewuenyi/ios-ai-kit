---
name: principle-outcome-oriented-execution
description: "Apply during planned rewrites and migrations with explicit phase boundaries (ObservableObject to @Observable, UIKit to SwiftUI, strict concurrency, a new navigation model). Converge on the target architecture; don't preserve smooth intermediate states with throwaway compatibility code. Never applies to the person's data."
disable-model-invocation: true
---

# Outcome-Oriented Execution

Optimize for the intended, verifiable end state rather than preserving smooth intermediate states.

**Why:** Keeping every intermediate step fully stable often creates temporary compatibility code that becomes long-lived debt. A bridge between `ObservableObject` and `@Observable`, a UIKit host kept alive for one screen, a `@preconcurrency` import left after the migration. Converge on the target architecture and prove correctness at explicit verification boundaries.

**Core rule:**
- Prioritize end-state integrity over transitional stability.
- Intermediate breakage is acceptable when it is planned, scoped, and reversible.

**Guardrails:**
- Use this for planned rewrites and migrations with explicit phase boundaries, on a branch in its own worktree (`scripts/ai/worktree.sh`), never on the default branch.
- Declare where temporary breakage is acceptable (which target or screen may not build or may not work between which phases).
- Keep high-signal checks for actively touched areas while migrating (`scripts/ai/build.sh`, the focused tests through `scripts/ai/test.sh`).
- Require full static and runtime verification at plan completion. `/verify` passes, and the changed screens are proven on the simulator.
- Breakage is never acceptable in the person's data. A store written by an intermediate build must still open in the final one. Persistence changes follow `principle-additive-data`, phase by phase.
