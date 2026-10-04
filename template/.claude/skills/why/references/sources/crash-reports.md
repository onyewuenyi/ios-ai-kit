# Crash and error reports

## What it holds

The archive of what went wrong in the field. For defensive or corrective code it often holds the direct motivation: the exact exception, the faulting thread, and how often it hit before someone added a guard, a catch, a retry or a fallback.

- **Crash groups** (Crashlytics issues, Sentry issues): counts, first and last seen, affected app versions and OS versions
- **Individual reports**: the faulting thread's stack, exception type and codes (`EXC_BAD_ACCESS`, `EXC_BREAKPOINT` from a Swift trap, a watchdog `0x8badf00d`), device model, OS build
- **Non-fatal errors** the app records (a logged `CKError`, a failed Core Data save)
- **Xcode Organizer** crash and hang reports, and **TestFlight** feedback with its attached crash logs
- **`.ips` and `.crash` files** checked into the repo, attached to issues, or handed over

The most valuable thing here is the timing. "The crash group first appeared in 1.3 (build 41), peaked at 300 a day, and stopped in 1.4 (build 47), the build that shipped the guard."

## How to search it

Use the crash-reporting MCP the session has (Crashlytics, Sentry, and others). Inspect its tools first. Without one, search the repo and the issue tracker for attached reports, and name Organizer and TestFlight as gaps the person can fill by exporting them.

1. **Orient.** Find the project or app and its bundle ID.
2. **Search for crash groups tied to the target.** Use the type and function names in the target, the error or exception it checks for, and its file name. A Swift symbol shows in a stack demangled (`TaskStore.save(_:)`) or mangled (`$s...`). Search both.
3. **Narrow by version and time.** For a candidate group, read:
   - **first seen.** When did it start?
   - **last seen.** When did it stop? Does that match the target's ship date?
   - **affected versions.** Which builds hit it, and which build ended it?
   - **trajectory.** Did it spike and then end?
4. **Read a full report.** Does the faulting thread pass through the target? Do the device, OS and breadcrumbs match the condition the target defends against?
5. **Map versions to commits.** Match the build number (`CURRENT_PROJECT_VERSION`) to the tag or commit that produced it, and compare with the PR's merge date.
6. **Treat AI root-cause summaries as hypotheses.** Some tools generate one. The reports and stacks are the evidence. The summary is not.

## What good evidence looks like

- A group whose first seen falls shortly before the target's PR and whose last seen falls shortly after
- A faulting stack that runs through the target function
- A comment on the group from the PR author describing the fix
- The PR or commit citing the crash group's URL or ID
- A high-count group that ends at the build containing the target

## Pitfalls

- **Grouping drift.** A rename or refactor can move the same crash under a new group ID. If a group ends abruptly, look for a new one that starts the same day.
- **Release correlation is noisy.** A build holds many commits. A crash that ends at build 47 does not prove the target ended it. Check the other changes in that build.
- **Silent fixes.** The crash may stop because an OS update or a framework fix landed, not because of the guard. The timing suggests. It does not prove.
- **Resolved is not fixed.** A person can mark a group resolved with no code change. Treat it as a human marker.
- **Symbolication gaps.** An unsymbolicated report has addresses, not names. Without the dSYM for that build, say the stack could not be read.
- **Sampling and opt-in.** Apple's reports come only from users who share analytics. A low count may mean low opt-in, not a rare crash.
- **Simulator crashes are not field crashes.** A crash seen only on the simulator says little about devices.

## What to return

For each relevant crash group or report:
- ID and title
- project or app
- first seen and last seen
- count, and the sampling or opt-in caveat when known
- affected app and OS versions
- a short verbatim stack excerpt that shows the link to the target
- how first and last seen line up with the target's ship date
- the URL
- any comment or resolution note from the author
