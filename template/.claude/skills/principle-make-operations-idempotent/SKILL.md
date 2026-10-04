---
name: principle-make-operations-idempotent
description: "Apply when designing launch and store setup, migrations, seeding, sync, share acceptance, notification scheduling, background tasks, or scripts that run amid app termination, relaunches and retries. Converge to the same end state regardless of partial prior runs."
disable-model-invocation: true
---

# Make Operations Idempotent

Design operations so they converge to the correct state regardless of how many times they run or where they start from. Every state-mutating operation should answer two questions. What happens if this runs twice? What happens if the previous run was killed halfway?

**Why:** On iOS, interruption is the normal case. The system terminates a suspended app without notice, a background task expires, a CloudKit push arrives twice, the person force-quits mid-save, a test runner restarts the host. If partial state changes the next run's outcome, every relaunch becomes a debugging session.

**The pattern:**
- **Convergent startup.** Launch scans for existing state (the store, the share, the scheduled requests), cleans stale artifacts, and adopts what is live, instead of assuming a first run.
- **Content-based cleanup.** Deduplicate by content equivalence or a stable identity, not by creation order or "the newest wins". Two devices creating the same record is normal under sync.
- **Stable identifiers make work replaceable.** A `UNNotificationRequest` added again with the same identifier replaces the old one. A `BGTaskRequest` resubmitted with the same identifier replaces the pending one. Choose identifiers derived from the domain, not fresh UUIDs per call.
- **Self-healing locks.** In scripts, use PID-based stale lock detection. In the app, a flag in `UserDefaults` that says "migration in progress" must be checked against the store's real state on the next launch.
- **Idempotent scheduling.** Failed work respawns cleanly, and fresh input is regenerated after each cycle.
- **Seeds and seams refuse or reset.** A seeding seam either refuses a non-empty store or resets it first, never appends on a second run.

**The test:**
1. What happens if this runs twice in a row?
2. What happens if the previous run was killed at every possible point (before save, between two saves, after save before the flag)?
3. Does re-execution converge to the same end state?

If any answer is "it depends on what state was left behind," the operation needs a reconciliation step. Destructive operations also follow `principle-additive-data`.
