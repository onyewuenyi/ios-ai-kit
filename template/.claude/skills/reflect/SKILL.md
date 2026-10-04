---
name: reflect
description: Mine the current session for durable lessons (a correction, a trap, a wrong assumption, a slow path, a skill that misfired) with three parallel reviewers, then route each to the strongest mechanism that would have prevented it. A type, a test, a hook, a script, an ios-screens line, a skill or playbook edit, an agent definition, or a project rule. Proposes, never applies without approval. Use for /reflect, "capture what we learned", or after a long or painful task.
disable-model-invocation: true
---

# Reflect

**Job:** turn this session's lessons into structure, so the next session cannot repeat them.

**Not my job:** applying anything the owner did not pick · writing rules into memory (memory is for facts about the owner and the work) · lessons that will not recur · what the repo already enforces · reading another project's transcripts.

**When there is nothing to report:** "Nothing durable to encode from this session", with the one candidate that came closest and why it was dropped.

Skip a trivial or off-topic session, and one where an existing skill was followed correctly. One-offs are not lessons.

## 1. Locate the transcript

Find this session's transcript before fanning out. It lives under this repo's directory only. Never glob across `~/.claude/projects/*/`. That reads private sessions from unrelated projects.

```bash
python3 .claude/skills/recall/scripts/sessions.py find "<the opening words of this session's first prompt>"
python3 .claude/skills/recall/scripts/sessions.py list --since 1d     # if find fails: newest first
```

Confirm the match by its first prompt. Subagent transcripts sit under `<session>/subagents/`. If no path resolves, write a tight digest of the session (the requests, the corrections, the dead ends, the tools and skills used) and pass that instead.

## 2. Collect your own candidates

From this conversation, list every moment where:
- the owner corrected you, or rejected an approach
- something you believed turned out false (an environment fault read as an app bug, a metric that lied, a stale install)
- a check caught a defect late that an earlier check could have caught
- you spent more than a few steps on something a script would do in one
- the owner handed you context you could have fetched yourself (an issue, a PR, a crash report, a chat thread, through `gh` or an MCP)
- a rule in CLAUDE.md, a skill or a playbook was missing, wrong, ignored, or did not trigger when it should have
- a subagent (`ios-agent`, `ui-verify`, `build-verify`, `review-lens`, `comment-sicko`) returned something wrong or wasteful
- a line in `.claude/ios-screens.txt` turned out stale (re-date its `#seen:` or retire it)

Drop one-offs. A lesson must plausibly recur. Drop what the repo already enforces. For a short session with one or two clear candidates, skip to step 5 and route them yourself.

## 3. Spawn three reviewers in parallel

One message, three Agent calls, `subagent_type: general-purpose`, so each inherits the session's MCP tools for looking up what the transcript cites. Each is told to write nothing.

| Lens | `model` | Prompt |
|---|---|---|
| Judgment | `opus` | `references/judgment-reviewer.md` |
| Tooling | `sonnet` | `references/tooling-reviewer.md` |
| Divergent | `opus` | `references/divergent-reviewer.md` |

The tooling lens runs on a different model on purpose. A second opinion is the same question against a different model, and agreement across models is high signal. When `.claude/ios.env` sets `MODEL_JUDGMENT` or `MODEL_CODE`, that value wins for its role.

Pass each template verbatim, with the transcript path or the digest filled in. Reviewers return findings in their reply.

## 4. Synthesize

One Agent call, `subagent_type: general-purpose`, `model: opus`, with `references/synthesizer.md` verbatim and each reviewer's full output inlined where marked, plus your own list from step 2 as a fourth input. It returns Accepted, Rejected and Backlog, each Accepted row routed to a rung of the ladder below.

## 5. Route each lesson to the strongest rung

The ladder is the **Encode lessons in structure** principle (`principle-encode-lessons-in-structure`). Check every Accepted row. When a stronger rung fits than the one proposed, move it up.

| Rung | Mechanism | Lands in |
|---|---|---|
| 1 | Type or API shape | the app's source |
| 2 | Test (including a grep test for an absence) | the app's test target |
| 3 | Hook | `.claude/settings.json` (this app), or ios-ai-kit's `template/.claude/hooks/guard.py` if it applies to every iOS project |
| 4 | Script or doctor check | ios-ai-kit's `template/scripts/ai/` (with a case in its `tests/`) |
| 5 | Screen line, playbook step or skill edit | `.claude/ios-screens.txt` (an `expect:` or `absent:` that would have caught it, dated `#seen:<date>`), an ios-ai-kit playbook in `ios-loop/playbooks/`, or the body of the skill that misfired |
| 5b | Skill description | the `description:` of a skill that should have triggered and did not |
| 5c | Agent definition | the agent that made the mistake (ios-ai-kit's `template/.claude/agents/`, or the project's own). Sharpen its job and anti-jobs. |
| 6 | Rule text | the project's CLAUDE.md or `.claude/rules/` (and its long-form doc if the project keeps one) |
| 7 | Memory | only facts about the owner or the work, never rules |

Decide app or kit. A lesson true of any iOS app goes to ios-ai-kit, because installed kit files here are overwritten on upgrade and a kit fix made only in this repo is lost. A lesson true of this app only goes to the project.

**Backlog** holds a mechanism worth building that is too large for this session (a new script with tests, a new hook, a type change across the app). It is filed as a GitHub issue after approval, in the repo it belongs to.

## 6. Propose

Present the table. Lesson (one sentence, with the moment it happened), rung, exact target file, the proposed edit (a diff for text, a sketch for a test or a hook). Then the Rejected list with reasons, then the Backlog. Wait for the owner to pick. Rules and skill edits change every future session, so nothing is applied without approval.

## 7. Apply

Apply the approved rows on a branch.

- A one-line edit to a skill, playbook, rule or agent. Make it directly.
- A substantive skill edit (a new section, more than about 10 lines), a description tuned so a skill triggers, or a new skill. Follow the `authoring-a-skill` playbook.
- A new test or hook. Run it once to prove it fires on the failure and passes on the fix.
- A structural fix that replaces prose. Delete the prose.
- A kit change. Run the kit's own check (`python3 tests/standard.py` in the ios-ai-kit repo) before committing.
- A Backlog row. File it with `gh issue create`, in the repo it belongs to.

Commit, then `scripts/ai/pr.sh`. Kit changes go to the ios-ai-kit repo as their own PR.

## 8. Summarize

Short list, no preamble.

- Applied. `<path>`, what changed, one line each.
- New skills or agents. `<path>`, one line each (rare).
- Backlog filed. `<issue URL>`, one line each.
- Dropped. One line per rejected finding, with the reason.
