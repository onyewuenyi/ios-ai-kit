# Swift patterns

Code examples for each rule in `SKILL.md`. The principles behind them are language-agnostic. See **principle-type-system-discipline** and **principle-boundary-discipline**. The examples use `Chore` as the domain type, because `Task` is Swift's concurrency type.

## Enums with payloads

Model variants with an enum. Each case carries only the data that exists in that state, so contradictory combinations cannot be written.

```swift
// Don't. Booleans and optionals let contradictory states exist (loading with an error and data).
struct ChoreListState {
    var isLoading: Bool
    var chores: [Chore]?
    var error: LoadError?
}

// Do. Only valid states exist.
enum ChoreListState {
    case idle
    case loading
    case loaded([Chore])
    case failed(LoadError)
}
```

## Exhaustive switch

No `default:` over your own enums. When a case is added, every switch that must handle it stops compiling.

```swift
var body: some View {
    switch state {
    case .idle, .loading:
        ProgressView()
    case .loaded(let chores):
        ChoreList(chores: chores)
    case .failed(let error):
        ErrorView(error: error)
    }
}
```

An SDK enum that Apple may extend (a non-frozen C enum) needs `@unknown default`. The compiler still warns when a new case appears.

```swift
switch traitCollection.userInterfaceStyle {
case .dark: palette = .dark
case .light, .unspecified: palette = .light
@unknown default: palette = .light
}
```

## Wrapper types

Wrap a primitive that carries meaning, so a `ChoreID` cannot be passed where a `HouseholdID` is expected. Validate once where the raw value enters.

```swift
struct ChoreID: Hashable, Codable, Sendable {
    let rawValue: UUID
}

struct Cents: Hashable, Codable, Sendable, Comparable {
    let rawValue: Int
    static func < (a: Cents, b: Cents) -> Bool { a.rawValue < b.rawValue }
}

func assign(_ chore: ChoreID, to member: MemberID) { /* inputs are trusted */ }
```

A wrapper that needs a rule gets a failable or throwing `init`, and that `init` is the only way in.

```swift
struct ChoreTitle: Hashable, Sendable {
    let rawValue: String

    init?(_ raw: String) {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }
        rawValue = trimmed
    }
}
```

Don't wrap by reflex. Wrap when two values of the same raw type could be swapped by mistake, or when the value has a rule.

## Constructive modeling

Build the type from parts that are all legal, instead of checking a loose type at runtime.

Non-empty, as a first element plus the rest.

```swift
struct NonEmpty<Element> {
    var first: Element
    var rest: [Element]

    var all: [Element] { [first] + rest }

    init(_ first: Element, _ rest: [Element] = []) {
        self.first = first
        self.rest = rest
    }

    init?(_ array: [Element]) {
        guard let head = array.first else { return nil }
        self.init(head, Array(array.dropFirst()))
    }
}

// Don't. [String] plus a check every caller must repeat.
func pickWinner(_ entries: [String]) -> String {
    precondition(!entries.isEmpty, "no entries")
    return entries.randomElement()!
}

// Do. An empty value of the type cannot exist.
func pickWinner(_ entries: NonEmpty<String>) -> String {
    entries.all.randomElement() ?? entries.first
}
```

A time span, as a start plus a duration. Foundation already has it.

```swift
// Don't. A comment holds the invariant.
struct Window {
    var start: Date
    var end: Date  // start <= end
}

// Do. DateInterval traps on a negative duration at construction, and derives end.
let window = DateInterval(start: .now, duration: 2 * 60 * 60)
```

A closed set of options is an enum, not a `String` compared against literals.

## Simplest total type

Don't strengthen everything. Keep `[T]` when every operation on it is total.

```swift
func total(_ amounts: [Cents]) -> Cents {
    Cents(rawValue: amounts.reduce(0) { $0 + $1.rawValue })  // [] is 0, fine
}
```

Strengthen when the loose type forces a lie at a use site. The tells are `!`, `.first!`, and a `fatalError("can't happen")`.

```swift
// Don't. Partiality smuggled past the compiler.
func newest(_ sessions: [Session]) -> Session {
    sessions.max(by: { $0.date < $1.date })!
}

// Do. Strengthen the input, and the force unwrap disappears.
func newest(_ sessions: NonEmpty<Session>) -> Session {
    sessions.rest.reduce(sessions.first) { $1.date > $0.date ? $1 : $0 }
}
```

Weakening the result to `Session?` is the other total signature.

## No `!`, `as!`, `try!`

```swift
// Don't
let chore = chores.first!
let cell = collectionView.dequeueReusableCell(withReuseIdentifier: "chore", for: indexPath) as! ChoreCell
let config = try! JSONDecoder().decode(Config.self, from: data)

// Do
guard let chore = chores.first else { return }

let registration = UICollectionView.CellRegistration<ChoreCell, Chore> { cell, _, chore in
    cell.configure(with: chore)
}
let cell = collectionView.dequeueConfiguredReusableCell(using: registration, for: indexPath, item: chore)

let config = try JSONDecoder().decode(Config.self, from: data)
```

When a failure is a programmer error that no input can cause, say so with a message.

```swift
guard let url = Bundle.main.url(forResource: "Seed", withExtension: "json") else {
    preconditionFailure("Seed.json is missing from the app bundle")
}
```

## Narrowing order

From best to last resort:

1. `switch` over an enum. The compiler narrows and checks exhaustiveness.
2. `if case let` and `guard case let` for one case.
3. `as?` to a protocol or a concrete type.
4. `is`, when only the answer matters.
5. `as!`. Never.

```swift
if case .failed(let error) = state {
    logger.error("Load failed: \(error.localizedDescription, privacy: .public)")
}
```

## Untyped data stays at the edge

```swift
// Don't
let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
let title = json?["title"] as? String ?? ""

// Do
nonisolated struct ChoreDTO: Decodable, Sendable {
    let id: String
    let title: String
    let due: Date?
}

let dto = try JSONDecoder().decode(ChoreDTO.self, from: data)
```

Untyped sources include network payloads, files, `UserDefaults`, the pasteboard, `userInfo` dictionaries on notifications, launch arguments, deep link URLs and App Intent parameters.

## `some` over `any`

```swift
// Don't. An existential box and a dynamic dispatch per call, and the concrete type is lost.
func render(_ items: [any ChoreRow]) -> some View { /* ... */ }

// Do, when the items share one concrete type
func render<Row: ChoreRow>(_ items: [Row]) -> some View { /* ... */ }
```

Keep `any` where the collection really mixes types.

## Codable at the boundary

Decode into a DTO, then convert to the domain type with validation. The conversion is the one place that knows both shapes.

```swift
enum ImportError: Error, Equatable {
    case badID(String)
    case emptyTitle
}

extension Chore {
    init(_ dto: ChoreDTO) throws(ImportError) {
        guard let uuid = UUID(uuidString: dto.id) else { throw .badID(dto.id) }
        guard let title = ChoreTitle(dto.title) else { throw .emptyTitle }
        self.init(id: ChoreID(rawValue: uuid), title: title, due: dto.due)
    }
}
```

- **Persisted JSON** carries a version. Decode with `decodeIfPresent` for fields added later, and keep a decoder for each version you still read.
- **Don't re-validate** deep in call chains. Inside the app, trust the domain type.

## Core Data and SwiftData at the boundary

Managed objects belong to their context and its queue. Map them to value snapshots inside `perform`, and pass IDs between actors.

```swift
struct ChoreSnapshot: Sendable {
    let id: NSManagedObjectID
    let title: String
    let due: Date?
}

func overdueChores(in container: NSPersistentContainer) async throws -> [ChoreSnapshot] {
    let context = container.newBackgroundContext()
    return try await context.perform {
        let request: NSFetchRequest<ChoreEntity> = ChoreEntity.fetchRequest()
        request.predicate = NSPredicate(format: "due < %@", Date.now as NSDate)
        return try context.fetch(request).map {
            ChoreSnapshot(id: $0.objectID, title: $0.title ?? "", due: $0.due)
        }
    }
}
```

SwiftData's `@Model` objects are not `Sendable`. Pass `PersistentIdentifier` across actors, and do background work in a `@ModelActor`.

A schema change is a new model version that is a superset of the last. Never edit the current version in place. See **principle-additive-data**.

## Sendable by construction

```swift
// Don't. The compiler's check is switched off and nothing guards `value`.
final class Counter: @unchecked Sendable {
    var value = 0
}

// Do. An actor, when callers can await.
actor Counter {
    private(set) var value = 0
    func increment() { value += 1 }
}

// Do. A Mutex, when access must stay synchronous (iOS 18+).
import Synchronization

final class Counter: Sendable {
    private let value = Mutex(0)
    func increment() { value.withLock { $0 += 1 } }
    var current: Int { value.withLock { $0 } }
}
```

## Actors and reentrancy

An actor runs one piece of its code at a time, but every `await` lets other calls in. State read before an `await` may be stale after it. Coalesce duplicate work with a stored `Task`.

```swift
actor ThumbnailCache {
    private var cache: [URL: Data] = [:]
    private var inFlight: [URL: Task<Data, Error>] = [:]

    func thumbnail(for url: URL) async throws -> Data {
        if let hit = cache[url] { return hit }
        if let running = inFlight[url] { return try await running.value }
        let load = Task { try await URLSession.shared.data(from: url).0 }
        inFlight[url] = load
        defer { inFlight[url] = nil }
        let data = try await load.value
        cache[url] = data
        return data
    }
}
```

## `@MainActor` ownership

UI state lives on the main actor. In a module built with `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor`, every declaration is main-actor isolated unless it says `nonisolated`. In a module without it, mark UI models `@MainActor` yourself.

Move heavy work off the main actor with a `nonisolated` type and an `@concurrent` function. `Task.detached` drops priority and task-local values, and is rarely what you want.

```swift
nonisolated struct ChoreDecoder {
    @concurrent
    func decode(_ data: Data) async throws -> [ChoreDTO] {
        try JSONDecoder().decode([ChoreDTO].self, from: data)
    }
}
```

One trap in a main-actor-default module. A conformance on a type that is not `Sendable` is main-actor isolated, so decoding that type off the main actor fails with "main actor-isolated conformance of 'X' to 'Decodable' cannot be used in nonisolated context". Declare the DTO `nonisolated`, as `ChoreDTO` is above. Marking it `Sendable` also makes the compiler infer it nonisolated.

## `@Observable` over `ObservableObject`

```swift
@Observable
final class ChoreListModel {
    private(set) var chores: [Chore] = []
    var filter: ChoreFilter = .open

    var visible: [Chore] { chores.filter(filter.includes) }  // derived, never stored

    func reload(from store: ChoreStore) async throws {
        chores = try await store.all()
    }
}

struct ChoreListScreen: View {
    @State private var model = ChoreListModel()
    let store: ChoreStore

    var body: some View {
        ChoreList(chores: model.visible)
            .task { try? await model.reload(from: store) }  // a failed reload keeps the last list on screen
    }
}

struct FilterPicker: View {
    @Bindable var model: ChoreListModel

    var body: some View {
        Picker("Show", selection: $model.filter) {
            ForEach(ChoreFilter.allCases, id: \.self) { Text($0.label) }
        }
    }
}
```

- The view that creates the model owns it in `@State`. A child that only reads takes a plain `let`. A child that binds takes `@Bindable`. App-wide models go in the environment (`.environment(model)`, read with `@Environment(ChoreListModel.self)`).
- Views re-render only for the properties they read. Don't read a large model in a parent that doesn't need it.
- `ObservableObject` with `@Published` stays only where the deployment target is below iOS 17.

## Access control

```swift
@Observable
final class HouseholdModel {
    private(set) var members: [Member] = []  // read anywhere, written here
    private let store: HouseholdStore        // nobody else touches it

    init(store: HouseholdStore) { self.store = store }
}
```

`public` and `open` belong only in a package or framework that exports API, and that API gets `///` doc comments.

## Errors that say what failed

```swift
enum SyncError: Error {
    case notSignedIn
    case quotaExceeded(retryAfter: Duration)
    case conflict(ChoreID)
}

func push(_ changes: [Change]) async throws(SyncError) { /* ... */ }

do {
    try await push(changes)
} catch .quotaExceeded(let wait) {
    scheduleRetry(after: wait)
} catch {
    show(error)  // error is SyncError here, and the remaining cases are known
}
```

Use typed throws where the set of failures is closed and callers act on each case. Keep untyped `throws` where errors from many layers pass through.

Never discard an error silently.

```swift
// Don't
try? context.save()

// Do
do {
    try context.save()
} catch {
    logger.error("Save failed: \(error.localizedDescription, privacy: .public)")
    context.rollback()
}
```

## Real tests

```swift
import Testing
@testable import Chores

@Suite struct ChoreImportTests {
    @Test(arguments: ["", "   ", "\n"])
    func rejectsBlankTitles(_ title: String) {
        let dto = ChoreDTO(id: UUID().uuidString, title: title, due: nil)
        #expect(throws: ImportError.emptyTitle) { try Chore(dto) }
    }

    @Test func keepsTheTitleTrimmed() throws {
        let dto = ChoreDTO(id: UUID().uuidString, title: "  Milk ", due: nil)
        let chore = try Chore(dto)
        #expect(chore.title.rawValue == "Milk")
    }
}
```

Assert against a literal expected value. If the test would still pass when every function it calls returned a default value, rewrite the assertion or delete the test. Use an in-memory store for persistence tests, never the person's data. Run one test with `scripts/ai/test.sh -only-testing:ChoresTests/ChoreImportTests/keepsTheTitleTrimmed()`.

## Labels that read

Swift's argument labels already do what named-object arguments do in other languages. Use them.

```swift
// Don't. Two Dates in a row, easy to swap, and the call site says nothing.
func schedule(_ chore: Chore, _ a: Date, _ b: Date)

// Do
func schedule(_ chore: Chore, from start: Date, until end: Date)
schedule(chore, from: .now, until: deadline)
```

Past about four parameters, group the related ones into a `struct` with defaults.

## Structured logging

```swift
import OSLog

let logger = Logger(subsystem: "com.example.chores", category: "sync")

logger.info("Pushed \(changes.count) changes for \(householdID.rawValue, privacy: .private(mask: .hash))")
```

Interpolated values are private by default in release logs. Mark a value `.public` only when it can never identify a person. Time an operation with `OSSignposter` so it shows in Instruments.
