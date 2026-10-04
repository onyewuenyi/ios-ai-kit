# Incidents and postmortems

Not a separate source. A cross-cutting angle. Incidents often motivate defensive code ("we added this after the sync outage"). When the target looks defensive (a nil guard, a retry, a timeout, a swallowed error, a late actor hop, a feature flag, an `if #available` workaround, a migration fallback), hunt for incident history inside your own source.

- **Source control.** Messages like "hotfix", "fix crash", "add defensive check", a revert followed by "re-apply with", an expedited build number bump, a release branch.
- **Issue tracker.** Issues labeled `crash`, `data-loss`, `incident`, `postmortem`, `app-review`, or a hotfix milestone.
- **Long-form documents.** Postmortems that name the target file, the feature or the error text.
- **Team chat and email.** Incident and release channels around the date the target was added. App Review rejection mail and expedited review requests.
- **Crash and error reports.** Groups whose first and last seen bracket the target's ship date, with stacks through the target.
- **Runtime and performance telemetry.** Hang or memory spikes, backend incidents, monitors created as postmortem action items.
- **Product analytics.** An error-reporting event that spikes in the incident window and falls after the fix ships. That supports the claim that the target resolved the user-visible symptom even when the crash data is noisy.
- **Agent sessions.** A session where the owner reported the incident and the fix was written.

When you find an incident, read the whole postmortem. Its action items usually tie straight to code changes. When several sources corroborate (a crash group ID in an issue, which a postmortem cites, which a chat thread links to the target PR, and the error event falls after the release), the evidence is especially strong.

Spend time here only when the code's defensive character makes an incident origin plausible.
