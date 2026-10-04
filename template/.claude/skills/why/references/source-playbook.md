# Source playbooks

`/why` spawns one investigator per reachable evidence category. Each reads the one playbook below for its category. A playbook describes the category, not one vendor. Adapt it to the MCP the session actually has.

| Category | Playbook | Typical sources |
|---|---|---|
| Source control history | `sources/code-archaeology.md` | git, `gh` PRs and reviews, in-repo docs |
| Issue tracker | `sources/issue-tracker.md` | `gh issue`, Linear, Jira |
| Long-form documents | `sources/long-form-docs.md` | Notion, Google Drive, Confluence, Claude Docs |
| Team chat and email | `sources/team-chat.md` | Slack, Gmail, Discord |
| Crash and error reports | `sources/crash-reports.md` | Crashlytics, Sentry, `.ips` files, Xcode Organizer exports, TestFlight feedback |
| Runtime and performance telemetry | `sources/runtime-telemetry.md` | MetricKit payloads, Xcode Organizer metrics, backend observability (Datadog, Grafana) |
| Product analytics | `sources/product-analytics.md` | Statsig, Amplitude, Firebase Analytics, a SQL warehouse |
| Agent sessions | `sources/agent-sessions.md` | Claude Code transcripts and project memory |

Cross-cutting:

- `sources/incident-postmortem.md`. Add it when the target looks defensive (a nil guard, a retry, a timeout, a swallowed error, a late actor hop, a feature flag, an `if #available` workaround, a migration fallback).
