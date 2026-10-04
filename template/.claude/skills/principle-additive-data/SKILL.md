---
name: principle-additive-data
description: "Apply to any change to the data model, persistence, sync, CloudKit, or a destructive path (reset, clear, dedupe, migrate). The person's data is never the experiment. A schema change is a new version that is a superset of the last; destructive paths back up first, touch only what they name and report what they did; content leaves the device only through a stated path."
disable-model-invocation: true
---

# Additive Data

The person's data is never the experiment. Code can be reverted. A store that a build corrupted, or records a sync deleted on every device, cannot.

**Why:** Every build ever shipped wrote data in its own shape, and the next build must open it. A Core Data model version edited in place makes the shipped store unreadable. A CloudKit schema is additive only once deployed to Production. A "self-heal" that resets a store on a sync error can wipe both the local and the mirrored copy. Each of these is a one-way door.

**Pattern:**
- **A schema change is a new version that is a superset of the last.** Add a model version (or a new SwiftData `VersionedSchema` with a migration stage) and make it current. Never edit a shipped version in place. Nothing removed, no type changed, no optional made required, every new attribute optional or defaulted, every relationship with an inverse. A change of meaning is a new field beside the old one.
- **Prove the migration on a real old store.** Install the previous build, seed it, install the new build over it without deleting the app, and read the data back. A test that opens a fixture store of the old version with the new model is the durable form. The `schema-change` playbook in `ios-loop` holds the steps.
- **Destructive paths back up first, touch only what they name, and report what they did.** Copy the store files (`.sqlite`, `-wal`, `-shm`) before a reset or a dedupe. Delete by an explicit predicate, never "everything that is not X". Tell the person what was removed, in numbers.
- **Measure a destructive path with a plain-launch guard between runs,** per `principle-environment-before-code`, so a broken simulator does not pass for a broken store.
- **Content leaves the device only through a path the app states,** in words that are true. A new network call, model call off device, analytics event or share that carries user content is a product decision, not an implementation detail.
- **Ask before the one-way doors.** Deploying a CloudKit schema to Production, deleting user data you did not create, and anything that sends content off the device, per `principle-never-block-on-the-human`.

**The test:** If this build shipped and then was pulled, would every person's data still open in the previous build and the next one? If the answer depends on luck, the change is not additive.
