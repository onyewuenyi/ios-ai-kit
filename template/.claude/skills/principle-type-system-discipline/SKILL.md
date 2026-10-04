---
name: principle-type-system-discipline
description: "Apply when designing Swift types, reviewing a signature, or writing any typed code. Make illegal states unrepresentable with enums carrying associated values, wrap semantic primitives (struct TaskID), parse Codable and Core Data at boundaries, refuse force casts and unwraps, switch exhaustively with no default over your own enums, derive from authoritative schemas."
disable-model-invocation: true
---

# Type System Discipline

The type checker is a proof assistant. Use it to eliminate impossible states, mismatched primitives, and unhandled variants at compile time. A case the types let you ignore becomes a runtime failure the compiler could have stopped. Prefer defining errors and special cases out of existence over proliferating handlers. Unrepresentable states, total functions, and interface redesign (the patterns below) are the tools.

Applies to any typed language. On iOS that is Swift. The `/swift-best-practices` skill grounds it in Swift 6 syntax.

**The patterns:**

- **Make illegal states unrepresentable.** Model variants as enums with associated values. Don't model state as a bag of optional properties where contradictory combinations compile. A subtle anti-pattern is `struct Task { var completed: Bool; var completedAt: Date? }`, which admits `completed == true, completedAt == nil`, a meaningless value. Derive the boolean from a single source (`var completed: Bool { completedAt != nil }`), or model the variants explicitly as `enum Status { case open; case done(at: Date) }`. If a bug forces the question "wait, can this combination actually happen?", the type is too loose.
- **Types are constructions, not restrictions.** Build the type up from the values you want instead of carving them out of a looser type with checks. The invariant that seems to need a refinement type is usually a construction away. A non-empty list is a head plus a rest (`struct NonEmpty<T> { var first: T; var rest: [T] }`), not an array with a count check. A valid time range is a start plus a duration, not two `Date`s you must keep ordered. No representation is privileged. A list of pairs is an even-length list if you interpret it that way, so choose the shape that cannot build the illegal value and expose the interface callers need on top.
- **Wrap semantic primitives.** A task ID and a household ID are both `UUID`s underneath but should not be interchangeable. Wrap each, `struct TaskID: Hashable, Codable, Sendable { let raw: UUID }`. Validate once at creation, trust the type downstream.
- **External data is untyped until parsed.** JSON from `URLSession`, push payloads, deep links, launch arguments, Info.plist values, `UserDefaults`, `NSManagedObject` attributes, `CKRecord` fields, Foundation Models output. Have a parse function at every boundary that turns unstructured input into the typed model (a `Decodable` type, a failable initializer, a `throws` init from a managed object). See `principle-boundary-discipline` for where to put validation.
- **Don't lie to the type system.** `as!`, `!`, `try!`, `unsafeBitCast`, `@unchecked Sendable` and `nonisolated(unsafe)` bypass the compiler and are latent crashes or races. If the compiler can't prove a fact, prove it (validate, narrow, refine the model) or accept that the cast is a hazard and say why next to it.
- **Exhaustive matching is the compiler's job.** When you `switch` over your own enum, list every case and write no `default:`, so adding a case next month fails compilation at every site that must handle it. For a framework enum that is not frozen and may grow (an imported `NS_ENUM` such as `UNAuthorizationStatus`, or a SwiftUI enum such as `ScenePhase`), handle the known cases and add `@unknown default`, which warns when the SDK adds one.
- **Derive types from authoritative schemas.** When a Core Data model, a SwiftData `@Model`, an OpenAPI spec, a CloudKit schema, a `@Generable` type, a string catalog or an asset catalog defines a shape, derive from it (generated classes, generated symbols such as `ImageResource` and `ColorResource`) instead of hand-rolling a parallel type. See `principle-encode-lessons-in-structure`.
- **Strengthen a type only where partiality appears.** A `precondition`, a `fatalError("unreachable")`, a force unwrap or a `guard ... else { return }` that "should never happen" marks the place a type is too weak. Push that check up into the type. Then stop. The type system's job is to track the cases each use site must handle, not to describe the data as precisely as possible. Prefer total functions. `sum` of an empty array is 0, so it takes the plain array. `first` of an empty array has no answer, so a function that must have one demands the non-empty type.

**The tests:**

- "Can I write a comment explaining when this combination of properties is valid?" If yes, the type is too loose. Split it into an enum.
- "Do two of my function arguments share a primitive type but mean different things?" Wrap them.
- "Where did this `as!`, this `!`, this `?? fallback` come from?" Trace it to the boundary and validate there instead.
- "If a case is added next month, will the compiler tell the next agent where to add it?" If no, the `switch` has a `default:` it should not have.
- "Is this type duplicating a shape another file owns?" Derive instead.
- "Am I strengthening this type to keep an operation total, or just to be more precise?" If nothing would otherwise crash, keep the plain type.
