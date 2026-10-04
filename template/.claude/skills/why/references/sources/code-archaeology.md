# Source control history (git, `gh`, the repo)

## What it holds

- Commits: messages, dates, authors, diffs
- PR descriptions, review comments and discussion, through `gh`
- Code comments, `TODO`, `FIXME`, deprecation notes, `@available(*, deprecated, message:)`
- Decision records and in-repo docs (`docs/`, a decisions log, `CLAUDE.md`, `.claude/rules/`)
- Tests. Their names and assertions often encode the edge case that motivated a change
- Files changed in the same commits (the co-change signal)
- Release notes, a CHANGELOG, `CURRENT_PROJECT_VERSION` and `MARKETING_VERSION` bumps that date a change to a build
- Issue numbers cited in commit messages and PR bodies
- iOS-specific records of a decision: a new `.xcdatamodel` version in the `.xcdatamodeld`, a line in an `.entitlements` file or `Info.plist`, `PrivacyInfo.xcprivacy`, a build setting in `project.pbxproj` or an `.xcconfig`, a pinned package in `Package.resolved`

The most trustworthy source, tied directly to the code, and the most complete. Everything that went through the repo is here.

## How to search it

Widen the seed commit list.

```bash
git log --follow --oneline -- <file>          # history through renames
git log -S '<exact text>' -- <file>           # commits that added or removed this text
git log -G '<regex>' -- <file>                # same, for a pattern
git blame -L <start>,<end> <file>             # who wrote each line, and when
git show <hash>                               # one commit in full
git log <old>..<new> -p -- <file>             # a range
git log --all --oneline -- '*.xcdatamodeld'   # model versions over time
```

For each substantive commit, pull the PR.

```bash
git log -1 --format=%B <hash>
gh pr list --state all --search "<hash>" --json number,title
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews,files
gh api repos/{owner}/{repo}/pulls/<number>/comments   # inline review comments
```

The `comments`, `reviews` and inline review comments hold most of the signal.

Look for out-of-band records.

```bash
rg -l -i 'decision|rationale|why we' docs/ --glob '*.md'
rg -n -C2 '(TODO|FIXME|HACK|XXX|NOTE)' <file>
rg -l '<symbol>' --glob '*Tests*'
rg -n '<constant or launch argument>' --glob '!*.pbxproj'
```

## What good evidence looks like

- A PR description that explains the problem, not only the change ("fixes the duplicate rows after a CloudKit import")
- A long review thread where alternatives were argued
- A comment beside the target that explains a constraint the code cannot show
- A test named `importKeepsExistingTasksWhenTheMirrorFails()` that reveals the edge case
- A commit message that cites an issue, a crash or an App Review rejection
- A decisions-log entry dated near the change

## Pitfalls

- **Squash merges.** The branch's commits are gone. Fall back to the PR body and its comments.
- **Misleading messages.** "Small refactor" sometimes hides a behavior change. Read the diff, not only the message.
- **Copied patterns.** The author may have copied a pattern without knowing why. Find where it first appeared and investigate that commit.
- **Bot and tooling commits.** Dependency bumps, formatter runs and project-file churn from Xcode rarely carry motivation. Skip them when looking for intent.
- **`project.pbxproj` noise.** Xcode rewrites it on unrelated changes. A blame line there dates the last rewrite, not the decision. Use `git log -S` on the setting's value instead.
- **Code as evidence of intent.** The code is not evidence for why it exists. "The function is named X" is not a citation.

## What to return

Every commit, PR, comment, test or doc that bears on the question, with:
- the exact text, quoted
- the hash, PR number or file:line
- author and date
- whether it is direct (addresses the question) or circumstantial
