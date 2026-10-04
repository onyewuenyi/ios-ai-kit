---
name: principle-migrate-callers-then-delete-legacy-apis
description: "Apply when introducing a new internal Swift API while old callers still exist. Migrate callers and delete the old API in the same wave instead of keeping @available(deprecated) shims or compatibility layers. Persisted data, CloudKit schemas and shipped app versions are external callers and follow the data rules instead."
disable-model-invocation: true
---

# Migrate Callers Then Delete Legacy APIs

When we decide a new API is the right design, migrate callers and remove the old API in the same refactor wave instead of preserving compatibility layers.

**Rule:**
- Do not keep legacy API paths only because internal callers still exist.
- Inventory callers (the compiler is the inventory; delete the old declaration and read the errors, or grep), migrate them, and delete the old API immediately.
- Treat temporary adapters (an `@available(*, deprecated)` forwarder, an `ObservableObject` wrapper around a new `@Observable` model) as exceptional and time-boxed, not default architecture.
- Update tests to assert the new contract, and delete tests that only protect pre-refactor implementation details.

**When this applies:**
- No external users depend on backward compatibility. Code inside one app target, or a local package only this app imports, qualifies.
- The project can absorb coordinated breaking changes.
- The new API is part of a simplification or refactor initiative.

**When it does not:** some callers live outside the source tree, and the compiler cannot migrate them.
- The persisted store. Every build ever shipped wrote data in the old shape, and the next build must read it. Schema changes follow `principle-additive-data`.
- CloudKit records, which other devices on older builds still read and write.
- A server API, a widget or extension on an older build, App Intents and Shortcuts the person saved, URL schemes, and a Swift package published to others.

For those, the old shape stays readable until no installed build depends on it. Everything else migrates and deletes in one wave.

Keeping both old and new APIs creates dual-path complexity, slows cleanup, and makes the codebase feel append-only.
