---
name: principle-prove-it-works
description: "Apply after completing a task, before declaring done. Prove it on the surface where the user meets it (the running app on the simulator or device, the built bundle) through /verify, scripts/ai/sim.sh, xcui.py and the AI judge; not a proxy, a subagent's self-report, 'it compiles' or 'tests pass'."
disable-model-invocation: true
---

# Prove It Works

Verify every task output by checking the real thing directly. Do not infer from proxies, self-reports, "it compiles" or "the unit tests pass".

**Why:** Unverified work has unknown correctness. Indirect verification (file mtimes, a build that succeeded, a subagent's report, a screenshot from an earlier run) feels cheaper than direct observation. Acting on a wrong inference costs far more than checking the source. "Should work" is a guess.

**Prove it on the surface.** A change is done when its effect was observed where the user meets it. The running app, the built bundle, the device.
- Drive the real path. A launch seam or deep link through `scripts/ai/sim.sh` (`launch`, `openurl`), a UI test, or a real tap through Xcode's device-interaction tools.
- Capture three things. The action, the resulting state, and any side effect (the store, a notification scheduled, a request sent).
- Keep the evidence in a path you name, and put the path in the reply.
- If you cannot reach the surface, say so in those words, with the reason.

Check the real thing, not a proxy:
- Check process liveness directly (`sim.sh alive`), not through derived state such as the absence of a crash report.
- Read the actual value. The installed binary (`sim.sh install` checks it is yours), the built bundle's Info.plist, the row in the store, the element in the UI hierarchy. Not a cached or derived representation.
- When verification fails, suspect the observation method before suspecting the system. Another session's build installed over yours, a screenshot of a process launched with other arguments, a stale `.xcresult`. See `principle-environment-before-code`.

## Script the check when you can

The strongest proof is a deterministic script that reruns the same comparison, not a one-time eyeball.
- `/verify` runs the gates (format, build, tests, seams fenced, blast radius, visual) and keeps a history. A visual gate that ends in JUDGE is not done until the screens are looked at and recorded with `scripts/ai/history.py judge PASS` or `FAIL`, with what was seen.
- `scripts/ai/xcui.py` asserts what a screen shows from the UI hierarchy, which survives restyling better than pixels.
- A UI test or a launch seam plus a screenshot is the durable form for a behavior that must not regress.

Write the script, run it, and keep its output as an artifact a reviewer can rerun instead of trusting your word. Keep the artifact visible for the human. Commit it only for large or complex work where the trail has to be auditable later, like a big port or migration (the `/show-me-your-work` skill).

For UI, the surface includes its edges, per `principle-extremes-are-the-test`. For anything that ships, the Release build is a separate surface, per `principle-release-is-another-app`.
