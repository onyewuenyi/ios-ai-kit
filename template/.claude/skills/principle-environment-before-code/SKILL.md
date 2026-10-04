---
name: principle-environment-before-code
description: "Apply before you believe a crash, a hang, a 'my change did nothing', or a number from the simulator. On iOS the environment fails like an app bug (a broken simulator runtime, another session's build installed over yours, a destination by name, shared simulator preferences, a half-signed bundle). Run scripts/ai/doctor.sh and a plain-launch guard first."
disable-model-invocation: true
---

# Environment Before Code

Before you debug the app, prove the environment can run a known-good app. On iOS the toolchain, the simulator and the installed build fail in ways that look exactly like app bugs.

**Why:** Each of these has produced a convincing app "bug" that no code change could fix.
- A simulator runtime that can no longer spawn processes. Every launch "crashes", including a build that worked an hour ago, and a batch of runs reads as "0 of 6 survived".
- Another session's build installed over yours on a shared simulator. "My change did nothing."
- A destination given by name (`name=iPhone 17 Pro`) that resolves to another runtime or another session's device.
- `simctl spawn … defaults write` writing the simulator's shared preferences, so a "fresh install" is not fresh.
- A half-signed bundle left in DerivedData by a failed signing step, which breaks every later install.
- A screenshot taken of a process launched with other arguments than the ones you think.

Time spent fixing code against a broken environment is lost, and the "fix" that seems to work is a coincidence you will ship.

**Pattern:**
- **Run `scripts/ai/doctor.sh` first** whenever anything looks off. It is read-only and checks the toolchain, the runtime and this checkout's simulator.
- **Guard every crash measurement.** Run `scripts/ai/sim.sh guard` before and after a batch. A plain launch with no seams must stay alive. If the guard fails, the batch measured the environment, not the app.
- **Use this checkout's simulator, by UDID.** `scripts/ai/sim.sh udid` gives it. Never a device by name, never the one the system calls current. Each worktree gets its own simulator and its own `.build/dd`, so two sessions cannot install over each other.
- **Check what is installed.** `scripts/ai/sim.sh install` verifies the installed binary is the one you built. Before trusting a screenshot, check the process was launched with the arguments you meant.
- **Reset state you did not mean to keep.** `scripts/ai/sim.sh reset-app` gives a fresh install. Remember what survives it (Keychain items, shared simulator preferences).
- **On a signing failure, stop.** Report which certificate or profile is missing. Do not retry into a half-signed bundle.

**The test:** Would a plain launch of a known-good build pass right now, on this simulator? If you have not checked, the next number you read may be about the machine.

Pairs with `principle-fix-root-causes` (reproduce before fixing) and `principle-explain-the-number` (rule out what else a number measured).
