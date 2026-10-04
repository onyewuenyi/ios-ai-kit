---
name: principle-redesign-from-first-principles
description: "Apply when integrating a new requirement into an existing iOS design (a second user, offline, sync, a new platform such as iPad, a new data source). Redesign as if the requirement had been a foundational assumption from day one, instead of bolting it on."
disable-model-invocation: true
---

# Redesign From First Principles

When integrating a change, don't bolt it onto the existing design. Redesign as if the requirement had been there from the start.

- Read all affected files and understand the current design. Send the wide reading to an `Explore` subagent and keep the map, per `principle-guard-the-context-window`.
- Ask "if we were writing this from scratch with this new requirement, what would we build?" A shared household added to a single-user app changes the model's ownership, not just one screen. iPad support changes layout assumptions in every view, not just the root.
- Propagate the change through every reference. Types, the persisted model (as a new version, per `principle-additive-data`), tests, launch seams, `.claude/ios-screens.txt`, docs, examples, and rationale sections.
- Think about the whole redesign, then deliver it incrementally, per `principle-sequence-verifiable-units`.

This is the method for preserving option value when integrating changes into an existing design. It differs from `principle-attack-the-premise`, which questions a fact the current design assumes after fixes keep failing.
