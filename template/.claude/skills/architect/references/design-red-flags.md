# Design red flags

Screen every candidate before synthesis. A red flag is a reason to revise or reject the shape. The `design` lens of `/interrogate` reviews a diff against this same list.

Every flag below is written for the next contributor, an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles.

## Shallow module

A shallow module exposes a large interface while hiding little complexity. Judge depth by the capability and policy hidden behind the public surface relative to the size of that surface. Prefer a simple interface backed by substantial behavior.

Do not confuse a deep module with a deep call chain. A deep call chain scatters understanding across layers. A deep module concentrates capability behind one interface.

Signs:

- Callers coordinate several methods to complete one operation.
- Public options expose internal stages or implementation choices.
- Learning the interface does not save the caller from learning the implementation.

```swift
// Shallow: every caller must know the order, and the context it must use.
let request = store.makeFetchRequest(for: .overdue)
store.applyDefaultSort(to: request)
let rows = try store.context.fetch(request)
store.markFaultsFired(rows)

// Deep: one call, the policy lives behind it.
let rows = try await store.tasks(.overdue)
```

## Information leakage

Several modules depend on the same internal decision. A representation, policy or protocol detail appears in more than one place, so changing it takes coordinated edits.

Public transport or storage types are leakage. Parse external data into domain types behind the interface. Keep storage schemas, framework objects and protocol details private.

```swift
// Leaks: views hold NSManagedObject, so the Core Data schema is now the view layer's contract.
struct TaskRow: View { let task: CDTask }

// Leaks: a Codable DTO from the server is the type the whole app passes around.
func load() async throws -> [TaskDTO]

// Contained: the store maps rows and DTOs into a value type at its boundary.
struct TaskItem: Identifiable, Hashable { let id: UUID; var title: String; var due: Date? }
func tasks(_ filter: TaskFilter) async throws -> [TaskItem]
```

## Temporal decomposition

Modules are organized by execution order instead of the knowledge they own. Separate `Loader`, `Validator`, `Transformer` and `Saver` types often repeat one representation and its invariants across several boundaries.

Group code around domain knowledge and ownership. Methods that run at different times still belong to one module when they protect the same decisions. A `TaskImport` type that parses, validates and saves one import format beats four types that each know a quarter of it.

## Pass-through method

A pass-through method forwards the same arguments to another method with the same shape. It adds a layer without hiding complexity.

```swift
// Pass-through: the view model adds nothing the store does not already say.
func delete(_ id: UUID) async throws { try await store.delete(id) }
```

Remove it, or move responsibility to the module that can complete the operation. Keep a forwarding boundary only when it adds policy (undo registration, an analytics event, a permission check), adaptation, or a distinct abstraction.

## Split ownership

More than one module writes the same state, or keeps its own copy of it. An agent that edits one writer cannot see the others, so their rules diverge.

```swift
// Two writers: the sheet and the list both set `selection` on the same @Observable model,
// each with its own rule for clearing it after a delete.
@Observable final class TasksModel { var selection: TaskItem.ID? }

// A mirror: @State copies a model value, then drifts the first time the model changes underneath it.
@State private var title: String
init(task: TaskItem) { _title = State(initialValue: task.title) }
```

Give each piece of state one owner. Other modules read it, or ask the owner to change it through one method. In SwiftUI, a view either owns state (`@State`) or reads it (a `let`, a `@Binding`, an `@Observable` reference), never both for the same value. An edit buffer is fine when it is named as a draft and committed back through the owner.

## Two ways to do one task

The design supports more than one way to do the same task. An agent copies whichever way it finds first, so every way keeps gaining callers.

Examples: a `TaskStore.save()` beside callers that call `context.save()` directly. A completion-handler API kept beside its `async` replacement. Both `ObservableObject` and `@Observable` models for one feature. Two date formatters for the same display.

Keep one way. Move callers off the others and delete them in the same change, per `principle-migrate-callers-then-delete-legacy-apis`.

## Importable internals

A caller can reach a module's internals. An agent takes the shortest path that compiles, so it uses them directly and they become part of the interface.

In one app target everything `internal` is reachable from everywhere. Make internals unreachable from outside:

- `private` and `fileprivate` for helpers that belong to one type or file.
- A local Swift package (or a framework target) for a subsystem, with only its interface `public`. An `import` of anything else fails the build.
- Hide the persistence container behind the package: the app imports `TaskStore`, never the `NSPersistentContainer` or `ModelContainer`.

## Hand-synced list

Two or more places list the same items, and adding an item means editing every list. An agent that sees one list updates only that one.

```swift
// Hand-synced: a new tab needs a case, a title in a switch, an icon in another switch,
// and a row in the settings array.
enum Tab { case home, tasks, settings }
let allTabs: [Tab] = [.home, .tasks, .settings]

// Derived: one enum is the registry, everything else reads it.
enum Tab: CaseIterable { case home, tasks, settings
    var title: LocalizedStringResource { ... }   // exhaustive switch: a new case fails the build
    var systemImage: String { ... }
}
ForEach(Tab.allCases, id: \.self) { ... }
```

Keep one list and derive the others from it: `CaseIterable`, an exhaustive `switch` with no `default`, a registry type. If a list cannot be derived (an Info.plist key, a String Catalog entry, a launch-argument table), make a test fail when the lists disagree.
