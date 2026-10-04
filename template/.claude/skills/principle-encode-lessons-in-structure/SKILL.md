---
name: principle-encode-lessons-in-structure
description: "Apply when you catch yourself writing the same instruction or warning a second time, or notice a recurring correction. Encode the rule in the strongest mechanism that fits (a type, a failing test, a hook in .claude/settings.json, a scripts/ai check, an ios-screens line) instead of more text. /correct and /reflect route the lesson."
disable-model-invocation: true
---

# Encode Lessons in Structure

Encode recurring fixes in mechanisms (types, tests, hooks, scripts, metadata) instead of textual instructions. Every error, human correction, and unexpected outcome is a learning signal. Capture it, route it, and close the loop.

**Why:** Textual instructions are easy to miss. They require the reader to notice, remember, and comply, and an agent in a fresh session remembers nothing. Structural mechanisms enforce the rule without cooperation.

**Pattern:**
When you catch yourself writing the same instruction a second time:
1. Ask whether it can be a type, a test, a hook, or a script.
2. If yes, encode it. Delete the instruction.
3. If no (it requires judgment), make the instruction more prominent and add an example of the failure mode.

**Pick the strongest mechanism.** When more than one would work, choose the strongest the situation allows, because agents copy whatever the surrounding code already does and a weaker guard becomes the next template. Strongest first:
1. A type that makes the wrong state unrepresentable, so it cannot compile (see `principle-type-system-discipline`).
2. A failing test in the app's test target, including a grep test for an absence (no launch-argument read outside `#if DEBUG`, no destination by simulator name in a script).
3. A hook in `.claude/settings.json` that blocks or asks (`PreToolUse`, `PostToolUse`, `Stop`).
4. A `scripts/ai/` script a playbook runs, or a gate inside `/verify`.
5. A canonical helper the codebase routes through.
6. A runtime check (`precondition`, an assertion in a DEBUG seam).
7. A line in `.claude/ios-screens.txt` or a playbook step.
8. A line in CLAUDE.md or a `.claude/rules/` file.

**Corollary:** If the fix is structural, only use the structural fix. The instruction is the symptom. Delete the prose a structural fix replaces.

**Feedback loop:**
- **Capture every correction.** When the human intervenes or a test fails, decide if it's a one-off or a pattern. `/correct` takes a correction the moment it happens. `/reflect` mines a whole session.
- **Route to the right layer.** A one-off goes in the reply or the PR description. A recurring fix becomes a test, a hook, a script, or a skill step. A systemic issue becomes a principle. Claude Code memory is for facts about the owner and the work, not for rules.
- **Close the loop.** Don't just record. Apply now or create a concrete todo.

**Anti-patterns:**
- Acknowledging without recording ("I'll keep that in mind" does not persist past the session).
- Recording without routing (a note about a test that should exist is wasted unless the test gets written).
- Fixing without generalizing (fixing one instance while leaving the recurring pattern intact).
