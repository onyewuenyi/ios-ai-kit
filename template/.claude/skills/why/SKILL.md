---
name: why
description: "Find the evidence for why code is the way it is: design rationale, why we picked Y, a regression's origin, a postmortem, a threshold or constant. Searches git history, gh PRs and issues, Claude Code sessions, and every MCP source this session has (docs, chat, crash reports, telemetry, analytics) in parallel, then returns a cited, confidence-tiered answer. Use how for runtime behavior."
disable-model-invocation: true
---

# Why

**Job:** answer "why is X this way" with cited evidence, each claim tiered by how well the record supports it.

**Not my job:** how the code works today (`/how`) · changing the code · confirming the hypothesis the person brought · filling a gap in the record with a plausible story.

**When there is nothing to report:** "No recorded rationale found", with every source searched, the queries run in each, and who would likely know.

Find the forces that gave code its shape. `/how` answers what the code does. `/why` answers what led to it.

Model per role. `sonnet` for investigators, `opus` for the synthesizer. When `.claude/ios.env` sets `MODEL_CODE` or `MODEL_JUDGMENT`, that value wins for its role. If the Agent tool rejects a model, use the default and say so.

## Posture

Work as a careful, cautious, precise investigator. Keep what you know apart from what you infer. `references/epistemics.md` holds the confidence tiers and the phrasing guide. The synthesizer must follow it.

## 1. Understand the target and the question

The **target** is a piece of code, a pattern, a feature, a constant, or a named design decision. The **question** is a design rationale, a trade-off, a motivating edge case, an external constraint (an App Review rejection, an OS bug, a framework limit), dead code, or a broad history sweep.

If the target is vague, take your best reading from the conversation (open files, recent edits, what was just discussed). State it in one line so the person can redirect, then go on.

## 2. Anchor in code

Before spawning investigators, pin the investigation to concrete code. Collect:

- the file paths and line ranges
- the key symbols (types, functions, constants, launch arguments, model entity names)
- the last few commits touching the target
- PR numbers from the commit subjects (the `(#1234)` pattern) and from `gh`

```bash
git blame -L <start>,<end> <file>
git log --follow -p -- <file>
git log --oneline -20 -- <file>
git log -1 --format=%B <commit>
gh pr list --state all --search "<commit sha>" --json number,title
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews
```

Some targets live outside Swift files. A Core Data change lives in a new `.xcdatamodel` version inside the `.xcdatamodeld`. A capability lives in the `.entitlements` file and `Info.plist`. A build setting lives in `project.pbxproj` or an `.xcconfig`. Anchor in whichever file holds the target.

This seed (paths, symbols, commits, PR numbers, linked issue numbers) goes to every investigator.

## 3. Spawn investigators in parallel (the default)

**Default to the full parallel investigation.**

### Discovery

List the evidence sources this session can reach. Git and `gh` are always there. MCP servers show up as tools named `mcp__<server>__<tool>`, either in your tool list or as deferred tools you load with ToolSearch. `claude mcp list` prints the configured servers.

Map each source to one evidence category.

1. Source control history
2. Issue tracker
3. Long-form documents
4. Team chat and email
5. Crash and error reports
6. Runtime and performance telemetry
7. Product analytics
8. Agent sessions

Classify each MCP by its name, its server instructions and its tool names. If one could fit two categories, pick the one that matches its main evidence and note the call in the coverage map.

Aim for a complete coverage map, not a minimal one. Document the null. Don't skip the search.

Launch every investigator in one message so they run together. One investigator per category. Never ask one agent to cover two.

Each investigator:
- `subagent_type`: `general-purpose`, so it inherits every MCP tool the session has. Tell it to write nothing, post nothing, and change no external state.
- `model`: `sonnet`

Each investigator gets:
1. the base prompt in `references/investigator-prompt.md`
2. the one playbook in `references/sources/` for its category (index: `references/source-playbook.md`), adapted to the MCP at hand
3. `references/sources/incident-postmortem.md` too, **when the target looks defensive** (a nil guard, a retry, a timeout, a `try?` that swallows, a lock or actor hop added late, a feature flag, a launch-argument seam, an `if #available` workaround, a migration fallback)
4. the code anchor from step 2
5. the person's question, verbatim

### The roster

One investigator per category with a reachable source. Each entry says what kind of "why" that category surfaces, so you know what to expect, how to name a gap, and, in the rare provably-irrelevant case, how to justify a skip.

1. **Source control.** git, `gh` PRs and reviews, code comments, tests, in-repo docs and decision logs. Always spawn. The one guaranteed source. Best at *the rationale captured at implementation and review time*.
2. **Issue tracker.** GitHub Issues through `gh issue`, or a tracker MCP (Linear, Jira, and others). Best at *the product or business reason*. Strongest when the why sits outside engineering.
3. **Long-form documents.** A docs MCP (Notion, Google Drive, Confluence, Claude Docs). Best at *design rationale written before the code*.
4. **Team chat and email.** A chat or mail MCP (Slack, Gmail, and others). Best at *deliberation that never reached a doc*. Matters most when the PR and issue trail is thin.
5. **Crash and error reports.** A crash-reporting MCP (Crashlytics, Sentry, and others), crash reports in the repo or handed over (`.ips`, `.crash`), Xcode Organizer and TestFlight feedback when the person can export them. Best at *the exact failure that motivated defensive code*.
6. **Runtime and performance telemetry.** MetricKit payloads the app stores or uploads, Xcode Organizer metrics (launch time, hangs, memory, energy, disk writes), and the app's backend observability through an MCP (Datadog, Grafana, and others). Best at *the production reality behind a timeout, a budget or a cache*.
7. **Product analytics.** An analytics or warehouse MCP (Statsig, Amplitude, Firebase Analytics, BigQuery, and others). Best at *the product and data reality behind a flag, an experiment or a number*.
8. **Agent sessions.** This repo's Claude Code transcripts and project memory. Code an agent wrote carries its reasoning in the session that wrote it. Best at *the trade-offs argued with the owner while the code was written*.

### When to skip an investigator

Skip only with a written reason, and put it in the final Sources consulted section. Two reasons are valid.

- **No source reaches that category** in this session. That is a gap, not a choice. "Team chat skipped. No chat MCP is connected, so the conversation record was not searchable."
- **The source is provably irrelevant**, not probably irrelevant. A high bar. "Crash reports skipped. The target is a build script that never runs in the app."

When the target is one trivial commit and its PR body already holds the full answer, you may answer inline, but only after confirming every other category's search would add nothing. Say so. This is rare.

## 4. Synthesize

Spawn one synthesizer.

- `subagent_type`: `general-purpose`, so it can spot-check citations through the same MCP tools. Tell it to write nothing and change no external state.
- `model`: `opus`

It gets:
1. every investigator's findings, null results included, and every skipped category with its reason
2. the code anchor from step 2
3. the person's question
4. `references/epistemics.md`
5. the template in `references/synthesizer-prompt.md`

## 5. Present

Present the synthesizer's output. Light edits for clarity, or context from the conversation, are fine. **Never rewrite the confidence language.**

## Output

The structure in `references/synthesizer-prompt.md`. The question, The code in question, What we found, What we can reasonably infer, Competing hypotheses, What we don't know, Sources consulted, Confidence summary. Adapt it as needed, but keep the tiers separate, and keep Sources consulted as one line per category, including the empty ones and the skipped ones with their reason.

When the question precedes a change to this code, end with a constraint set built from the findings. **Preserve** (what the record says must stay), **Change** (what the record says is free to move), **Avoid** (what was tried and failed), **Risk** (what would break, and who to ask first).

## Failure mode to avoid

**Recency bias.** The latest commit is not the authority. The current shape is often many earlier decisions stacked up. Trace back.

## Reference files

- `references/epistemics.md`. The confidence tiers and phrasing guide.
- `references/investigator-prompt.md`. The base prompt for each investigator.
- `references/source-playbook.md`. The index of category playbooks.
- `references/sources/*.md`. One playbook per category, plus the cross-cutting `incident-postmortem.md`. Give each investigator the one file for its category.
- `references/synthesizer-prompt.md`. The synthesizer's prompt and the output format.
