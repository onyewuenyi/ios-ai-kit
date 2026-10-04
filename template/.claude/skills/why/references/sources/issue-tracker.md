# Issue tracker

## What it holds

- Issues describing features, bugs and their motivation
- Specs or PRDs attached to issues or their parents
- Parent and sub-issue links (an initiative above the tactical ticket)
- Comments that record a clarification, a scope change or a decision
- Labels and milestones (`bug`, `crash`, `app-review`, `perf`, `customer`, a release milestone) that name the kind of motivation
- Linked PRs

The product or business context usually lives here. "We're doing this because a TestFlight tester lost data" or "this is for the 2.0 launch" sits in the tracker, not the code.

## How to search it

GitHub Issues through `gh` is always available when the repo lives on GitHub. A tracker MCP (Linear, Jira, and others) works the same way through its own tools. Inspect its tool list first.

1. **Start with linked issues.** Fetch every issue the seed commits and PRs cite (`#123`, `ENG-1234`). Read each in full, comments included.

   ```bash
   gh issue view <number> --json title,body,author,createdAt,closedAt,labels,milestone,comments
   ```

2. **Search by keyword.** The feature name, the key symbol, the user-facing term, an error string. Try several phrasings.

   ```bash
   gh issue list --state all --search "<terms>" --json number,title,state,createdAt,labels --limit 50
   gh search issues --repo <owner>/<repo> "<terms>"
   ```

3. **Walk the tree.** On a sub-issue, fetch its parent. Sub-issues are tactical. Parents often carry the why.
4. **Read attached specs.** A project or parent issue often links the spec.
5. **Check labels and milestones.** They name the category of motivation and tie the work to a release.

## What good evidence looks like

- An issue that states the problem: "Testers on iOS 26 lose edits made offline"
- A comment that records a decision: "Going with a background context. Doing it on the main context hitches the list"
- A parent named like an initiative: "Family sharing launch"
- An attached spec
- Labels such as `crash`, `app-review`, `data-loss`, `perf-regression`

## Pitfalls

- **Scope drift.** The cited issue may have been closed and reopened with a new scope. Read its whole history.
- **Template filler.** A required "Why" section filled with "improve the experience" is not an answer.
- **Stale issues.** Old issues describe a plan that changed. Compare dates with the code's ship date.
- **Duplicate chains.** Follow "duplicate of" back to the canonical issue.
- **No access.** If you cannot open an issue, record the gap. Don't guess its content.

## What to return

For each relevant issue:
- number or ID, and title
- the motivation, quoted from the body or comments
- labels, parent, milestone
- author, created and closed dates
- the URL
