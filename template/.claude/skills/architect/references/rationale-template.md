# Rationale template

The prose that ships alongside the type sketch. One page. Sentence-case headings, no boilerplate. Replace the italic notes with content.

## Problem

*One paragraph. What we are trying to do, and what about the existing app or its constraints makes the shape non-obvious. If [Phase A](../SKILL.md#phase-a-ground-the-problem) surfaced constraints the design must honor (types to interoperate with, callers we cannot break, a Core Data model version that is frozen, an actor boundary, a CloudKit schema already deployed), name them so the reader sees the constraints you saw.*

## Usage (caller's view)

*Write this first, before the type sketch. Show the short README a consumer reads, plus two or three realistic call sites in their code: a SwiftUI view, a test, an App Intent, whatever calls it. What they import, what they call, what comes back, on which actor. The type sketch in [Shape](#shape) is derived from this. The two must agree. When they diverge, reconcile the sketch to the usage, not the reverse. The caller's experience is the spec. The types serve it.*

## Shape

*The recommended architecture. Data structures first: the value types, enums with payloads, the one owner of each piece of state. Then how data flows through the signatures, and which actor each call runs on. Name the load-bearing decisions. State which invariants are encoded in types, where validation lives, and what the system deliberately does not do. Judge interface depth explicitly. State what complexity the public surface hides, what stays exposed to callers, and why the interface is no larger than needed. Cite the principle behind each decision (for example, "per `principle-boundary-discipline`"). Do not restate it.*

## Synthesis decision

*Filled in by the **arena** skill. Which candidate became the base and why, what was adapted from each of the others, and what was rejected and why.*

## Tradeoffs accepted

*One bullet per tradeoff the chosen shape makes. Form: "we accept X in exchange for Y." Name anything a future reader might mistake for an oversight, including what looks like premature optimization or premature simplification.*

## Alternatives considered

*Required. Name at least one concrete alternative shape, with one line on why it lost. Judge each on interface depth, not implementation simplicity alone. Name the complexity it exposes to callers and the complexity it hides. Two or three alternatives belong here when the design space had real contenders. One is fine when the constraints forced the answer, phrased as "this was the only viable shape because ...". Do not list flavors of one shape. This section covers design alternatives, not the other runners' candidates.*

## Open questions and risks

*What the human needs to weigh in on, and risks worth flagging before implementation starts (a migration, a sync conflict, an App Review question, something only a device can prove). Phrase each as a question, so the human's answer is the resolution.*

## Next implementation step

*The first thing to build against the sketch. One sentence. What you would start writing right after synthesis, or after sign-off if a checkpoint was opted into.*
