# Understand the code before changing it

Editing code you don't understand is how subtle regressions ship. On iOS they ship to a phone you can't reach, inside a review cycle measured in days. The kit gives you four ways in. `/how` explains what the code does now. `/why` digs up the reasons it is shaped that way. `/teach` blends both into one explanation. `/recall` rebuilds your own recent context on a topic.

Picture a detective with a blueprint of the machine. Helpers fetch the case files. The evidence board links each clue to where it came from. `/how` is the blueprint. `/why` is the case files.

## Trace behavior with `/how`

```text
/how does a task get from the capture sheet into Core Data? is the save on the main thread?
```

Ask the question you actually have. [`/how`](../../template/.claude/skills/how/SKILL.md) reads the code and answers at the level of a senior engineer onboarding you onto the subsystem. You get the runtime flow, the key types, which actor owns what, and the non-obvious parts. For a big subsystem it fans out two to four read-only `Explore` subagents first, so the bulk reading stays out of your session. For a narrow question it just reads and explains.

It reads an Xcode project the way the build does. It checks target membership, build settings that change behavior (`SWIFT_DEFAULT_ACTOR_ISOLATION`, Swift language mode), and which `#if` branch actually compiles.

## Dig up history with `/why`

```text
/why does the sync debounce at 2 seconds? does the reason still hold on iOS 27?
```

[`/why`](../../template/.claude/skills/why/SKILL.md) works like a detective on a cold case. It starts from git history and the pull requests on GitHub, then queries whatever other sources your Claude Code session can reach through MCP, such as the issue tracker, long-form docs, team chat, and crash or analytics dashboards, all in parallel. The report cites everything, separates direct evidence from inference, and says "appears to" when the record is thin. A null result gets reported too, because "nobody wrote down why" is itself an answer.

The two compose naturally. `do why first then how` is a perfectly good prompt when you suspect the history explains the mess.

## Actually understand it with `/teach`

```text
/teach me how this PR changes the Core Data merge policy. convince me it fixes the duplicate rows and not just hides them.
```

[`/teach`](../../template/.claude/skills/teach/SKILL.md) is for when a summary isn't enough. It runs `/how` and `/why`, for a small change maybe just one of them, and weaves the findings into a plain explanation that builds up one small diagram at a time. The "convince me" framing is worth stealing. It turns the explanation into an argument you can poke at instead of a tour.

## Rebuild your own context with `/recall`

```text
/recall catch me up on the widget work from last week
```

[`/recall`](../../template/.claude/skills/recall/SKILL.md) mines your own recent Claude Code sessions for this repo, plus the shared record (open PRs, issues, the verify history of recent commits), and hands back a brief on where things stand and what is next. Use it when you are returning to a topic cold. If you want to resume one specific session's work, that is the Session pickup playbook below, not `/recall`.

## Take over prior work with Session pickup

When another agent, a cloud session, or you last week left a branch mid-flight, say this.

```text
/ios-loop take over this branch. read the decision log, figure out what's done, and continue from there. don't redo finished work.
```

The Session pickup playbook treats the prior trail as authoritative. It reconstructs the branch state and decisions, reads `python3 scripts/ai/history.py last` for what was verified at which commit, names the resume point, and checks inherited claims against the original goal instead of re-deriving everything. A cloud-authored branch was never compiled with Xcode, so pickup builds it before believing anything it says. Its partner, the Pause safely playbook, is what you ask for when you are the one leaving.

**Pitfall.** Don't skip this page's skills because "the agent will read the code anyway". An agent that starts editing without a traced model tends to fix the symptom at the first plausible spot, like adding a `DispatchQueue.main.async` around a crash it never understood. `/how` first is cheaper than the second bug.

Next is [Design the change](./04-design.md).
