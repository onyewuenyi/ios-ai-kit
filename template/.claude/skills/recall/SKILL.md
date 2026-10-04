---
name: recall
description: "Rebuild your recent working context in this repo from its Claude Code transcripts, live git and gh state, and the shared record (issues, prior fixes, crash reports), then hand back a tight current-state brief. Use for 'recall my work on X', 'catch me up', 'what have I been working on', 'where did I leave off', before starting or resuming work."
disable-model-invocation: true
---

# Recall

**Job:** before work starts or resumes, rebuild the recent context of this repo and hand back a tight brief of where things stand and what to do next.

**Not my job:** resuming one specific session (the `session-pickup` playbook) · turning habits into a skill (`/automate-me`) · a readable summary of the work for someone else · reading another project's transcripts.

**When there is nothing to report:** "No sessions in this repo touched X in <window>", with the window and the search terms used, and the live state (`git status`, open PRs) in one line.

Keep it tight and on topic. Read only what the threads in scope need, then stop.

Context lives in two records. Your own sessions hold what you did and decided. The shared record holds everything that happened around the same code under other names: the bugs testers keep reporting, the fixes that shipped and were reverted, the crashes still firing in the field. `/why` searches that second record across source control, the issue tracker, docs, chat, crash reports and telemetry. A feature with a long bug tail keeps most of its story there, so don't rebuild it from transcripts alone.

Transcripts live at `~/.claude/projects/<repo path with every non-alphanumeric character as ->/<session>.jsonl`, with subagents under `<session>/subagents/`. Each line is one JSON event. `.claude/skills/recall/scripts/sessions.py` reads them for this repo and its worktrees only.

```bash
python3 .claude/skills/recall/scripts/sessions.py list --since 7d [--grep <topic>]   # newest first
python3 .claude/skills/recall/scripts/sessions.py digest <id> [--grep <topic>]         # one line per prompt and tool call
```

1. **Classify, then route.** One specific prior session to resume is the `session-pickup` playbook, not this. Turning habits into a durable skill is `/automate-me`. A human-readable summary of your work is a different task. Recall loads working context across recent sessions before you act. If the person already gave you a full state capsule (paths, branch, the change), use it and skip the mining.
2. **Lock the scope before searching.** Pin the window ("recent" is a real range, default the last 7 days), the topic if one is named, and the repo (this one by default, never another project's transcripts unless asked). State the scope back. Never quietly turn "all" into "the last N".
3. **Fan out across the sessions.** `sessions.py list` gives the candidates in real modification order. Never order by session id. Skip the current session and obvious noise (subagent runs, one-turn `claude -p` judge or eval runs, test sessions). For one or two sessions, read them directly with `digest`. For more, spawn parallel `general-purpose` subagents with `model: haiku` (or `MODEL_FAST` from `.claude/ios.env`), each taking a slice. Tell each to grep the topic first, read only the matching sessions and only their relevant regions, and return one block per session in the same schema: topic, the person's goal, decisions, open threads, struggles and corrections, artifacts (PRs, issues, branches, worktrees, simulators, screenshots), each citing the session id. The raw transcripts stay in the subagents. The main thread gets only their findings.
4. **Sweep the shared record** whenever the topic names a feature, file, screen, subsystem or bug. This is the default, not a judgment call, and "my work on X" does not exempt it. Hand it to `/why`'s investigators, but change their question from "why was this built this way" to "what is the current state, what was tried and didn't hold, and what are testers and users still reporting". Reuse its per-source playbooks, run its investigators in parallel with the session mining, and keep its posture: one investigator per source, a null result is a finding, an unreachable source is named as a gap. Skip this step only for pure activity recall with no named target ("what did I do this week"), where your sessions and the live state are the whole answer.
5. **Verify against live state.** Check every PR, branch and issue the mining and the sweep surfaced: `git status`, `git log`, `git worktree list`, `python3 scripts/ai/prs.py`, `gh pr view`, `gh issue view`. When the answer depends on what an agent actually did (the tools it ran, the files it read, the errors it hit), read the full transcript region, not a summary.
6. **Write the brief** to the contract below. Group by thread. Stay on the named topic.

## Output contract

Lead with the capsule, then the threads, then the problems, then the next move. Deeper detail goes below or gets cut.

- **Capsule.** At most 5 bullets. What this work is and where it stands overall.
- **Threads.** One line each, with exactly one status tag: `[merged #N]`, `[open PR #N]`, `[in flight <branch>]`, `[verified, uncommitted]`, `[reverted #N]`, or `[planned, not started]`. An untagged thread is not done. Tag it.
- **Problems.** At most 5, the recurring ones. Include the symptoms testers or users keep reporting and any fix that shipped and was reverted, so the next attempt starts where the last one failed.
- **Next move.** The single most useful next action, concrete.

An adjacent feature or issue stays out unless it blocks this one. When the capsule and threads outgrow a screen, cut detail before you cut threads. Write the brief through `/unslop`. Cite session findings by session id and shared-record findings by their source (PR #, issue #, crash group, chat permalink). Sanitize private context before anything goes outside the machine.

**Reply:** the brief, to the contract above.
