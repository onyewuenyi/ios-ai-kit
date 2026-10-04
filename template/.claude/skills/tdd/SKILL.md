---
name: tdd
description: "Fix a bug test-first in an iOS app: a focused Swift Testing or XCTest regression test that fails before the fix and passes after, run with scripts/ai/test.sh -only-testing. Use only when the person asks for TDD, a failing test or a regression test, or when the bug has an obvious cheap local test target. Skip when the test path is unclear, expensive, UI-heavy or not requested."
disable-model-invocation: true
---

# TDD bug fix

**Job:** make the broken behavior executable before changing production code, so one focused test fails before the fix and passes after it.

**Not my job:** coverage beyond the bug · a test that needs a broad new harness or fixture · rewriting existing tests to match the fix · proving UI on the surface (`ui-verify`, `/verify`).

**When there is nothing to report:** "No practical test path", with the reason and the closest regression check used instead, and its result.

Don't force a test when it would be impractical. If the only available test needs a broad new harness, brittle mocks, slow end-to-end infrastructure, a physical device, production-only state, vague reproduction steps or large unrelated fixture churn, skip the new test and use the closest useful check instead.

## Workflow

1. **Understand the bug.** Name the intended behavior, the current behavior, the code path, and the smallest observable reproduction.
2. **Choose the narrowest executable check.** Prefer the closest test the codebase already uses for that path. A Swift Testing `@Test` in an existing `@Suite`, or a method in an existing `XCTestCase`. Match the framework of the neighboring tests. Models, stores, parsers and pure functions test cheaply. If no practical test path is obvious, do not build one from scratch to satisfy this workflow.
3. **Write the failing test first.** Add the smallest focused test that would have caught the bug. It encodes the intended behavior, not the current implementation. Call the code the way its callers do and assert against a literal expected value (**principle-test-behavior-not-implementation**).
   - **Swift Testing.** `#expect(store.tasks.map(\.title) == ["Milk", "Eggs"])`, and `#require` to unwrap an optional or stop early. `@MainActor` on the test when the code under test is main-actor isolated. `await confirmation { … }` for a callback that must fire.
   - **XCTest.** `XCTAssertEqual`, `XCTUnwrap`, and `XCTestExpectation` with `fulfillment(of:timeout:)` for async callbacks.
   - **Persistence.** An in-memory store (`NSPersistentStoreDescription` with `url = URL(fileURLWithPath: "/dev/null")`, or `ModelConfiguration(isStoredInMemoryOnly: true)`), never the person's data.
4. **Run the new test before fixing.**

   ```bash
   scripts/ai/test.sh -only-testing:AppTests/TaskStoreTests/importKeepsExistingTasks()   # Swift Testing, the () is required
   scripts/ai/test.sh -only-testing:AppTests/TaskStoreTests/testImportKeepsExistingTasks  # XCTest, no ()
   ```

   Confirm it fails for the intended reason. "Nothing ran" is not a failure of the test. It means the identifier is wrong. If the test passes, or fails for an unrelated reason, correct the test or the reproduction before touching the implementation.
5. **Fix the bug.** The smallest production change that gives the intended behavior and keeps the nearby contracts.
6. **Rerun the regression test,** then the suite it lives in. Confirm both pass.

## When a failing test is impractical

Use the closest executable regression check instead. A launch-argument seam with `scripts/ai/sim.sh launch`, a hierarchy assertion with `scripts/ai/xcui.py`, a screenshot compared with `sim.sh compare`, a log assertion, a script.

Prefer no new test over a bad test. A bad test mostly tests mocks, encodes implementation details, depends on timing, the simulator's state or other global state, needs expensive infrastructure for a small fix, or would be deleted right after proving the fix.

## Guardrails

- Never change a test to match a wrong implementation.
- Never weaken an existing assertion unless the expected behavior genuinely changed and the reason is stated.
- Keep the regression test on the bug. No broad fixture churn, no unrelated coverage.
- If the bug is flaky, make the test deterministic where possible (inject the clock, the random source, the scheduler), and say which signal it locks down. Never retry a flaky test green.
- Tests that share one in-memory store need serial execution (`.serialized`, or the project's `-parallel-testing-enabled NO`). Follow what the project already does.
- If the bug exposes a broader class of failure, land the focused regression test first, then consider sibling coverage.

## Reply

Report the evidence, not only the outcome.

- The failing-before test or check, and the failure it produced.
- The passing-after run, and any nearby validation (the suite, `/verify`).
- If failing-before could not be shown, why, and the closest regression check used instead.
