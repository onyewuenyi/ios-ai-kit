# Investigation (scout)

**You own the answer. Plan, route, write.**

A read-only question. How does X work, why does Y behave this way, is Z safe to change, should we do X or Y, are we sure. The deliverable is a cited report or a recommendation, not a change. A report may recommend implementation. It never authorizes it.

1. **State the question and the decision it serves,** one sentence each. If the answer would not change a decision, say so and stop. **Check.** Both sentences are in the todo list.
2. **Route through `/how`** over the subsystem the question names. For a motivation question ("why was this built this way"), also route through `/why`. Write the throughput checkpoint as one line, `throughput checkpoint: n/a, read-only investigation`. **Check.** The routed skill's output is in hand.
3. **Gather evidence, cheapest first.** The code (callers, types, tests), the history (`git log -S`, `git log -L`, `git blame`), the project's docs and decision records, then the running app (a seam through `scripts/ai/sim.sh launch`, a log, a measured number) when behavior is the question. Delegate wide sweeps to an `Explore` agent and keep only its conclusions (principle-guard-the-context-window). **Check.** Every part of the question has at least one piece of evidence, or is listed as unknown.
4. **Label every claim** measured, read in code (with file:line), or inferred. A prediction or an unseen cause is a guess, and says so. Where the code and the docs disagree, the running app decides. Never hand the reader a check you could have run. **Check.** No unlabeled claim remains.
5. **Write the report** to `.build/reports/<yyyy-mm-dd>-<slug>.md` (gitignored unless the owner wants it kept). Use the `/how` shape (Overview, Key Concepts, How It Works, Where Things Live, Gotchas). For a decision between alternatives, write a recommendation with a tradeoffs table instead. Either way it carries:
   - the question and the one-paragraph answer
   - the evidence, each item with its label and location
   - what is still unknown and the check that would settle it
   - options with a recommendation, if a decision is pending

   **Check.** The answer is in the first paragraph.
6. **Run `/unslop` on the reply.** **Check.** No long dash, no colon joining two clauses, one thought per sentence.
7. **Stop at the report.** No PR, no `/verify`, no `/architect`. If implementation follows, it starts as a new task in the matching playbook (Bug fix or Feature) from a clean base. Scratch edits and debug logging from the investigation do not ride along. A reproduced bug becomes that task's failing check. **Check.** `git status` shows no change from this investigation.

**Reply:** the answer first, then the report path, the strongest evidence, and the open unknowns. For "are we sure?", your real judgment with reasons. Push back when the premise is wrong.
