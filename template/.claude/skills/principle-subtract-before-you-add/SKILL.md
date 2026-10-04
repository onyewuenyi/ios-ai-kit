---
name: principle-subtract-before-you-add
description: "Apply when sequencing an addition, refactor, or rewrite. Remove dead code, unused views and seams, redundant validators, stale flags and stub references first, then build on the simpler base. The best diff deletes something."
disable-model-invocation: true
---

# Subtract Before You Add

When evolving a system, remove complexity first, then build.

**Why:** Adding to a complex system compounds complexity. Removing first leaves less code, reveals the essential structure, and usually makes the next design obvious. Default to subtraction.

Make simplification a continual investment. Leave the design slightly simpler and more capable behind the same or smaller surface than you found it.

**The pattern:**
- Sequence removal before construction. Delete the unused view, the feature flag that is always on, the protocol with one conformer, then add.
- Cut before you polish (get to the minimum before investing in quality).
- Design for observed usage, not speculative edge cases.
- No speculative validators, parsers, or guards beyond what the spec demands. Each one is a branch a test must cover.
- Simplify prompts. Remove redundant instructions and excessive templates from Foundation Models instructions, from skills, and from CLAUDE.md.
- When a reference has no novel content, delete it rather than leaving a stub.

Removal has one limit on iOS. Code and prompts are yours to delete. The person's data and the persisted schema are not, per `principle-additive-data`. Delete the code that reads a field, never the field in a shipped model version.

See `principle-laziness-protocol` for the size of each change.
