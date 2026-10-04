# Team chat and email

## What it holds

- Real-time discussion of problems and decisions
- Incident threads where a fix was decided under pressure
- Design threads where trade-offs were argued
- Questions answered by a senior engineer that never reached a doc
- Threads after a merge that explain why something was revisited
- Email with Apple (App Review, Developer Technical Support), testers and partners
- Direct messages, usually not searchable

Chat is often where the real decision happened, especially for a change too small for a doc. It is also the most fragile source. Threads get deleted, channels get archived, retention cuts history off.

## How to search it

Use the chat or mail MCP the session has (Slack, Gmail, Discord, and others). Inspect its tools first. Some need authentication. If authentication fails, stop and report the gap.

1. **Search by author and date.** Messages from the PR author around the merge date. This narrows the search sharply and often finds the thread.
2. **Search by keyword.** The feature name, key symbols, the casual name people use for it, misspellings included.
3. **Search for the PR.** People link PRs when they review or discuss them. Search the PR URL or `/pull/<number>`.
4. **Search the error text.** If the code handles a specific error or crash, search its message.
5. **Narrow by channel or label.** Engineering, project, release, incident and App Review channels or mail labels.
6. **Read the whole thread.** When a message is relevant, fetch its thread. The decision is often in the replies.

## What good evidence looks like

- A thread that argues a trade-off ("a background context avoids the hitch, but merges get harder")
- An incident thread describing the bug the code prevents
- A reviewer's question and the author's answer
- An App Review or DTS email that states the constraint
- A message from the product owner explaining a user's ask

## Pitfalls

- **Retention cliffs.** If nothing exists before some date, name the cliff.
- **Unsearched DMs.** Many decisions happen in private messages you cannot see. Say so.
- **Jokes read as decisions.** "lol just ship it" is not a decision. Look for considered discussion.
- **A message without its thread** reads differently. Always fetch the thread.
- **Auth failures.** If the MCP is not authenticated, stop. Report that the source was not searchable. Never invent findings.

## What to return

For each relevant thread or email:
- channel, label or mailbox
- permalink or thread ID
- participants
- date range
- key quotes, verbatim, with attribution
- what larger discussion or incident it belonged to
