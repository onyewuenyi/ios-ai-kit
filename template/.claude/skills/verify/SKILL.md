---
name: verify
description: Run the full definition-of-done gate for this iOS repo (format, build with no new warnings, tests, Release-safety of launch arguments, blast radius, and the visual matrix judged by an AI judge, or by eye) and write the PR-ready report. Use for /verify, "run the gate", "is this ready to merge", before opening a PR, and on every branch a cloud session produced.
disable-model-invocation: true
argument-hint: "[--no-visual] [--no-tests] [--release] [screen names…]"
---

# Verify

**Job:** run every gate on the working tree and write the PR-ready report, with every visual sheet judged.

**Not my job:** merging · pushing to the default branch · fixing beyond three attempts per gate · calling a skipped gate passed · judging a sheet nobody looked at.

**When there is nothing to report:** the gate table, all PASS, and the "Not verified here" list.

1. Run `scripts/ai/verify.sh $ARGUMENTS`. It runs every gate even after a failure and writes `.build/verify/report.md`.
2. For each failed gate, read `.build/verify/<gate>.txt`.
   - **Fix it** if it is in this change's scope, and re-run.
   - **Report it** if it is not, and don't hide it.
   - **Cap: three fix attempts per gate,** then report what is left.
   - Never weaken, skip or delete a test to get a pass.
3. **Visual (gate 6).** `verify.sh` captures each screen at default, dark and the largest text size, then `scripts/ai/judge.py` asks a separate Claude call to judge every sheet against the intended change (`VERIFY_INTENT`, else the branch's commit subjects) and the app's conventions in `.claude/judge-notes.md`. The script checks the answer and records it, so the gate prints PASS or FAIL with one line of evidence per screen.
   - A **FAIL** is work: read the evidence, open the sheet yourself, fix the root cause, re-run. If the judge is wrong about a deliberate design, add one line to `.claude/judge-notes.md` saying what is intended; a note never excuses a real defect.
   - The gate stays **JUDGE** when no verdict came back (no `claude` on PATH, an invalid answer) or `VISUAL_JUDGE=human`. Then judge by eye: spawn the `ui-verify` agent with the `JUDGE` sheet paths plus the screens `reach` (gate 5) named, and look for clipped primary text, overlap, controls off-screen or under the keyboard, dark-mode contrast and blank states.
   - Where the change touched an interaction and Xcode is open, ui-verify also drives it with device interaction and asserts the resulting UI hierarchy.
4. **Record a human verdict** only when the gate still reads `JUDGE`: `python3 scripts/ai/history.py judge PASS "<one line per screen>"` (or `judge FAIL "<what is wrong>"`). Only a judged pass counts as verified for `pr.sh`, `merge.sh`, the lead and the status line. Never judge sheets you did not open.
5. **Reply with:**
   - the gate table from `report.md`;
   - the visual verdict per screen, with sheet paths;
   - a filled-in **Not verified here** list (device-only behavior, anything a gate skipped).

   That text is the PR description's verification section.
6. **Propose it.** When every gate passed (or each failure was accepted) and the work is committed, run `scripts/ai/pr.sh`: it opens the PR with this report as its body, or updates the open one. Never push to the default branch and never merge; the owner does.

A change is done only when every gate passes, or each failure is explained and accepted by the person asking.
