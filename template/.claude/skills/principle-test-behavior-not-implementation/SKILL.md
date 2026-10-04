---
name: principle-test-behavior-not-implementation
description: "Apply when you write, change, or keep a Swift Testing, XCTest or XCUITest test. Call the code the way its users do and assert the result they observe against a literal expected value. If the test would still pass when every function it calls returned nil, empty or a default, rewrite the assertion or delete the test."
disable-model-invocation: true
---

# Test Behavior, Not Implementation

A test calls the code the way its users do and asserts the result they observe against a literal expected value. A test that asserts which calls the code made, or restates a constant the code contains, does neither.

The check. Before you keep a test, ask whether it would still pass if every function it calls returned `nil`, an empty collection, zero, or a default value. If yes, it observes no behavior and cannot fail for a defect. Rewrite the assertion or delete the test.

**Why:** A test that cannot fail for a defect costs test time and review attention and catches nothing. A constant pin also fails when someone edits the constant or the prompt it restates, so it prevents that edit.

**Five shapes that still pass when every function returns a default:**

- **Weak or no assertion.** No `#expect` or `XCTAssert`, or only `#expect(x != nil)`, `XCTAssertNotNil`, a bare `try` that checks only that nothing threw, `#expect(x is Foo)`, `#expect(items.count > 0)`. In a UI test, only `XCTAssertTrue(app.buttons["Save"].exists)`.
- **Spy or absence only.** Only `#expect(spy.callCount == 1)`, `#expect(spy.called == false)`, `#expect(x == nil)`, `#expect(items.isEmpty)`, `#expect(x != wrongValue)`.
- **Self-referential.** The expected value comes from the code under test. `#expect(f(a) == f(a))`, `#expect(parsed.url == buildURL(...))`.
- **Constant pin.** The assertion restates a hand-maintained constant, a config default, a table row, or a prompt string. `#expect(Limits.maxTools == 8)`, `#expect(Prompt.system.contains("You are"))`.
- **Fixture asserts fixture.** The assertion reads data the test built, or a value computed in `init()` or `setUp()`, and the subject never runs inside the test body.

**The fix:** call the subject inside the test body with one concrete input and assert the literal output or the observable effect. `#expect(slug("Hello, World!") == "hello-world")`. For an absence, assert the presence on the other input in the same test. For a constant, test the mechanism that reads it with one input instead of restating the value. For a spy, assert the payload it received or the state after the call, not that it was called. For a store, assert the rows a fresh fetch returns after the operation. For a UI test, act, then assert the label, value or state the person would see. When no such assertion exists, delete the test.

**Keep** a test of a relation across a table's rows (a key present in two tables, a parent that exists, every enum case with a display name), and a check that exists to fail compilation (a conformance or a type relation asserted in code that must compile).
