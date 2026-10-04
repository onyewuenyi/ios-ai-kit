## What changed and why

<!-- scripts/ai/pr.sh fills the section below from .build/verify/report.md when /verify ran on this commit. -->

## Verification (`/verify`)

| # | Gate | Result | Time | Summary |
|---|---|---|---|---|
| 1 | format | | | |
| 2 | build (no new warnings) | | | |
| 3 | tests | | | |
| 4 | seams (no launch-argument read outside `#if DEBUG`) | | | |
| 5 | reach (screens the change can affect) | | | |
| 6 | visual: default · dark · AX5, judged | | | |
| 7 | release (with `--release`) | | | |

**Not verified here** (device-only behavior, skipped gates): …

- [ ] New files are in the right target (synchronized folder or explicit membership)
- [ ] Empty, loading, error and success states exercised for any new screen
- [ ] Animation changes checked with Reduce Motion
- [ ] Label `cloud-authored` is set if this branch came from a cloud session, and `/verify` ran on a Mac
