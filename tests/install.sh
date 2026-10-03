#!/usr/bin/env bash
# Installer tests against a real Xcode project (Plantly's first commit, cloned to a temp dir).
set -uo pipefail
here=$(cd "$(dirname "$0")" && pwd); kit="$here/.."; pass=0; fail=0
ok() { if eval "$2"; then pass=$((pass+1)); echo "  ok   $1"; else fail=$((fail+1)); echo "  FAIL $1"; fi; }
src=${PLANTLY:-$HOME/Projects/Plantly}
first=$(git -C "$src" rev-list --max-parents=0 HEAD)
fresh() { local d; d=$(mktemp -d)/app; git clone -q "$src" "$d"; git -C "$d" checkout -q "$first"; echo "$d"; }

echo "fresh project"
r=$(fresh); out=$(python3 "$kit/install.py" "$r" 2>&1)
ok "detects project, scheme, bundle and synchronized folders" '[[ $out == *"Plantly.xcodeproj · scheme Plantly · dev.example.Plantly · iOS 27.0 · synchronized folders"* ]]'
ok "writes ios.env with the scheme" 'grep -qx "SCHEME=Plantly" "$r/.claude/ios.env"'
ok "ios.env carries the cloud gate defaults" 'grep -qx "CLOUD_BRANCH_PREFIX=claude/" "$r/.claude/ios.env" && grep -qx "CLOUD_PUBLISH=1" "$r/.claude/ios.env"'
ok "every kit script is executable" '[[ -z $(find "$r/scripts/ai" -name "*.sh" ! -perm -u+x) ]]'
ok "CLAUDE.md has exactly one kit block" '[[ $(grep -c "ios-ai-kit:begin" "$r/CLAUDE.md") == 1 ]]'
ok "settings has the four hook events and worktree.baseRef head" 'python3 -c "import json,sys;d=json.load(open(\"$r/.claude/settings.json\"));assert set(d[\"hooks\"])=={\"PreToolUse\",\"PostToolUse\",\"PermissionRequest\",\"Stop\"} and d[\"worktree\"][\"baseRef\"]==\"head\""'
ok ".gitignore has the local-only paths" 'grep -qx ".claude/ios.local.env" "$r/.gitignore" && grep -qx ".build/" "$r/.gitignore"'
ok ".swift-format matches the code (4 spaces)" 'python3 -c "import json;assert json.load(open(\"$r/.swift-format\"))[\"indentation\"][\"spaces\"]==4"'
again=$(python3 "$kit/install.py" "$r" 2>&1)
ok "second install changes nothing" '! grep -qE "^\s+(added|updated|merged) " <<< "$again"'

echo "merging into an existing setup"
r=$(fresh); mkdir -p "$r/.claude"
cat > "$r/.claude/settings.json" <<'J'
{"permissions":{"allow":["Bash(make:*)","mcp__xcode__XcodeListWindows"]},"enabledPlugins":{"x@y":true},
 "hooks":{"PostToolUse":[{"matcher":"Edit","hooks":[{"type":"command","command":"xcrun swift-format --in-place \"$f\""}]}]}}
J
printf '# Team rules\n\nKeep this line.\n' > "$r/CLAUDE.md"
printf 'PROJECT=Plantly.xcodeproj\nSCHEME=Custom\n' > "$r/.claude/ios.env"
out=$(python3 "$kit/install.py" "$r" 2>&1); python3 "$kit/install.py" "$r" >/dev/null 2>&1
ok "team rules and plugins survive" 'python3 -c "import json;d=json.load(open(\"$r/.claude/settings.json\"));assert \"Bash(make:*)\" in d[\"permissions\"][\"allow\"] and d[\"enabledPlugins\"]=={\"x@y\":True}"'
ok "an existing swift-format hook is kept and ours skipped" '[[ $out == *"skipped  format hook"* ]] && [[ $(grep -c format-swift.sh "$r/.claude/settings.json") == 0 ]]'
ok "retired wrong rules are removed on upgrade" '! grep -q XcodeListWindows "$r/.claude/settings.json"'
ok "an older ios.env gains the cloud keys once, its values kept" 'grep -qx "SCHEME=Custom" "$r/.claude/ios.env" && [[ $(grep -c "^CLOUD_BRANCH_PREFIX=" "$r/.claude/ios.env") == 1 && $(grep -c "^CLOUD_PUBLISH=" "$r/.claude/ios.env") == 1 ]]'
ok "existing CLAUDE.md content is kept" 'grep -q "Keep this line." "$r/CLAUDE.md"'
sed -i '' 's/## iOS loop (ios-ai-kit)/## STALE/' "$r/CLAUDE.md"; python3 "$kit/install.py" "$r" >/dev/null 2>&1
ok "an upgrade replaces the block in place" '! grep -q "## STALE" "$r/CLAUDE.md" && [[ $(grep -c "ios-ai-kit:begin" "$r/CLAUDE.md") == 1 ]]'

echo "workspace projects"
r=$(fresh); mkdir -p "$r/App.xcworkspace"
printf '<?xml version="1.0" encoding="UTF-8"?>\n<Workspace version="1.0"><FileRef location="group:Plantly.xcodeproj"></FileRef></Workspace>\n' > "$r/App.xcworkspace/contents.xcworkspacedata"
out=$(python3 "$kit/install.py" "$r" 2>&1)
ok "a workspace is preferred over its project" 'grep -qx "WORKSPACE=App.xcworkspace" "$r/.claude/ios.env"'

echo "simulator ownership"
r=$(fresh); python3 "$kit/install.py" "$r" >/dev/null 2>&1
printf 'SIM_UDID=00000000-0000-0000-0000-000000000000\nSIM_OWNER=/some/other/checkout\n' > "$r/.claude/ios.local.env"
out=$(cd "$r" && /bin/bash scripts/ai/sim.sh destroy 2>&1); rc=$?
ok "destroy refuses another checkout's simulator" '[[ $rc != 0 && $out == *"refusing"* ]]'
out=$(cd "$r" && SIM_UDID=11111111-1111-1111-1111-111111111111 SIM_OWNER=$r /bin/bash -c 'source scripts/ai/lib.sh; echo "${SIM_UDID:-none}"' 2>&1)
ok "an inherited SIM_UDID is ignored (only the checkout's file counts)" '[[ $out == "00000000-0000-0000-0000-000000000000" ]]'
echo "$pass passed, $fail failed"; exit $fail
