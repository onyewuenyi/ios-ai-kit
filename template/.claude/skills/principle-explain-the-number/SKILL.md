---
name: principle-explain-the-number
description: "Apply before you trust, report, or act on a number you measured (a launch time, a hang rate, a speedup, a regression, a memory figure, a crash rate, a model eval). Find what limits it, rule out that it measured something other than the work you think, and stamp it with build, OS and device or simulator."
disable-model-invocation: true
---

# Explain the Number

A measured number is a claim about a system. Before you trust it, report it, or act on it, find what limits it and rule out that it measured something else.

**Why:** A run that went wrong still prints a plausible number. Requests that failed, a cache that skipped the work, code that never ran, a Debug build or a simulator standing in for a Release build on a device, and run-to-run noise all produce results that look fine. Instruments lie more often than code. If you cannot say why the number is not twice as good, you do not know what you measured.

**Pattern:**

- **Ask "why not double?"** Name the resource or code path that bounds the result. The main thread, an actor or lock, disk I/O, a Core Data fetch, the network, the on-device model, or the harness itself. Get it from a profile or from counters taken during a run (Time Profiler or `xcrun xctrace`, `os_signpost` intervals, the Hangs instrument, MetricKit), then map it to source. A guess from reading the code is not a limiter.
- **List what else the number could be measuring, and rule out each one with evidence.** The usual suspects on iOS:
  - errors (requests that failed fast, a model call that was refused or timed out);
  - skipped or cached work (a warm second launch, a cached image, a seam that did not apply);
  - code that never ran (a feature flag off, a launch argument fenced out, a stale build installed);
  - an untuned side (Debug against Release, simulator against device; simulator numbers are Mac numbers);
  - noise (thermal state, Low Power Mode, a background indexer);
  - a piece too small to matter end to end.
- **Prove the instrument separates.** Show it reads a known-good case as good and a known-bad case as bad before you trust it on the unknown.
- **Keep the evidence with the number.** Report the median and the worst over N of at least 5 runs, with a stamp (build, OS version and build, device model or `sim:`), and the named limiter, in the notes or a linked artifact, so a reader can check the claim.
- **Argue thresholds from per-case values,** never from a summary. A mean hides the one case that fails.

For a performance number, run the full procedure with the `/benchmark-checklist` skill. For a model eval, ask the same of the trials. Did every run do the task (an eval where under about 90% of cases were served is DEGRADED, not a result), does the gap hold across trials and models, and does the scenario matter.

You skipped this when the evidence behind a number has no run count, no spread, no stamp, or no named limiter, or when the time saved is larger than the time the changed piece took.

Distinct from `principle-prove-it-works`, which checks that an output is real. This checks that a measured number means what you say it means.
