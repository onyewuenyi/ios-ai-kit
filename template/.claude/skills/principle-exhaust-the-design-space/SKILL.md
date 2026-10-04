---
name: principle-exhaust-the-design-space
description: "Apply when facing a novel interaction or architectural decision with no precedent in the app. Build 2-3 competing prototypes (SwiftUI previews, variants in worktrees, simulator captures side by side with sim.sh compare) and compare them before committing."
disable-model-invocation: true
---

# Exhaust the Design Space

When a novel interaction or architectural decision has no established precedent, explore several concrete alternatives before implementation. Building the wrong thing costs more than exploring three options.

**The rule.** When the right answer is not obvious, build 2-3 competing prototypes or sketches. Compare them side by side. Only then commit. Design it twice is this rule by another name. A second flavor of the first shape does not count.

**How on iOS:**
- For UI, build each variant behind a `#Preview` or a launch seam, capture each on the simulator in the same state, and put them in one image with `scripts/ai/sim.sh compare`. Feel lives in motion, so record the gesture (`sim.sh record`, then `sim.sh frames`) when the choice is about a transition.
- For architecture, sketch each option as Swift types and signatures, then walk the dominant paths through each. The `/arena` skill runs N attempts in separate worktrees when sketches are not enough.
- The `prototype` playbook in `ios-loop` holds the procedure. If running the variants would settle the question, run them before asking anyone.

**When it applies:**
- Novel UI interactions (no prior art in the app or in the platform's own apps)
- Architectural choices with multiple viable approaches
- Product design decisions where the experience depends on feel, not logic

**When it doesn't:**
- Mechanical implementation where the pattern is established
- Bug fixes or refactors with a clear target state
- Changes where constraints dictate a single viable approach
