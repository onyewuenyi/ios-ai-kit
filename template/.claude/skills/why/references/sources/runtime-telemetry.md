# Runtime and performance telemetry

## What it holds

The record of what the app and its backend actually did in the field, as opposed to what was planned or discussed.

- **MetricKit payloads** (`MXMetricPayload`, `MXDiagnosticPayload`) the app stores or uploads: launch time, hang rate, memory, disk writes, CPU and energy, and diagnostics for hangs, crashes and CPU or disk exceptions
- **Xcode Organizer metrics** per app version: launch time, hang rate, memory, battery, disk writes, scrolling hitches
- **`os_signpost` and `Logger` output** the app ships, when it is collected anywhere
- **Backend observability** for the app's own server, through an MCP (Datadog, Grafana, and others): metrics, monitors, dashboards, traces, logs, incidents
- **Monitors and alerts.** A threshold someone decided was worth waking up for is direct evidence the team worried about that number.

The question this source answers is what the field looked like when the code was written. That often explains a timeout, a budget, a cache, a batch size or a background task.

## How to search it

Use the telemetry sources the session can reach. Inspect each MCP's tools first. Without one, search the repo for stored MetricKit payloads or exported Organizer data, and name Organizer as a gap the person can fill.

1. **Find the owner.** The app target, the extension, or the backend service the target talks to.
2. **Dashboards and monitors first.** They show what the team cared about. When one covers the target, note its query and threshold. The threshold often answers "why is this clamped at N?"
3. **Metrics around the target's date.** Did launch time, hang rate or memory move before the change and settle after? "Hang rate rose to 4% in 1.6, the main-thread import moved to a background context in 1.7, hang rate fell to 0.5%."
4. **Logs, narrowly.** Search by symbol, error text or feature name, always within a time window (about 30 days either side of the change). Unbounded log searches waste time and time out.
5. **Traces and spans** for the backend calls the app makes: timeouts, retries, slow endpoints.
6. **Incidents** near the date the target was added, when the target looks defensive.

## What good evidence looks like

- A monitor whose threshold matches the limit the code enforces
- A dashboard made by the target's author, charting what the code guards
- A metric that spikes just before the merge and settles after
- A MetricKit hang diagnostic whose stack runs through the code the change moved off the main thread
- An incident record naming the target, its symbols or its error text

## Pitfalls

- **Correlation is not causation.** A spike before a change and calm after suggests. Other changes landed in the same window. Check them.
- **Charts carry a framing.** A person named the chart. A chart titled "retry success" shows someone cared about retries, not that a given line exists because of it.
- **Vanished telemetry.** Metrics get renamed or expire. A window with no data is a gap, not a null result.
- **Opt-in data.** Organizer and MetricKit cover only users who share analytics, and Organizer shows recent versions only.
- **Simulator numbers are Mac numbers.** A measurement from the simulator says nothing about a device.
- **Instrumented is not caused.** A metric's existence shows someone measured it, not that the code was written because of it.

## What to return

For each relevant item:
- type (MetricKit payload, Organizer metric, dashboard, monitor, metric, log pattern, trace, incident)
- name and identifier or link
- owner and created or modified date
- the condition, query or value that bears on the question, verbatim when possible
- how strongly it connects to the target, and why
