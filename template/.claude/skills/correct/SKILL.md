---
name: correct
description: Find the mistakes agents keep repeating in this repo, from Claude Code transcripts, git reverts and fix-up commits, and PR review comments, and make each one impossible. Architecture first, then types, then a check whose error names the fix, then a test, docs last. Prove each check fails on a real past mistake, and keep the rule table in CLAUDE.md. Use for /correct, and each time the owner corrects an agent for something that happened before.
argument-hint: "[--since 30d]"
disable-model-invocation: true
---

# Correct

**Job:** turn every mistake class agents repeat in this repo into structure that makes it impossible, proven against a real past instance, and keep the rule table that says what enforces each rule.

**Not my job:** one session's lessons (`/reflect`) · friction that is not a mistake, such as permission prompts and slow gates (`/friction`) · a mistake seen once (it is a class at two) · editing the ios-ai-kit block in CLAUDE.md.

**When there is nothing to report:** "No repeated mistake classes since <since>", with the sources read and the one candidate closest to a class.

The owner keeps correcting agents in this repo for the same mistakes. Change the repo so the next agent cannot make them.

Assume every contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Design the repo so a change that looks right from one file is right for the whole app.

## 1. Find the mistake classes

Read the evidence. Default window 30 days.

- **Claude Code transcripts.** `python3 scripts/ai/friction.py --since 30d --json` lists rejected tool calls, repeated hook refusals and recurring compiler errors across this repo's sessions and worktrees. Then read the owner's own corrections in the transcripts it reads (`~/.claude/projects/<repo path with every non-alphanumeric as ->*/*.jsonl`): user turns that say no, stop, undo, "I said", "again", "don't", right after an assistant change.
- **Git reverts and fix-up commits.** `git log --since=30.days --grep='^Revert' --oneline`, `git log --since=30.days --grep='fixup!' --grep='^fix' -i --oneline`, and commits that touch a file a previous commit in the same PR touched. Read what each one undid.
- **PR review comments.** `gh pr list --state merged --limit 30 --json number,title`, then for each one `gh pr view <n> --comments` (review bodies and the conversation) and `gh api repos/<owner>/<repo>/pulls/<n>/comments` (the inline comments, with the repo's owner and name filled in). Group the comments that asked for the same change.
- **Instruction files and workaround comments.** `CLAUDE.md`, `.claude/rules/*.md`, the playbooks, and source comments that explain a workaround (`// Don't`, `// Must`, `// NOTE:`). A rule written twice is a rule nothing enforces.

Group the mistakes into classes. A class counts once it has happened twice. Name the evidence for each instance (a session id and date, a SHA, a PR comment link).

## 2. Fix each class at the highest level that works

1. **Eliminate it with architecture.** Give each piece of state one owner and each task one supported way. Hide internals so the wrong use fails the build (`private`, a local Swift package with a small `public` surface). Replace hand-synced lists with one source of truth (`CaseIterable`, an exhaustive `switch` with no `default`). Delete old ways and dead code an agent would copy. The red flags in `.claude/skills/architect/references/design-red-flags.md` are the usual causes.
2. **Enforce it with types, so the bad state cannot be written.** A non-optional, an enum with payloads instead of flags, a `@MainActor` or actor boundary, a `Sendable` requirement, a wrapper type whose only initializer validates. If bad code still compiles, add a check whose error names the file, type or function to use instead: a Swift Testing test that walks the sources (the way `scripts/ai/debug-fences.py` walks launch-argument reads), a swift-format or SwiftLint rule if the repo runs one, or a hook. If the pattern is already common, fail only when a change adds more.
3. **Test the behavior.** Fix or delete any test that would still pass if every function it calls returned nothing.
4. **Write docs or agent rules last, only for judgment calls.** Nothing fails when an agent skips them.

## 3. Fix and prove

Fix the most frequent classes now, one commit each, through the `ios-loop` skill. Prove each new check fails on a real past mistake: check out or re-apply the offending change from step 1 on a scratch branch and show the check failing on it, then passing on the fix. Run the same command locally and in `/verify` (a test in the scheme runs in both). Exceptions go on the offending line with a reason, an expiry date, and a human's approval.

## 4. Keep the rule table

Keep a table in the repo's `CLAUDE.md`, OUTSIDE the `<!-- ios-ai-kit:begin` … `<!-- ios-ai-kit:end -->` block (the installer rewrites everything inside it). One row per rule:

| Rule | Enforced by | Proof it fails | Since |
|---|---|---|---|
| Views never hold `NSManagedObject` | `TaskStore` is the only public type in the `Store` package | `a1b2c3d` (re-applied: build fails) | 2026-10-03 |

When the owner corrects you, fix the mistake and add the rule. If the rule was already there and nothing enforces it, that is a repeat, so fix it at the highest level in the same change. Drop a rule once its mistake cannot happen (the build already refuses it). Open the PR with `scripts/ai/pr.sh`.

**Reply:** each class with its evidence, the level you picked, why a higher level did not work, the proof each check fails on a past mistake, and the rule table's changes.
