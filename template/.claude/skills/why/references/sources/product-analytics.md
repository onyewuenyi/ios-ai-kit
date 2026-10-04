# Product analytics

## What it holds

The product and data view: what people did in the app, which experiments and flags ran, how use of a feature changed, where a constant came from.

- **Product events** the app logs (Statsig, Amplitude, Firebase Analytics, Mixpanel, a warehouse table)
- **Experiment and feature-flag records**: exposures by variant, the decision recorded at the end
- **Usage and cost events** for paid backends, such as model calls or sync volume
- **Warehouse query history and lineage**, when the analytics live in SQL

## How to search it

Use the analytics or warehouse MCP the session has. Inspect its tools first. Schemas and event names are specific to each app. **Probe before you trust a name.** List the events or tables and read a definition before querying one.

**Bound every query in time.** A window of about 30 days either side of the target's ship date. Widen it only with a reason.

Patterns that tend to pay off:

1. **Usage trajectory.** Daily counts of the relevant event across the window around the merge. A step from zero to steady volume within a day or two of release suggests the PR launched the feature. A decay to zero suggests a removal. App releases roll out over days, so expect a ramp, not a step, and line it up with the release date, not the merge date.
2. **Where a threshold came from.** The distribution (median, p99, max) of the relevant property in the weeks before the PR. A p99 that matches the target's constant suggests the number was chosen from data.
3. **Flag and experiment lookup.** Find the flag or experiment the target checks, then its exposures by variant and its recorded decision near the PR date.
4. **Query history** for a migration, a backfill or a performance rewrite of the backend, filtered by the table or symbol and a tight window.

## What good evidence looks like

- An error-reporting event that drops to near zero after a defensive change ships
- An experiment record naming the target's flag with a shipped or concluded decision around the release
- A property distribution whose p99 matches the constant in the code

## Pitfalls

- **Instrumented is not caused.** An event's existence shows someone logged it, not that the code exists because of it. Pair it with a citation from source control before claiming cause.
- **Instrumentation changes.** A step in volume may mean a new event started logging, not a change in behavior. Check for instrumentation PRs in the same window.
- **Schema drift.** A property that exists today may not have existed when the target was written.
- **Release rollout.** Phased release, App Store review time and slow updaters spread a change over weeks. Segment by app version, not only by date.
- **Retention cliffs.** If the window predates the data's retention, that is a gap, not a null result. Name it.
- **Unconfirmed tables.** Reporting a result from a table or event you never confirmed exists is a classic failure.

## What to return

For each finding:
- type (product event, experiment exposure, usage event, query history)
- the event or table name, and the exact query
- the time window
- a compact numeric summary (counts, percentiles, first and last seen). No raw rows.
- how it lines up with the target's release date and app version
- its strength: direct, circumstantial or weak
