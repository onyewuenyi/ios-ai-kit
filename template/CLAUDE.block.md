<!-- ios-ai-kit:begin (managed by ios-ai-kit install.sh; edit .claude/ios.env, not this block) -->
## iOS loop (ios-ai-kit)

- **Project:** {{CONTAINER}} · scheme `{{SCHEME}}` · app `{{BUNDLE_ID}}` · iOS {{DEPLOYMENT}} · files: {{FILE_STYLE}}.
- **Build / test / gate** (each checkout gets its own simulator and `.build/dd`, automatically): `scripts/ai/build.sh` · `scripts/ai/test.sh [-only-testing:Target/Suite/test()]` · `/verify` (format, build with no new warnings, tests, launch-argument safety, blast radius, visual matrix). New machine: `scripts/ai/bootstrap.sh`. Anything odd: `scripts/ai/doctor.sh`.
- **Hard rules:** never edit `*.pbxproj` by hand; never delete project files (disable instead); never change build settings unless the task says so; never print secrets; one logical change per build; drive simulators only through `scripts/ai/sim.sh` (by UDID, never `booted`).
- **Apple's exported skills win** on any API question (`swiftui-specialist`, `swiftui-whats-new-27`, …). The loop, MCP-versus-shell, bug-fix, UI two-pass and parallel rules: the `ios-loop` skill.
- **Cloud sessions have no Xcode:** never run `xcodebuild` or `simctl` there; say "not compiled with Xcode", list every unverified item, push a branch; it merges only after `/verify` passes on a Mac.
<!-- ios-ai-kit:end -->
