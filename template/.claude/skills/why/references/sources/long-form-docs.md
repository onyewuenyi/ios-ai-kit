# Long-form documents

## What it holds

- Product specs and PRDs
- Technical designs, RFCs and decision records kept outside the repo
- Design review notes
- Postmortems
- Runbooks that explain defensive code
- App Review correspondence and the plans written in response
- Strategy documents that set priorities

The why is often written out here, at length, before it becomes code. A significant feature usually has a doc.

## How to search it

Use the docs MCP the session has (Notion, Google Drive, Confluence, Claude Docs, and others). Inspect its tools first. Most have a search and a fetch.

1. **Search by keyword.** Try:
   - the feature name
   - key type and function names
   - the author's name (a design doc is often written before the code lands)
   - user-facing strings and error text
   - a date range when you know when the code shipped
2. **Fetch the candidates.** Read the full page, not the preview. The rationale is often in the middle.
3. **Follow links and child pages.** Designs often keep alternatives, appendices or implementation notes on sub-pages.
4. **Search meeting notes** when the MCP exposes them. A design review may have recorded the decision.

## What good evidence looks like

- A spec whose Problem or Motivation section matches what the target does
- An Alternatives considered or Rejected approaches section
- A postmortem that names the target as the fix for an incident
- Meeting notes that record "we decided X because Y" near the PR's author and date
- A decision record filled in for real (status, context, decision, consequences)

## Pitfalls

- **Outdated docs.** Specs are written before the code and rarely updated. Compare with the PR.
- **Doc and code drift.** The spec says X, the code does Y. Record both. The synthesizer surfaces the contradiction.
- **Template filler.** Look for specifics, not boilerplate.
- **Unlinked docs.** The best doc may be linked from nowhere. Broad searches help.
- **Several drafts.** Find the final or most recent one. Check dates.
- **No access.** Record a page you cannot open as a gap.

## What to return

For each relevant doc:
- title and URL
- authors and last-updated date
- the motivation, quoted, with its section
- linked pages the synthesizer can cite
- whether the doc was final or a draft
