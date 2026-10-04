---
name: swift-best-practices
description: Swift 6 and SwiftUI best practices for writing or reviewing .swift code. Value types, enums with payloads, exhaustive switches, wrapper types, no force unwraps or casts, Sendable and actors, @MainActor ownership, @Observable over ObservableObject, Codable and Core Data at the boundary, access control, typed errors, Swift Testing, Logger.
disable-model-invocation: true
---

# Swift best practices

**Job:** hold Swift code to the rules below while writing or reviewing it, and name the rule behind each change.

**Not my job:** API questions about a specific SDK (Apple's exported skills such as `swiftui-specialist` and `swiftui-whats-new-27`, and `DocumentationSearch`, win there) · formatting (swift-format) · comments (`/no-comments`) · changing build settings or the language mode.

**When there is nothing to report:** "Follows the Swift rules", with the two rules the code came closest to breaking.

Apply **principle-type-system-discipline** first. Its sibling **principle-boundary-discipline** governs where parsing happens. Examples for every row are in `references/patterns.md`.

| Rule | Summary |
|------|---------|
| Value types first | `struct` and `enum` by default. A `class` only for identity or shared mutable state, and then `final`. Shared mutable state across tasks is an `actor` or a `@MainActor` model. |
| Enums with payloads | Model variants as an `enum` with associated values so impossible states cannot be written. No bags of optionals, no parallel booleans (`isLoading` plus `error` plus `data`). |
| Exhaustive switch | No `default:` over your own enums, so adding a case breaks every switch that must handle it. `@unknown default` only for non-frozen SDK enums. |
| Wrapper types | Wrap a semantic primitive (`struct ChoreID: Hashable, Codable { let rawValue: UUID }`) so IDs, money and units cannot be mixed up. Validate once in a throwing or failable `init` at the boundary. |
| Constructive modeling | Build the shape so the illegal value cannot be constructed. A non-empty list as `first` plus `rest`, a time span as `DateInterval(start:duration:)`, a closed set as an enum. Not a runtime check repeated at every call site. |
| Simplest total type | Keep `[T]` while every operation on it stays total. Strengthen only where the loose type forces a `!`, a `.first!`, or a `fatalError("can't happen")`. Returning an optional is the other total signature. |
| No `!`, `as!`, `try!` | Each one is a crash waiting for the input that breaks it. Use `guard let`, `if case`, `as?` after validation, and `try` that propagates. A force unwrap is acceptable only on a literal you can see (`URL(string: "https://example.com")!`), never on runtime data. A programmer error gets `preconditionFailure("why")`, not a bare `!`. |
| Narrowing order | `switch` over an enum > `if case let` > `as?` to a protocol or type > `is` > `as!` never. A typed API (`UICollectionView.CellRegistration`, generics) beats a cast. |
| Untyped data stays at the edge | `Any`, `[String: Any]`, `AnyObject`, `JSONSerialization` and `NSDictionary` stop at the parse. Decode into a `Decodable` DTO, then convert to the domain type. |
| `some` over `any` | Prefer generics and `some Protocol` to `any Protocol` existentials. An existential erases type information and costs a box. Use `any` where the values really are heterogeneous. |
| Codable and Core Data at the boundary | Decode wire and file formats into DTOs, map them to domain types with validation, and version persisted payloads. `NSManagedObject` and SwiftData `@Model` objects stay inside their context. Map to value snapshots inside `perform`, and pass `NSManagedObjectID` or `PersistentIdentifier` across actors. |
| Sendable by construction | Value types of Sendable members are Sendable for free. No `@unchecked Sendable` or `nonisolated(unsafe)` without a lock that guards every access and a reason in the type. Prefer an `actor` or `Mutex` (Synchronization, iOS 18+). |
| Actors and reentrancy | State inside an actor can change across any `await`. Re-check after each one, and coalesce duplicate work with a stored `Task`. |
| `@MainActor` ownership | UI state lives on the main actor. Know the module's default isolation (`SWIFT_DEFAULT_ACTOR_ISOLATION`). Heavy work goes to a `nonisolated` type with an `@concurrent` function, not `Task.detached`. In a main-actor-default module, a type decoded or used off the main actor is declared `nonisolated`. Otherwise its conformances are main-actor isolated and the off-main use fails to compile. |
| `@Observable` over `ObservableObject` | Observation (iOS 17+). The owning view holds the model in `@State`. Children get it as a plain property, `@Bindable` for bindings, or `@Environment(Model.self)`. Derive values with computed properties instead of storing copies that drift. |
| Access control | `private` by default, `private(set)` for state others read but must not write, `internal` for the module, `public` only in packages that export API. `final` on classes not designed for subclassing. |
| Errors that say what failed | A closed set of failures is an `enum` conforming to `Error`, with typed throws (`throws(ImportError)`) where the set is closed. Never `try?` away an error without saying why the failure is fine. |
| Real tests | Swift Testing (`@Test`, `#expect`, `#require`, `arguments:`) for new tests. Call real types against in-memory stores. Don't mock what you can run. Verify UI on the simulator. See **principle-test-behavior-not-implementation**. |
| Labels that read | Every argument label reads at the call site. Drop a label (`_`) only when the call reads as a phrase without it. Group many related parameters into a `struct`. |
| Structured logging | `Logger(subsystem:category:)` with explicit privacy on interpolated values. No `print` in shipped code. `os_signpost` (`OSSignposter`) for timing. |

Examples: `references/patterns.md`.
