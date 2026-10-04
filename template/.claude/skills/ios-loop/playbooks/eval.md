# Eval, an A/B run of a skill or prompt change

**You own the experiment design. Plan, blind, run, read, synthesize.** Use it for a change to a skill, a playbook, an agent, a CLAUDE.md line or a prompt the app sends a model, whenever the question is "does the variant make the agent behave better".

**Blinding is non-negotiable.**

- No `eval`, `judge`, `experiment`, `rubric`, `score`, `compare`, `benchmark`, `candidate` or `arena` in any directory, branch, file or prompt you add where the candidate can see it. The repo's own test targets are organic and stay.
- The candidate prompt reads like an organic request. State the goal, never the meta.
- No chain-eliciting cues. Do not ask the candidate which skills, principles or files it used. Grade that from its transcript and the shape of its diff.
- Sanitize directory, worktree and branch names. Use names a person working on this app would pick.
- Do not tell a candidate that other candidates exist.
- The judge may know it is judging. It sees outputs by sanitized label only, never by model name or arm name.
- Two variants are scored by one judge in a single pass on one scale, blind to which arm each output came from.

## Steps

1. **Frame.** Name the variant under test (the diff, by path and commit) and the behavior that counts as success. Write the rubric, three to six concrete criteria, in a file outside every candidate directory. Pick the engine.
   - `claude plugin eval` when the change ships in a plugin with an eval suite (`evals/**/case.yaml`, or `prompt.md` plus `graders/*.md`). It runs each case, scores it with graders, and by default adds a no-plugin baseline arm.
   - Headless `claude -p` runs for everything else, such as a project skill in `.claude/skills/`, a playbook, an agent or a CLAUDE.md line, run once with the baseline and once with the variant.

   **Check.** The rubric file exists, names three to six criteria, and no candidate can reach its path.
2. **Set up sanitized environments.** One checkout per arm. `scripts/ai/worktree.sh new <neutral-name> origin/main` for the baseline, and the same for the variant with the change applied. Each worktree gets its own simulator and DerivedData, so iOS candidates can build and run. Plant the context an organic task would have, such as a seeded store, a failing test or an open issue. **Check.** `git -C <worktree> diff origin/main --stat` shows only the variant (or nothing for the baseline), and a word grep over every name you created finds none of the banned words.
3. **Author one organic prompt.** What the owner would type into a session. The same prompt goes to every candidate. **Check.** Read it as the candidate would and find no hint of what is measured.
4. **Run the candidates.** At least five runs per arm (principle-explain-the-number). Run them in the background, and mix Claude models through `--model` only when the model is part of the question.
   - Plugin engine. `claude plugin eval <plugin dir> --json <out>.json --judge-model opus -j <n>`, at the baseline checkout and again at the variant checkout when the question is old versus new. `--ablation with-without` (the default) answers plugin versus no plugin. `--case <glob>` narrows to the cases the change touches. `--max-cost-usd` caps spend when asked.
   - Headless engine. In each worktree, `claude -p "<prompt>" --model <model> --output-format stream-json --verbose > <out>/<label>-<k>.jsonl`. The model defaults to `MODEL_CODE` from `.claude/ios.env`.

   **Check.** Every run ended with a result. A run that errored or hit its turn limit is reported as no result, never as a failure of the variant.
5. **Judge blind.** One judge subagent (Agent tool, `model: opus`, or `MODEL_JUDGMENT`), on a different model from the candidates where the candidates ran on one model. It gets the rubric and the outputs under shuffled labels (`A1` to `A10`) and scores every output on one scale in one pass. In the plugin engine the graders are the first judge. Run this judge over the same outputs anyway when the change is a judgment call the graders cannot see. **Check.** The judge prompt contains no model name and no arm name.
6. **Verify the chain from transcripts, not self-report.** Each candidate's transcript is its `stream-json` file, or `~/.claude/projects/<its worktree path with every non-alphanumeric as ->/*.jsonl`. Read only those directories. Never glob across `~/.claude/projects/*`, which reads private sessions from unrelated projects. Parse them the way `scripts/ai/friction.py` does. Record which skills loaded, which files it read, which `scripts/ai/` commands it ran, and whether it ran `/verify` before claiming done. For iOS work, a candidate's claim that the app works counts only with its gate table (`python3 scripts/ai/history.py last <sha>` in its worktree) or a screenshot you opened. **Check.** Each candidate row in the table cites transcript evidence for every chain criterion.
7. **Read every output yourself,** end to end. Compare your reading with the judge's verdict. A disagreement means a biased judge or an ambiguous rubric, so name which and fix the rubric before any rerun. **Check.** Every case has your note beside the judge's score.
8. **Synthesize per case.** One row per case. Case, baseline result, variant result, the judge's score for each, your note. Report the median and the worst case per arm, not just a mean. A difference inside run-to-run spread is no difference. **Check.** The recommendation follows from the rows, and a case where the variant lost is named, not averaged away.

Clean up the worktrees with `scripts/ai/worktree.sh remove <path>` when the report is written.

**Reply:** the variant under test, the engine, the rubric, the per-case table, the judge's verdict, where you disagreed with it and why, the chain evidence from transcripts, and whether to promote the variant.
