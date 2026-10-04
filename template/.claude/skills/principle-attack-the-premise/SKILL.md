---
name: principle-attack-the-premise
description: "Apply when two or more fixes that share one premise have failed the same gate (a test, a crash rate, a hang, a /verify gate). Write the premise down, take a census of which actors hold the imbalance before the next fix, then question the premise instead of writing another fix that assumes it."
disable-model-invocation: true
---

# Attack the Premise

When two or more fixes that share one premise have failed the same gate, suspect the premise, not the fixes.

**Why:** Each failure under a shared premise is evidence about the premise. Three fixes at one symptom mean the model of the problem is wrong.

**Pattern:**
- **Write the premise down.** The premise is the one sentence that every failed fix assumed. "The list hangs because row rendering is slow." "The test crashes because the fixture is torn down too early." Stop patching until it is written.
- **Test the premise directly.** Design one run whose result would differ if the premise were false. A Time Profiler trace of the hang, the faulting thread of the crash report, a log line at the point the premise names. A fourth fix is not a test of the premise.
- **Take a census before the next fix.** Count the imbalance per actor. An actor is whatever repeats across runs. A test case, a thread or queue, a view, a model object, a simulator, a session. The census shows which actors hold the imbalance, not how large it is. Hang samples per type, crashes per test in the order they ran, invalidations per `@Observable` property. Write the census as a rerunnable script per `principle-build-the-lever`.
- **Read the skew.** If the same few actors hold most of the imbalance on every run, something assigns them that role. The test that always runs first against the shared in-memory store. The one model every row observes. Find what assigns the role. That assignment is the next "why" per `principle-fix-root-causes`.
- **Remove the asymmetry instead of compensating for it**, per `principle-laziness-protocol`. Rotate the role between actors, randomize the assignment, or move the role, so that no actor holds it on every run. A return path, a shared pool, a batched hand-off, or a periodic rebalance leaves the assignment in place and adds work on every run.

**Stop:**
- Do not start the next fix before the premise is written down and the census exists.
- If the census is even across actors, the premise is not the cause. Look for the cause elsewhere and keep the census as evidence.
- If the census looks impossible (every actor fails the same way), check the environment before the code, per `principle-environment-before-code`. A broken simulator runtime fails every actor alike.

This principle is distinct from `principle-redesign-from-first-principles`, which rebuilds a design around a new requirement. This one questions a fact the current design assumes.
