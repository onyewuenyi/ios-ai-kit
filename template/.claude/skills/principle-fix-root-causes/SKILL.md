---
name: principle-fix-root-causes
description: "Apply when debugging a crash, hang, wrong value or flaky test. Reproduce first with a rate, read the faulting thread, ask why until you reach the cause and fix it there; resist the guard let, retry or delay that silences the symptom. For restart bugs, suspect persisted state first."
disable-model-invocation: true
---

# Fix Root Causes

When debugging, do not fix symptoms. Trace every problem to its root cause and fix it there.

**Why:** Symptom fixes accumulate. Each workaround makes the system harder to reason about, and the real bug remains. A nil-check, a retry or a delay that makes the symptom stop is a new bug with a later date. Root-cause fixes are slower upfront but reduce total debugging time.

**Pattern:**
- **Reproduce first, with a rate.** "Crashes 4 of 6 launches with the seeded store" is a reproduction. "Crashed once" is not. No fix before the reproduction, and rerun the same reproduction after the fix to show the rate went to zero.
- **Read the evidence before forming a theory.** The faulting thread of the crash report (`scripts/ai/sim.sh crashes`), the exception reason, the hang's main-thread stack. Some traps write no report, so also check `sim.sh alive`.
- **Separate the three parts.** The trigger (what starts it), the masking condition (why it happens only sometimes), and the symptom (what you see). The fix goes at the trigger.
- **Ask "why" until you hit the root cause.**
- **Do not add guards.** A `guard let`, `?? default`, `try?` or `if !isEmpty` that silences a crash is a symptom fix. So is a `Task.sleep`, a `DispatchQueue.main.asyncAfter`, or a retry.
- **If a workaround needs a paragraph-long comment to justify it, the code is wrong.** Fix the code, not the comment.
- **Check for the pattern, not just the instance.** Grep for the same pattern and fix all instances.
- **When stuck, instrument. Don't guess.** Add a `Logger` line, stream it with `log stream`, set a breakpoint, read the actual error and its `userInfo`.

**Restart bugs. Suspect state before code.**

When something "fails after restart" or "only on this device", suspect stale persistent state first. The Core Data or SwiftData store, `UserDefaults`, Keychain items (they survive an uninstall), caches in the app container, files in the App Group, and the installed build itself. If `scripts/ai/sim.sh reset-app` restores behavior, prioritize state validation as the fix. If nothing in the app explains it, check the environment per `principle-environment-before-code`.

When two fixes for the same symptom have both failed, stop fixing and switch to `principle-attack-the-premise`.
