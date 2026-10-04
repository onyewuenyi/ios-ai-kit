---
name: benchmark-checklist
description: Vet an iOS performance measurement before you report or act on it. Seven questions (the limiter, a Release build tuned like production, physical limits, errors, repeatability, end-to-end relevance, whether the work happened), answered with Instruments and xctrace, XCTest measure, device vs. simulator and thermal state. Use when you run a benchmark, or report a speedup or regression you measured.
argument-hint: "[the claim you expect to make]"
disable-model-invocation: true
---

# Benchmark checklist

**Job:** make every performance number you report survive seven questions, answered with evidence from a run, or be reported as inconclusive with the gap named.

**Not my job:** finding and fixing the slowness (the perf playbook in `ios-loop`) · looping on one metric (the hillclimb playbook) · deciding which number the product should care about.

**When there is nothing to report:** "The measurement holds", with the claim, the run count and range, the limiter, and the device.

Use this when you produce a performance number: a PR's before and after, a regression claim, a hillclimb harness, a library or configuration choice. `principle-explain-the-number` says why. Answer each question with evidence from a run, not from a guess about the code.

For a quick ballpark the user asked for, one run is enough. Still check questions 4 and 7, and say it is one run. Skip the rest unless that run looks wrong. A choice between options is never a ballpark.

## Before you run anything

- **Write down the claim** you expect to make, in the words you would ship ("cold launch to first frame is 30% faster at p50 on an iPhone 15 with 2,000 tasks"). The questions test that sentence.
- **Read the measurement code.** Note what it times, what it counts, and what it ignores. For XCTest `measure`, that is the block and its metrics. For `os_signpost`, where each interval begins and ends. For a launch metric, which launch (cold after a reboot, cold after a kill, warm).
- **Check the machine.** On the Mac: `uptime` for load, `sysctl -n hw.ncpu` for cores, `pmset -g therm` for thermal throttling. Every other simulator, build and indexing job on this Mac competes with yours. If you cannot stop them, interleave the sides so both see the same noise, and say so in the report.
- **Check the device.** Charged or on power, Low Power Mode off, not hot to the touch. Record `ProcessInfo.processInfo.thermalState` at the start and end of the run (`.nominal` or `.fair`). A run that ends `.serious` or `.critical` measured the throttle, not the code.

## The questions

1. **Why not double?** Name the limiter. Profile in a run you do not report, because Instruments slows the work it watches. Use the Time Profiler (`xcrun xctrace record --template 'Time Profiler' --attach <pid>`, or `--launch`), System Trace for blocked threads and I/O, Animation Hitches for scrolling, Allocations for memory churn, `sample <pid>` for a quick stack. Map the hot spot to source. Watch the driver too. If the UI test or the script that feeds the work saturates first, you measured the driver. If a change did not move the number, the limiter explains why, so find it before you call the change useless.
2. **Was it tuned?** Run every side the way it ships.
   - A Release build (`scripts/ai/build.sh -configuration Release`), never Debug. Debug is `-Onone`, and it can be ten times slower in Swift generics and collections.
   - No debugger attached, and the scheme's diagnostics off (Address and Thread Sanitizer, Main Thread Checker, Zombies, malloc stack logging).
   - No debug logging: `-com.apple.CoreData.SQLDebug`, verbose `os_log` levels, and DEBUG-only launch seams all cost time.
   - Production data at production size, caches as warm or cold as users see them, the same OS and app versions.
   - If one side runs on defaults, you compared configurations, not implementations. A limiter that is a setting (a save per row, a missing fetch index, `returnsObjectsAsFaults` off for a list of thousands, a Debug build) means that side is untuned. Tune it and measure again before picking a winner. If you cannot tune it, do not pick a winner from that run. Narrowing the claim to the code as it ships today does not fix this when the user is choosing what to adopt.
3. **Did it break limits?** Do the arithmetic. Compare bytes per second with flash and network bandwidth, and operations per second times the cost per operation with the cores you have. A frame has 8.3 ms at 120 Hz and 16.7 ms at 60 Hz. Compare the time saved with the time the changed piece took. Removing a piece that takes 10% of the run can make the run at most about 11% faster. A result past a limit means the run measured something other than the work: a cache, a no-op, a bug.
4. **Did it error?** Count failures and check that the outputs are correct, not just present. A fetch that threw, a decode that returned `nil`, a request that got a 429, a model call that hit its guardrail: errors behave differently from successes. Rejections are often fast, and timeouts and retries are slow. If the harness does not count errors, add the count.
5. **Does it reproduce?** Run each side at least 5 times, and alternate the sides (A, B, A, B) so warmup, lazy initialization, caches, dyld and thermal drift do not favor one side. XCTest `measure` runs 5 iterations by default; set `XCTMeasureOptions.iterationCount` higher when the spread is wide, and remember its first iteration is often a cold outlier. Report the median and the range. A gap smaller than the run-to-run variation is no measurable difference. When the call is close, use a rank-sum test or the harness's own statistics.
6. **Does it matter?** Next to any micro result, measure the end-to-end path a person waits on: launch to first frame (`XCTApplicationLaunchMetric`), a tap to the next screen, a scroll's hitch ratio, with realistic data sizes. Report the micro result as a share of the whole. A helper that takes 1% of a screen's load can make it at most 1% faster.
7. **Did it even happen?** Confirm the work ran inside the timed region. The fetch fired its faults, the rows were saved, the image was decoded (not merely loaded), the view body was evaluated (a `LazyVStack` row off screen is never built), and the code used the result. In a Release build the optimizer deletes work whose result nobody reads. A `lazy` sequence nobody iterates, a `Task` nobody awaits, and a timeout all produce numbers for work that never happened.

## Simulator vs. device

A simulator number is a Mac number. The simulator runs on the Mac's cores, memory and storage, with a different GPU path and no thermal limits like a phone's. Label every simulator result `sim`. Use it to compare two sides on the same Mac, never as an absolute. Confirm any claim a user would feel on a physical device, in Release, and say which device.

## Report

- Lead with the verdict: faster, slower, no measurable difference, or inconclusive.
- Give the number with its unit, the run count, the range, the limiter, the build configuration and the device. For example: "cold launch p50 412 ms → 338 ms, median of 7 runs per side, range 331 to 349 ms after, Release, iPhone 15 on iOS 27.0, thermal nominal, bound by the first Core Data fetch on the main thread."
- Call the verdict inconclusive when you claim a difference but cannot name the limiter, when a side ran untuned, when the device throttled, or when you could not check questions 4 and 7. Name the gap.
- Keep a PR body to one primary number. Put the runs, the range and the limiter evidence in a linked file or the `.trace`.

## How this fits the other perf material

- The **perf** playbook in `ios-loop` finds and fixes slowness. This skill vets its baseline before the playbook plans from it, and every number after that.
- The **hillclimb** playbook loops on one metric. This skill vets its harness before the harness is frozen. The frozen harness then prints error and work counts, so each keep-or-revert checks questions 4 and 7 for free.
