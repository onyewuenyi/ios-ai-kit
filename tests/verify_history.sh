#!/usr/bin/env bash
# verify.sh's history (verify.tsv) and history.py, with every gate stubbed to pass or fail on demand.
set -uo pipefail
kit=$(cd "$(dirname "$0")/.." && pwd); pass=0; fail=0
ok() { if eval "$2"; then pass=$((pass+1)); echo "  ok   $1"; else fail=$((fail+1)); echo "  FAIL $1"; fi; }
g() { git -c user.email=t@t -c user.name=t "$@"; }

w=$(mktemp -d); cd "$w" && git init -q -b main app && cd app || exit 1
mkdir -p scripts .claude; cp -R "$kit/template/scripts/ai" scripts/; echo "SCHEME=App" > .claude/ios.env
for s in format build test; do
  printf '#!/bin/bash\n[[ ${STUB_FAIL:-} == *%s* ]] && { [[ %s == test ]] && echo "fail Suite/flaky(): boom"; echo "%s: failed"; exit 1; }\necho "%s: ok"\n' "$s" "$s" "$s" "$s" > "scripts/ai/$s.sh"
done
printf 'print("seams: ok")\n' > scripts/ai/debug-fences.py; printf 'print("reach: ok")\n' > scripts/ai/blast-radius.py
g add -A; g commit -qm base
v() { scripts/ai/verify.sh --no-visual >/dev/null 2>&1; }
hist=$(git rev-parse --git-common-dir)/ios-ai/verify.tsv
H() { python3 scripts/ai/history.py "$@"; }

v; sha=$(git rev-parse HEAD)
ok "a run appends one row per gate (5 run, visual skipped)" '[[ $(wc -l < "$hist") -eq 6 ]]'
ok "rows carry the full sha and a clean tree" 'awk -F"\t" -v s="$sha" "\$3==s && \$5==0" "$hist" | grep -q build'
ok "a clean passing run counts as verified" 'H verified "$sha"'
ok "the report is stamped with that commit" 'head -1 .build/verify/report.md | grep -q "sha=$sha dirty=0 result=PASS"'

STUB_FAIL=test v
ok "a second run appends, never truncates" '[[ $(cut -f2 "$hist" | sort -u | wc -l) -eq 2 ]]'
ok "a failing test gets its own fail: row" 'grep -q "fail:Suite/flaky()" "$hist"'
ok "the latest run on the commit decides: now not verified" '! H verified "$sha"'
v
ok "fail then pass on the same commit is a flip (a flake)" 'H flips | grep -q "Suite/flaky()"'

echo x >> scripts/ai/format.sh; v
ok "a dirty tree is recorded and never counts as verified" '[[ $(tail -1 "$hist" | cut -f5) == 1 ]] && ! H verified "$sha"'
git checkout -q scripts/ai/format.sh
echo "notes" >> README.md 2>/dev/null || echo "notes" > README.md; git add README.md 2>/dev/null; g commit -qm readme; echo "more notes" >> README.md; v
ok "an uncommitted Markdown note does not make the run dirty" '[[ $(tail -1 "$hist" | cut -f5) == 0 ]]'
git checkout -q README.md

rm -rf .build
ok "history survives rm -rf .build" '[[ -s "$hist" ]]'
git worktree add -q ../wt -b feature 2>/dev/null; (cd ../wt && scripts/ai/verify.sh --no-visual >/dev/null 2>&1)
ok "a worktree appends to the same history" '[[ $(tail -1 "$hist" | cut -f4) == feature ]]'
ok "stats reports a median per gate" 'H stats | grep -q "^build"'
ok "an unverified commit says so" '! H last 0000000 >/dev/null'
echo "$pass passed, $fail failed"; exit $fail
