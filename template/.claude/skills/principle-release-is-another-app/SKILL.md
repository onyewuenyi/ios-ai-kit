---
name: principle-release-is-another-app
description: "Apply when a change touches build settings, Info.plist, entitlements, launch-argument seams, third-party SDKs, the privacy manifest, or submission. Verify the Release artifact you ship (scripts/ai/verify.sh --release, the bundle audit), not the Debug build you tested; a green Debug run proves nothing about the archive."
disable-model-invocation: true
---

# Release Is Another App

The Release build is a different app from the one you tested. Different compiler settings, different code behind `#if DEBUG`, different entitlements and environments, a different signing identity. Verify the artifact you ship.

**Why:** A successful `xcodebuild archive` proves nothing about submission. Each of these has passed every Debug check and still reached, or nearly reached, a Release build.
- Launch-argument seams compiled into Release because a fence was missing. `strings` on the binary cannot check this, because Swift stores literals of 15 bytes or fewer inline where `strings` does not see them.
- No privacy manifest in the built bundle, which App Store review rejects.
- Export compliance unanswered.
- A usage description string missing, so the permission prompt terminates the app.
- An in-process photo picker that needs a permission string the app never declared.
- Development entitlements or a development CloudKit environment in the shipped build.

**Pattern:**
- **Fence every seam.** Every launch-argument or environment read sits inside `#if DEBUG`. `scripts/ai/debug-fences.py` walks the sources and finds the ones outside.
- **Build and read the Release artifact.** `scripts/ai/verify.sh --release` adds the release gate. `scripts/ai/release.sh` audits an archive, through `scripts/ai/audit-bundle.py`, for the privacy manifest, usage strings, export compliance, entitlements and seams. Every FAIL is fixed. Every WARN is fixed or explained.
- **Check the environments.** Production entitlements, the production CloudKit container environment, release API keys and App Check.
- **List what only a human can check** as done or owed. The privacy policy link, App Privacy answers that match the manifest, account deletion if accounts exist, the CloudKit schema deployed to Production. The `release` playbook in `ios-loop` holds the full procedure.
- **Measure performance on Release, on a device,** per `principle-explain-the-number`. Debug numbers are a different app's numbers.

**The test:** Has anyone opened the built Release bundle (not the project) and read what is in it? If not, the release has not been verified.
