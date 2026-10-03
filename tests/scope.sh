#!/usr/bin/env bash
# The gates' scope: a branch's committed work counts, not only what is uncommitted.
set -uo pipefail
kit=$(cd "$(dirname "$0")/.." && pwd); pass=0; fail=0
ok() { if eval "$2"; then pass=$((pass+1)); echo "  ok   $1"; else fail=$((fail+1)); echo "  FAIL $1"; fi; }
g() { git -c user.email=t@t -c user.name=t "$@"; }
w=$(mktemp -d); git init -q --bare -b main "$w/remote.git"; git clone -q "$w/remote.git" "$w/app" 2>/dev/null; cd "$w/app" || exit 1
mkdir -p scripts .claude App; cp -R "$kit/template/scripts/ai" scripts/; echo "SCHEME=App" > .claude/ios.env
echo 'struct A {}' > App/A.swift; g add -A; g commit -qm base; git push -q origin HEAD:main; git remote set-head origin -a >/dev/null
cf() { (source scripts/ai/lib.sh; changed_files); }
ok "on main with nothing ahead, nothing is in scope" '[[ -z $(cf) ]]'
g switch -qc claude/x; echo 'struct B {}' > App/B.swift; g add App/B.swift; g commit -qm b
ok "a committed change on the branch is in scope" '[[ $(cf) == *App/B.swift* ]]'
echo 'struct C {}' > App/C.swift
ok "untracked work is in scope too" '[[ $(cf) == *App/C.swift* && $(cf) == *App/B.swift* ]]'
ok "the base is where the branch left main" '[[ $( (source scripts/ai/lib.sh; base_commit) ) == $(git merge-base HEAD origin/main) ]]'
out=$(python3 scripts/ai/blast-radius.py --diff "$(git merge-base HEAD origin/main)" --src App 2>&1)
ok "blast radius sees the branch's committed Swift change" '[[ $out != *"No Swift changes"* ]]'
dd=$( (source scripts/ai/lib.sh; echo "$DD") )
python3 -c 'import time; time.sleep(20)' xcodebuild build -derivedDataPath "$dd" -scheme App & fake=$!
sleep 1
out=$(scripts/ai/check.sh 2>&1)
ok "the Stop check skips while another build holds this DerivedData" '[[ $out == *"skipped, a build or test is already running"* ]]'
out=$( (source scripts/ai/lib.sh; BUILD_WAIT=2 wait_dd) 2>&1 )
ok "a build waits for it, then says plainly it is still busy" '[[ $out == *"waiting for it"* && $out == *"still busy"* ]]'
kill $fake 2>/dev/null; wait $fake 2>/dev/null
ok "free again: nothing waits" '( source scripts/ai/lib.sh; ! dd_busy )'
git remote remove origin
ok "with no remote, the scope falls back to uncommitted work" '[[ $(cf) == *App/C.swift* && $(cf) != *App/B.swift* ]]'
echo "$pass passed, $fail failed"; exit $fail
