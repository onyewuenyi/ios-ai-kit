---
name: architect
description: Sketch Swift types, signatures and module boundaries before code, design it twice with Claude model runners, then implement against the chosen sketch and scrap it when implementation proves it wrong. Use for /architect, "architect this", "design this", or non-trivial iOS work where jumping to code would lock in the wrong shape (a new store, a sync boundary, a model layer, a feature crossing modules).
argument-hint: "[the design task] [with checkpoint]"
disable-model-invocation: true
---

# Architect

**Job:** decide the shape of new code (types, signatures, owners, module boundaries) before it is written, from at least two structurally distinct candidates, and keep the implementation honest to that shape.

**Not my job:** one-file edits whose shape is already obvious · picking a library or a config by benchmark (`/benchmark-checklist`) · reviewing a finished diff (`/interrogate`) · a design fork a screenshot settles (the prototype playbook in `ios-loop`).

**When there is nothing to report:** "The shape is forced", with the one constraint that forces it and the sketch, then go straight to Phase D.

Design before implementing. Sketch Swift types, protocol and function signatures, and module boundaries, with `fatalError("not implemented")` bodies and `// TODO:` pseudocode. Synthesize across several Claude model runners. Fill in code against the chosen sketch. If implementation proves the sketch wrong, throw it out and redesign.

## Start

Open a todo list with one entry per phase before starting.

1. Ground
2. Sketch
3. Agree
4. Implement
5. Scrap

## Phase A: Ground the problem

Build a real mental model of every system the new code touches. Run the **how** skill over the relevant subsystems: the views, the `@Observable` models, the stores and contexts, the actors, the app and scene lifecycle hooks the change will sit beside.

Naming a file is not grounding. Produce the traced model `how` prescribes. If the design redefines ownership or layering (who writes a Core Data context, which actor owns a cache, where a SwiftUI view gets its state), also run the **why** skill on the existing shape so the rationale becomes a constraint, not a guess.

Skip Phase A only when the work is greenfield with no surrounding system to integrate.

## Phase B: Sketch

Run the **arena** skill with the design-sketch task and the Phase A grounding. Pass [`references/runner-prompt.md`](references/runner-prompt.md) as each runner's prompt. Each candidate produces a design package shaped per [`references/rationale-template.md`](references/rationale-template.md).

**Runners.** Claude models through the Agent tool's `model` parameter, one runner each on `opus`, `sonnet` and `fable` by default. `.claude/ios.env` may override a seat with `MODEL_JUDGMENT` (the `opus` seat) or `MODEL_CODE` (the `sonnet` seat). If the Agent tool rejects a model, run that seat on `opus` and say so. A runner writes a sketch, not an app, so it needs no simulator. It still gets its own worktree (`scripts/ai/worktree.sh new arch-<slug>-<n>`) when the sketch is files in the repo, so two runners never write the same path.

**Design it twice.** Require at least two structurally distinct candidates before synthesis, even when the first looks sufficient. This is `principle-exhaust-the-design-space` made concrete. Whole-shape alternatives, not point fixes inside one shape. "An actor owns the cache" and "the cache is a value the store returns" are two shapes. "An actor with a dictionary" and "an actor with an `NSCache`" are one.

**Screen every candidate** against [`references/design-red-flags.md`](references/design-red-flags.md) before synthesis. Assume the next contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Prefer the design where a change that looks right from one file is right for the whole app.

**Compare viable candidates on interface depth.** Prefer the design that hides more complexity behind a smaller, simpler public surface. A rich interface can keep call chains short by concentrating capability instead of scattering it across layers.

Arena returns one synthesized design package. Its synthesis decision fills the rationale's "Synthesis decision" section.

## Phase C: Agree (opt in)

Default: proceed to implementation with the synthesized design. No human checkpoint.

Opt in when the invoker asks: "/architect with checkpoint", "stop and show me before implementing", or similar. Then surface the synthesized design and pause for sign-off with `AskUserQuestion`.

The synthesis can ship as its own commit either way, the "scaffold first" mode of `principle-foundational-thinking`. Stubs must still compile. `scripts/ai/build.sh` passes on the scaffold commit, with `fatalError` bodies that no test or launch path reaches. Planned and scoped breakage during fill-in is fine, per `principle-outcome-oriented-execution`. For adversarial pressure on the design before implementing, run `/interrogate` with the `design` lens on the scaffold.

If the human pushes back on the shape (at a checkpoint or after the fact), treat it as Phase A evidence. Re-ground and re-run Phase B before writing more code.

## Phase D: Implement against the sketch

Replace `fatalError("not implemented")` bodies with code, pseudocode with logic. The synthesized sketch is the contract. Build and test through the `ios-loop` skill, one logical change per build.

Deviations from the sketch are signal worth surfacing, not friction to absorb silently. If a function needs a parameter the sketch did not anticipate, ask whether the sketch was wrong, the requirement was missed, or the implementation is overreaching.

## Phase E: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch cannot absorb, throw the sketch out. Do not bolt fixes onto a wrong design, per `principle-redesign-from-first-principles` and `principle-fix-root-causes`.

The signal is a pattern, not single instances. Tells:

- The same shape of workaround appearing across unrelated code.
- Several unrelated edge cases that each need a special-case branch.
- Types that need escape hatches to compile: `as!`, `Any`, `AnyView` to unify branches, `@unchecked Sendable`, `nonisolated(unsafe)`, optionals that are always set in practice.
- The "we need a lock" reflex (a `Mutex`, a serial queue, `MainActor.assumeIsolated`) when the sketch said the state was not shared.
- Callers that must know the abstraction's internal rules to use it (call `prepare()` before `load()`, save on the right context).
- Two or more independent Phase D deviations of the same shape.

Use judgment. A few edge cases do not condemn an architecture. Some problems are complex. Complexity in the data is not complexity in the design.

When you scrap:

1. Re-run the **how** skill over what has been built.
2. Redesign as if the new constraints had been day-one assumptions, per `principle-redesign-from-first-principles`.
3. Subtract before adding, per `principle-subtract-before-you-add`. The new sketch is smaller than the old one before it grows.
4. Return to Phase B and re-run arena.

## Outputs

The caller's usage is written first, and the type sketch is derived from it. One Swift file with new types and signatures for small changes. A module map (which target, package or folder owns what, and what each exposes) plus type definitions for larger work. The rationale ships alongside, shaped per `references/rationale-template.md`, including the usage sketch and the synthesis decision.

**Reply:** the chosen shape in three lines, the candidates and why the base won, the red flags each candidate tripped, the rationale's path, and the first implementation step (or the Phase E verdict and what changed).
