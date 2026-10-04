---
name: principle-boundary-discipline
description: "Apply when wiring validation, error handling, or framework adapters in an iOS app. Concentrate guards at system boundaries (launch arguments, Info.plist, URLSession, Codable decoding, Core Data and CloudKit records, deep links, model output); trust internal types and keep business logic in pure Swift functions that need no SwiftUI, Core Data or simulator to test."
disable-model-invocation: true
---

# Boundary Discipline

Place validation, type narrowing, and error handling at system boundaries. Trust internal code unconditionally. Business logic lives in pure functions. The shell (views, the app delegate, persistence and network adapters) is thin and mechanical.

**Why:** Scattered validation is noisy, redundant, and gives a false sense of safety. Logic kept out of SwiftUI views, `NSManagedObject` subclasses and `URLSession` delegates can be tested in a plain unit test in milliseconds, without the framework and without the simulator.

**The pattern:**
- **At boundaries:** validate, throw typed errors, handle defensively. On iOS the boundaries are launch arguments and the environment, Info.plist and config files, `UserDefaults` and Keychain reads, `URLSession` responses, `Codable` decoding, Core Data and SwiftData fetch results, `CKRecord`s from CloudKit, deep links and universal links, App Intents parameters, push payloads, pasteboard and share-extension input, and Foundation Models output.
- **Inside the system:** typed values, `throws` propagation, no re-validation. Trust the types.
- **Across the boundary.** Expose domain concepts, not the boundary's private representation. Keep general-purpose mechanism inside and special-purpose policy at the edge.

**Applications:**

Validation and error handling:
- Validate config at parse time (the boundary), not inside business logic. Read the launch argument or Info.plist key once, into a typed value.
- Parse raw data into domain types at the boundary. A `Decodable` DTO or a managed object becomes a domain `struct` in one function.
- Do not re-export transport, storage, framework, or wire types through the public surface. No `NSManagedObject`, `CKRecord`, `HTTPURLResponse` or `[String: Any]` in the API of a view model or a service.
- No redundant `guard let` or `?? default` deep in call chains if the boundary already validated. A force unwrap deep inside is the same smell from the other side.

Code organization:
- Business logic in pure functions with no `import SwiftUI`, `CoreData` or `UIKit`.
- Parse functions are pure transforms from `Data` (or a record) to typed state.
- Prompt construction is structured state in, `String` out. The `LanguageModelSession` call is the shell.
- Scoring and assessment are pure transforms from state to results.

**The tests:**
- "Is this data crossing a system boundary right now?" If not, validation is redundant.
- "Can this be a pure function that the view or the store just calls?" If yes, extract it.
- "Does checking this rule need the simulator, a persistent container, or a network stub?" If yes, the rule lives inside the shell. Move it out.
