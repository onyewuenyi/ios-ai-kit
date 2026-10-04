# Steer with principle names

The kit ships its principles as individual skills, one rule each, at `.claude/skills/principle-<name>/SKILL.md`. `/ios-loop` reads their index at the start of every multi-step task, applies the ones the task triggers, and names each applied principle in its reply along with the decision it changed.

You don't invoke principles. You use their names to steer. Each name points at a complete rule the agent has already read, so one phrase redirects the work more precisely than a paragraph of instructions.

## Steering in practice

Say the agent is about to add a fourth `TaskRow` variant next to three that are barely used.

```text
use subtract before you add. delete the dead row variants first, then design what's left.
```

Say it claims success because the build passed.

```text
apply prove it works. launch the seam, open the edited task, and show me the sheet at AX5.
```

Say two parallel attempts are about to share one simulator and one DerivedData.

```text
separate before serializing shared state. give each attempt its own worktree, no locks.
```

Say it is about to believe a crash on a simulator that has been up for three days.

```text
environment before code. run doctor.sh and sim.sh guard before you read that crash.
```

Each phrase lands because the rule behind it is specific. The agent still has to say, in its reply, which decision the rule changed. A principle citation with no decision behind it is the tell that it name-dropped instead of applying.

## The principles, briefly

The core principles decide how much to build and when to rethink the design.

- **Laziness Protocol** prefers deletion and the smallest change that solves the problem, over a new protocol, wrapper or flag threaded through every view.
- **Foundational Thinking** chooses the core Swift types, and which actor owns which state, before writing logic.
- **Redesign from First Principles** integrates a new requirement as if it had been there from day one.
- **Attack the Premise** questions the premise that two or more failed fixes shared, after a census of which actors hold the imbalance.
- **Subtract Before You Add** removes dead weight before building on top of it.
- **Minimize Reader Load** collapses layers and hidden state a reader must hold in their head.
- **Outcome-Oriented Execution** converges a rewrite on the target design instead of preserving throwaway compatibility states.
- **Experience First** chooses the user's result over implementation convenience, and fewer polished screens over more rough ones.
- **Exhaust the Design Space** builds two or three competing prototypes when there is no precedent, in previews or side by side on the simulator.
- **Build the Lever** builds the script, test or check that does or proves the work, so a reviewer can rerun it.

The architecture principles decide where state, validation and compatibility live.

- **Model the Domain** encodes repeated rules in one Swift type, not scattered conditionals across views.
- **Boundary Discipline** validates at the boundary (launch arguments, `Codable` decoding, Core Data and CloudKit records, `URLSession`) and trusts internal types.
- **Type System Discipline** makes illegal states unrepresentable, with enums carrying payloads instead of parallel optionals.
- **Make Operations Idempotent** converges retries, relaunches and a second share acceptance on the same end state.
- **Migrate Callers Then Delete Legacy APIs** migrates and deletes in one wave.
- **Separate Before Serializing Shared State** removes the sharing before adding a lock, an actor hop or a queue.

The verification principles define what counts as proof.

- **Prove It Works** verifies the real artifact, the app on the simulator or the built bundle, not a proxy.
- **Fix Root Causes** reproduces with a rate, reads the faulting thread, and fixes at the cause, not with a `guard let`, a retry or a delay.
- **Sequence Work into Verifiable Units** ends each small unit in a check before starting the next.
- **Test Behavior, Not Implementation** calls the code the way its users do and asserts a literal expected value, and deletes a test that would still pass if every function it calls returned a default.
- **Explain the Number** names what limits a measured number and rules out that it measured something else (a Debug build, a simulator, a warm cache) before anyone trusts or reports it.

The delegation principles keep parallel work sane.

- **Guard the Context Window** routes xcodebuild logs, crash reports, screenshots and bulk reading to subagents (`build-verify`, `Explore`, `ui-verify`) and keeps findings in the main session.
- **Never Block on the Human** proceeds on reversible work and presents the result, and parks a genuine product decision with a recommendation.

One meta principle sits over all of them.

- **Encode Lessons in Structure** turns advice you've repeated twice into a type, a test, a hook or a script.

The iOS principles cover the places where an app fails differently from other software.

- **Environment Before Code.** A broken simulator runtime, another session's build installed over yours, or a stale toolchain looks exactly like an app bug. Run `scripts/ai/doctor.sh` and `scripts/ai/sim.sh guard` first.
- **Extremes Are the Test.** Judge a UI change at the largest accessibility text size, the smallest iPhone, iPad, dark mode, Reduce Motion, VoiceOver, and the empty, one, many, error and offline states.
- **Release Is Another App.** Verify the artifact you ship with `scripts/ai/verify.sh --release`. Seams fenced out, the privacy manifest in the bundle, every usage string present.
- **Additive Data.** The person's data is never the experiment. A schema change is a new model version that is a superset of the last, and a destructive path backs up first.

Don't memorize the list. Skim it now, then come back when you catch the agent doing something a name here would have prevented. That's how the vocabulary sticks.

Next is [Make it yours](./09-make-it-yours.md).
