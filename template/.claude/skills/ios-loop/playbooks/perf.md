# Perf

**You own the measurement story. Plan, review, verify the numbers.** A slowness is a number before it is a fix. Tie every fix to a measurement. Do not read source instead of measuring.

For sustained improvement of one metric over many attempts, use `playbooks/hillclimb.md`. This playbook is the one-off fix.

1. **Define the number.** Cold launch to first frame, a scroll's hitch ratio, a view body's cost at N items, a request's latency, peak memory, energy over a fixed task. Name the device class. A simulator number is Mac silicon, never a phone number. Label it `sim:` and confirm any win on a device before claiming it (`playbooks/device-run.md`). Energy and thermal numbers exist only on a device. **Check.** The metric, its unit, the workload and the device class are one sentence in the todo list.
2. **Capture a baseline, vetted by `/benchmark-checklist`.** Prefer a build optimized like the one you ship. A Debug number carries the label `debug` and never compares with a Release one. N ≥ 5 runs, reporting median and worst. Tools, cheapest first:
   - `os_signpost` intervals around the work, recorded with `xcrun xctrace record --template 'Time Profiler' --instrument os_signpost --device <udid> --attach <process> --time-limit 30s --output .build/perf/<slug>/before.trace`
   - the template that matches the number (`'App Launch'`, `'Animation Hitches'`, `'SwiftUI'`, `'Allocations'`, `'Swift Concurrency'`, `'Power Profiler'` on a device)
   - `XCTest` `measure(metrics: [XCTClockMetric(), XCTMemoryMetric(), XCTApplicationLaunchMetric()])`
   - a probe test that times the pure function at realistic scale (for example 240 items)

   The simulator's UDID is `scripts/ai/sim.sh udid`. **Check.** `/benchmark-checklist` passes on the baseline, and the artifact path is recorded.
3. **Bracket the instrument** (principle-explain-the-number). Make it read a known-slow case as slow and a known-fast case as fast before trusting it. Find what limits the number, and rule out that it measured something other than the work you think (a cold cache, a Debug assertion, the simulator's first boot). **Check.** Both bracket cases read correctly.
4. **Profile, then hypothesize.** Run `/how` over the code on the hot path to ground the hypotheses. Read the heaviest stack in the trace. Common iOS causes are work in `body` (formatters, sorting, fetches), O(n²) derivations per row, main-actor I/O, an observed property that invalidates the whole tree, images decoded on the main thread, Core Data faults fired in a loop. Do not claim a ceiling without running it. **Check.** Each hypothesis names a frame in the trace and the mechanism behind it.
5. **Order the fixes by the performance mantras,** cheapest first. Stop at the first that meets the target.
   1. Don't do it. Stop work whose result nothing uses rather than cheapening it.
   2. Do it, but don't do it again.
   3. Do it less.
   4. Do it later.
   5. Do it when they're not looking.
   6. Do it concurrently.
   7. Do it cheaper.

   **Check.** The chosen fix names its mantra.
6. **Fix one thing, re-measure the same way.** If the fix crosses a function boundary, run `/architect` first. Delegate the implementation to an `ios-agent` subagent (model from `MODEL_CODE` in `.claude/ios.env`, `sonnet` by default) with the trace, the frame and the target. Review the diff. Capture a post-fix trace with the same command, the same workload and the same device. Verify each attempt before trying the next (principle-sequence-verifiable-units). Keep a table: hypothesis, change, before, after, kept or reverted. **Check.** Every row has both numbers, and a reverted change is gone from the tree.
7. **Compare the artifacts, not your memory of them.** Export both traces (`xcrun xctrace export --input <trace> --toc`, then `--xpath` for the table you need), load the rows into sqlite in a subagent (principle-guard-the-context-window), and diff them. Run every post-fix number through `/benchmark-checklist`. "Inconclusive" or a different surface is not a pass. Flag it. **Check.** The delta is past the run-to-run noise, from the same query on both captures.
8. **Confirm a simulator win on a device** (`playbooks/device-run.md`) before calling it a win. **Check.** A device number with its model and OS build, or the reply says plainly that only the simulator was measured.
9. **Pin the win** with a performance test or a probe that fails when it regresses past a stated budget. **Check.** The pin fails against the pre-fix code.
10. **Run `/verify`, then the Opening a PR playbook** (`playbooks/opening-a-pr.md`, `scripts/ai/pr.sh`). Cite the measurement in the PR. `/verify` runs the gates and the AI judge on the visual sheets, recorded by `scripts/ai/history.py judge`. **Check.** Every gate passes, the visual verdict is recorded, and the PR link exists.

**Reply:** the metric, baseline and post-fix numbers (median and worst, runs, device or `sim:`), the delta, the trace evidence for the cause, the table of tried changes, the artifact paths, the budget now pinned, and the PR link.
