#!/usr/bin/env bash
# Hook fixtures: feed recorded tool events to the kit's hooks and check each decision.
set -uo pipefail
k=$(cd "$(dirname "$0")/../template/.claude/hooks" && pwd); pass=0; fail=0
dec() { python3 "$k/guard.py" | python3 -c 'import json,sys; d=sys.stdin.read().strip(); print(json.loads(d)["hookSpecificOutput"]["permissionDecision"] if d else "allow")'; }
ev() { python3 -c 'import json,sys; print(json.dumps({"tool_name":sys.argv[1],"tool_input":{sys.argv[2]:sys.argv[3]}}))' "$@"; }
check() { if [[ "$2" == "$3" ]]; then pass=$((pass+1)); echo "  ok   $1"; else fail=$((fail+1)); echo "  FAIL $1: got $2, want $3"; fi; }
check "name-only simulator destination is denied" "$(ev Bash command "xcodebuild -scheme A -destination 'platform=iOS Simulator,name=iPhone 17 Pro' build" | dec)" deny
check "destination with OS= is allowed" "$(ev Bash command "xcodebuild -destination 'platform=iOS Simulator,name=iPhone 17 Pro,OS=27.0' build" | dec)" allow
check "destination by id is allowed" "$(ev Bash command "xcodebuild -destination id=ABC build" | dec)" allow
check "generic device destination is allowed" "$(ev Bash command "xcodebuild -destination 'generic/platform=iOS' archive" | dec)" allow
check "erase all asks" "$(ev Bash command "xcrun simctl erase all" | dec)" ask
check "unrelated command is allowed" "$(ev Bash command "ls -la" | dec)" allow
check "new model version edit is allowed" "$(ev Edit file_path "/tmp/X.xcdatamodeld/X 2.xcdatamodel/contents" | dec)" allow
check "Swift edit is allowed" "$(ev Edit file_path "/tmp/A.swift" | dec)" allow
check "garbage input is allowed" "$(echo nope | dec)" allow
# `booted` is denied only when it is ambiguous (more than one booted simulator).
n=$(xcrun simctl list devices booted -j | python3 -c 'import json,sys;print(sum(len(v) for v in json.load(sys.stdin)["devices"].values()))')
want=$([[ $n -gt 1 ]] && echo deny || echo allow)
check "simctl booted with $n booted simulator(s) -> $want" "$(ev Bash command "xcrun simctl io booted screenshot /tmp/x.png" | dec)" "$want"
# committed model version asks
repo=$(mktemp -d); git -C "$repo" init -q; mkdir -p "$repo/M.xcdatamodeld/M.xcdatamodel"; echo '<m/>' > "$repo/M.xcdatamodeld/M.xcdatamodel/contents"
git -C "$repo" add -A; git -C "$repo" -c user.email=t@t -c user.name=t commit -qm m
check "committed model version edit asks" "$(cd "$repo" && ev Edit file_path "$repo/M.xcdatamodeld/M.xcdatamodel/contents" | dec)" ask
# stop-check: never blocks twice, skips without code changes, ignores repos without the kit
sc() { python3 "$k/stop-check.py"; echo "rc=$?"; }
check "stop check yields when stop_hook_active" "$(echo '{"stop_hook_active":true,"cwd":"/tmp"}' | sc 2>/dev/null | tail -1)" rc=0
check "stop check is silent outside a kit repo" "$(echo "{\"cwd\":\"$repo\"}" | sc 2>/dev/null | tail -1)" rc=0
check "stop check can be turned off" "$(echo "{\"cwd\":\"$repo\"}" | IOS_AI_STOP_CHECK=0 sc 2>/dev/null | tail -1)" rc=0
echo "$pass passed, $fail failed"; exit $fail
