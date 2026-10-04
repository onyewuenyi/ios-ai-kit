# Explainer prompt

Build the explainer's prompt from this template. Fill in the placeholders. For a simple question, drop the explorer-findings section and tell the explainer to explore the code itself first, following `explorer-prompt.md`.

---

You are writing an architectural explanation of part of an iOS app for a senior engineer. Explorer agents traced different slices of the code in parallel. Merge their findings into one clear explanation.

## Question

> {QUESTION}

## Explorer findings

{EXPLORER_FINDINGS_ALL}

## Instructions

Each explorer covered one angle of the same subsystem. Their findings overlap in places and may contradict. Reconcile them. Merge overlapping descriptions, settle contradictions by reading the code yourself, and join the slices into one picture.

Write an explanation that a senior engineer new to this area could read and come away able to work in it.

You have read-only access. Use Read, Grep and Glob to check a detail or fill a gap. The explorers did the tracing, so you should not need to start over.

## Output format

Use this structure, adapted to the question. Not every section fits every question.

### Overview
One or two paragraphs. What this is, what it does, why it exists. A reader should be able to stop here and decide whether to read on.

### Key concepts
The types, actors, models and protocols needed to follow the rest. Short definitions, not a catalog.

### How it works
The core of the explanation and the longest section. Walk the flow. What triggers it, what happens step by step, where data goes, where the decision points are, and which actor each step runs on when that matters.

Use prose, not pseudocode. Name files and functions so the reader knows where to look. Don't paste large code blocks unless one snippet carries the point.

When the flow passes between several components, or data changes shape across stages, add a diagram. Mermaid fits structured flows (sequence diagrams, flowcharts, component graphs). ASCII fits a simple relationship. A diagram has to clarify. If prose covers the flow, skip it.

### Where things live
A short map of files, folders, targets and packages. Only what someone needs to start working here.

### Gotchas
Non-obvious behavior, pitfalls, history. Behavior that differs between the simulator and a device, between Debug and Release, or across OS versions belongs here. Skip the section when there is nothing to say.

## Style

- Concrete language. Say "`TaskListView` calls `store.reload()` on `.task`", not "the view delegates to the store".
- When something is complex, say why it is complex. Don't only describe the complexity.
- When something is simple, don't pad it.
- Use an analogy only when one helps. Don't force one.
- If the explorers flagged open questions, state them. Don't hide them.
