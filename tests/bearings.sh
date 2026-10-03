#!/usr/bin/env bash
# The SessionStart bearings: each line appears when its condition holds, silence when all is well.
set -uo pipefail
kit=$(cd "$(dirname "$0")/.." && pwd); pass=0; fail=0
ok() { if eval "$2"; then pass=$((pass+1)); echo "  ok   $1"; else fail=$((fail+1)); echo "  FAIL $1"; fi; }
g() { git -c user.email=t@t -c user.name=t "$@"; }
w=$(mktemp -d); git init -q --bare -b main "$w/remote.git"; git clone -q "$w/remote.git" "$w/app" 2>/dev/null
cd "$w/app" || exit 1
mkdir -p scripts .claude/hooks; cp -R "$kit/template/scripts/ai" scripts/; cp "$kit/template/.claude/hooks/bearings.py" .claude/hooks/
echo "SCHEME=App" > .claude/ios.env; g add -A; g commit -qm base; git push -q origin HEAD:main; git remote set-head origin -a >/dev/null
sd=$(git rev-parse --git-common-dir)/ios-ai; mkdir -p "$sd"
b() { echo '{"source":"startup"}' | CLAUDE_PROJECT_DIR="$w/app" python3 .claude/hooks/bearings.py; }
ctx() { b | python3 -c 'import json,sys; d=sys.stdin.read(); print(json.loads(d)["hookSpecificOutput"]["additionalContext"] if d.strip() else "")'; }

ok "a clean, current checkout says nothing" '[[ -z $(b) ]]'
start=$(python3 -c 'import time;print(time.time())'); b >/dev/null; secs=$(python3 -c "import time;print(time.time()-$start)")
ok "it is cheap (under 2 s, even beside a running build)" 'python3 -c "import sys; sys.exit(0 if $secs < 2 else 1)"'
echo x > a.txt; g add a.txt; g commit -qm local
ok "commits on main not on origin point at pr.sh" '[[ $(ctx) == *"not on origin: scripts/ai/pr.sh"* ]]'
echo y >> a.txt
ok "uncommitted paths are named" '[[ $(ctx) == *"1 uncommitted path"* ]]'
git checkout -q a.txt; g switch -qc claude/topic
ok "an unverified branch HEAD asks for /verify" '[[ $(ctx) == *"has not been verified"* ]]'
printf '%s\tr1\t%s\tclaude/topic\t0\tbuild\tFAIL\t3\terror\n' "$(date +%s)" "$(git rev-parse HEAD)" > "$sd/verify.tsv"
ok "a failed /verify on HEAD is named with its gate" '[[ $(ctx) == *"FAILED (build)"* ]]'
printf '%s\tr2\t%s\tclaude/topic\t0\tbuild\tPASS\t3\tok\n' "$(date +%s)" "$(git rev-parse HEAD)" >> "$sd/verify.tsv"
python3 -c "import json,time; json.dump({'generated': time.time()-7200, 'items': [{'number': 40, 'bucket': 'needs-you', 'action': 'merge-ready'}, {'number': 39, 'bucket': 'needs-work', 'action': 'verify'}]}, open('$sd/prs.json','w'))"
ok "needs-you PRs from the cached digest, with its age" '[[ $(ctx) == *"Needs you (2h old"*"#40 merge-ready"* && $(ctx) != *"#39"* ]]'
printf '%s\nWARN gh is not signed in\n' "$(date +%s)" > "$sd/doctor.txt"
ok "doctor warnings are carried" '[[ $(ctx) == *"doctor: WARN gh is not signed in"* ]]'
printf '%s\n' "$(( $(date +%s) - 9*86400 ))" > "$sd/doctor.txt"
ok "a doctor run older than 7 days is named" '[[ $(ctx) == *"doctor.sh last ran 9d ago"* ]]'
printf '%s\tr0\tdead\tmain\t0\tbuild\tPASS\t1\tok\n' "$(( $(date +%s) - 10*86400 ))" | cat - "$sd/verify.tsv" > "$sd/v" && mv "$sd/v" "$sd/verify.tsv"
ok "friction not run in 7 days of use is named" '[[ $(ctx) == *"/friction"* ]]'
touch "$sd/friction.last"
ok "…and is quiet once it ran" '[[ $(ctx) != *"/friction"* ]]'
ok "silent in a cloud session" '[[ -z $(echo "{}" | CLAUDE_CODE_REMOTE=true CLAUDE_PROJECT_DIR="$w/app" python3 .claude/hooks/bearings.py) ]]'
ok "garbage input still exits 0" 'echo nope | CLAUDE_PROJECT_DIR="$w/app" python3 .claude/hooks/bearings.py >/dev/null'
ok "a repo without the kit is ignored" '[[ -z $(echo "{}" | CLAUDE_PROJECT_DIR=/tmp python3 .claude/hooks/bearings.py) ]]'
echo "$pass passed, $fail failed"; exit $fail
