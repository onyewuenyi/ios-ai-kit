---
name: principle-experience-first
description: "Apply when product, UX, or feature-scope tradeoffs come up in an iOS app. Choose user delight over implementation convenience; ship fewer polished features over more rough ones; prototype in previews and on the simulator before production code."
disable-model-invocation: true
---

# Experience First

When implementation convenience conflicts with user delight, choose delight.

- Every feature, control, and option must be justified
- Ship less, ship better (a polished experience with three features beats a rough one with ten)
- Prototype before committing (design decisions are cheaper in a throwaway `#Preview` or a branch on the simulator than in production code)
- Get the details right (transitions, alignment, spacing, feedback and haptics, empty and error states, Dynamic Type, dark mode)
- Tighten the core loop (every feature should serve the central workflow or get out of the way)

The user is whoever consumes the work. For an app that is the person holding the phone. For a Swift package or an internal API it is the colleague who imports it. The engineer who maintains the code next is a user too. Weigh their experience the same way, and explain impact from their perspective.

Foundations should serve the experience. `principle-foundational-thinking` governs the *sequence* of work. This principle governs the *target*. Judge the target at its edges, per `principle-extremes-are-the-test`.
