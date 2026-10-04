---
name: blast-radius
description: Find what an iOS change could break somewhere else before it ships, beyond the diff and beyond what grep shows, starting from scripts/ai/blast-radius.py's map of reachable surfaces, and prove the one fact it is safe because of by running real code. Use for "blast radius of X", "what could this break", or reviewing a small diff you do not trust.
argument-hint: "[--diff \"<git diff args>\"] [paths]"
disable-model-invocation: true
---

# Blast radius

**Job:** find what a change breaks somewhere else, and prove the one fact it is safe because of by running real code, not by writing it up.

**Not my job:** listing callers (grep does that in a second) · fixing what it finds (that is the bug-fix playbook) · an adversarial review across classes of failure (`/interrogate`).

**When there is nothing to report:** "Safe because <the one fact>", the step it was proven to, the proof, and the surfaces checked.

Companion to the **how** and **why** skills. `how` tells you what the code does. `why` tells you why it is shaped that way. Blast radius tells you what it breaks somewhere else. The job is the breakage grep will not show you.

## Don't trust your own writeup

A blast-radius writeup that sounds right is worthless. It reads as convincing whether or not it is true. So do not hand back the writeup alone. Find the one or two facts the whole thing depends on and prove them by running code.

### How sure are you

For each fact the change's safety depends on, get it as far down this list as is cheap, and say where it stopped.

1. You said so. Worthless on its own.
2. You pointed at the line. A real `file:line`, or the framework's own documentation or header.
3. You showed the bad case cannot happen. You walked the failure step by step and it does not reach.
4. You ran it. A test that calls the real code and fails loud if you are wrong.
5. You reproduced it in the running app, on the simulator or a device.

Step 4 is usually one small Swift Testing `@Test` that calls the exact function you are worried about, run with `scripts/ai/test.sh -only-testing:<Target>/<Suite>/<test>()`. Step 5 is a launch seam or deep link through `scripts/ai/sim.sh launch` or `scripts/ai/sim.sh openurl`, with a screenshot you looked at.

## Steps

1. **Map the reach.** `python3 scripts/ai/blast-radius.py` (uncommitted work), or `python3 scripts/ai/blast-radius.py --diff "main...HEAD"` for a branch, plus paths to limit it to your files when the checkout carries other work. It lists the types and declarations each changed line touches, every other file that names them, and the screens in `.claude/ios-screens.txt` they reach. That is the floor of the search, not the answer.
2. **Read the change.** The diff, the symbols it adds, changes and deletes, and what it now does differently, including the part the diff does not spell out (a new default argument, a changed `Equatable`, an `@Observable` property now read in `body`). Use the **why** skill to pull the PR and commits.
3. **Find the one fact it is safe because of.** Most changes that look risky are safe because of a single fact, like "this fetch only runs on the store's private context and nothing else reads its results". Find that fact. If it holds, most risky cases clear at once. Spend your time here, not on a long list of maybes.
4. **Look where grep stops.**
   - The framework's behavior at your pinned SDK: read the header and documentation for the API you call, and the Swift package's resolved version in `Package.resolved`.
   - When things run: actor hops and `await` suspension points, `onAppear` vs. `task`, view identity changes that reset `@State`, `scenePhase` transitions, a Core Data merge arriving on another context.
   - What a symbol search misses: a `Codable` key on the wire or on disk, a Core Data attribute name in the model file, a CloudKit record field, a `UserDefaults` key, an App Group container a widget or extension reads, a URL scheme or Universal Link path, a String Catalog key, an App Intent parameter Shortcuts users have saved, a launch argument, code three hops downstream.
5. **Be honest about each risk.** Give it a real chance of happening and a real cost if it does. Keep the risks you confirmed. List the ones you checked and cleared separately. Cite a real `file:line`. A search that finds nothing is still an answer. Never make up a caller or an API.
6. **Prove the one fact.** Write a test or a seam run that exercises the real code, run it, and paste what happened.
7. **For a big or wide change, run it as an arena.** Ask several Claude models the same question through `/arena` and merge the answers. Different models catch different real bugs.

## What to hand back

- **What it does.** What changed, including the part that is not obvious.
- **The one fact it is safe because of.** State it, say which step you got it to, and show the proof. If you could not prove it, write unproven.
- **Risks.** Each names how it breaks, the `file:line`, how likely and how bad, and how to check. Paste the proof for the ones that matter.
- **Cleared.** What you checked and why it is fine.
- **Surfaces.** The screens `blast-radius.py` listed, for `/verify` to capture.
- **Before you merge.** The cheapest test or repro that catches the real bug, including the one you wrote.

Write it through the **unslop** skill, cite real code, and strip anything private before it goes anywhere public.

**Reply:** the writeup above, with the one safety fact either proven or marked unproven.
