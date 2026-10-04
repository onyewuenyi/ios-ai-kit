---
name: how
description: "Explain how a part of this iOS app works: a subsystem, a runtime flow, a screen's data path, where a type lives, which target or module owns it, whether code sits in the right layer. Use for \"how does X work\", a walkthrough before changing something, onboarding onto an area, or \"where should this live\". Use why for the motivation behind it."
disable-model-invocation: true
---

# How

**Job:** answer "how does X work" with an explanation a senior iOS engineer could start working from.

**Not my job:** why the code is shaped this way (`/why`) · changing code · reviewing a diff (`/interrogate`) · teaching at a person's pace (`/teach`).

**When there is nothing to report:** "X is not in this codebase", with the searches that came up empty (symbols, file globs, targets) and the nearest thing that does exist.

Explore the code to answer a "how does X work" question. Aim at an engineer onboarding onto a subsystem. Give enough for a working mental model, not so much that it reads like annotated source.

Model per role. `opus` for the explainer, `sonnet` for explorers. Use `general-purpose` agents, not `Explore`. `Explore` reads excerpts, and an explanation needs whole implementations read. When `.claude/ios.env` sets `MODEL_JUDGMENT` or `MODEL_CODE`, that value wins for its role. If the Agent tool rejects a model, use the default and say so.

## 1. Assess complexity

If the scope is ambiguous, state your reading and explore. The person can redirect.

- **Simple.** One type, one view, one small utility, a narrow question such as "how does `TaskStore.save()` work". No explorers. One explainer explores and explains in one pass. Go to step 2b.
- **Complex.** A subsystem across many files, targets or packages, a flow that crosses actors or processes (app, widget, extension, a background task), a full architectural overview. Spawn explorers first, then the explainer. Go to step 2a.

When in doubt, take the simple path.

## 2a. Explore (complex questions only)

Split the question into 2 to 4 angles, each a distinct slice of the subsystem. Good iOS slices are the entry point (a scene, an App Intent, a notification, a deep link), the state owner (the `@Observable` model, the store, the actor), persistence and sync (Core Data, SwiftData, CloudKit, files), and the view tree. Spawn every explorer in one message.

- `subagent_type`: `general-purpose`, told to read only and write nothing
- `model`: `sonnet`

Each explorer gets `references/explorer-prompt.md` with its angle filled in. Then go to step 3.

## 2b. Explain directly (simple questions)

Spawn one subagent that explores and explains in one pass.

- `subagent_type`: `general-purpose`, told to read only and write nothing
- `model`: `opus`

Build its prompt from `references/explainer-prompt.md`, without the explorer-findings section. Go to step 4.

## 3. Synthesize (complex questions only)

When every explorer has returned, spawn one subagent to merge their findings into one explanation.

- `subagent_type`: `general-purpose`, told to read only and write nothing
- `model`: `opus`

Build its prompt from `references/explainer-prompt.md` with every explorer's findings filled in.

## 4. Present

Present the explainer's output. Light edits for clarity, or context from the conversation, are fine. Do not rewrite it.

## Output

The sections in `references/explainer-prompt.md`, dropping any that do not apply: Overview, Key concepts, How it works, Where things live, Gotchas.
