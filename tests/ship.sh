#!/usr/bin/env bash
# The idea-to-merged path's deterministic parts: judge.py validates and records the AI judge's verdict,
# verify.sh runs it, and merge.sh lands a PR only when prs.py --check calls it merge-ready.
set -uo pipefail
kit=$(cd "$(dirname "$0")/.." && pwd); pass=0; fail=0
ok() { if eval "$2"; then pass=$((pass+1)); echo "  ok   $1"; else fail=$((fail+1)); echo "  FAIL $1"; fi; }
g() { git -c user.email=t@t -c user.name=t "$@"; }
w=$(mktemp -d); cd "$w" && git init -q -b main app && cd app || exit 1
mkdir -p scripts .claude; cp -R "$kit/template/scripts/ai" scripts/; echo "SCHEME=App" > .claude/ios.env; echo ".build/" > .gitignore
for s in format build test; do printf '#!/bin/bash\necho "%s: ok"\n' "$s" > "scripts/ai/$s.sh"; done
printf 'print("seams: ok")\n' > scripts/ai/debug-fences.py; printf 'print("reach: ok")\n' > scripts/ai/blast-radius.py
mkdir -p ev; printf 'png' > ev/home.png; printf 'png' > ev/tasks.png
printf '#!/bin/bash\necho "JUDGE %s/ev/home.png"; echo "JUDGE %s/ev/tasks.png"; echo "visual: evidence in ev"\n' "$PWD" "$PWD" > scripts/ai/visual.sh
echo "home | |" > .claude/ios-screens.txt
mkdir -p "$w/bin"; cat > "$w/bin/claude" <<'C'
#!/bin/bash
echo "$*" > "$CLAUDE_LOG"
case ${FAKE_JUDGE:-pass} in
  pass) echo '{"structured_output":{"screens":[{"name":"home","verdict":"PASS","evidence":"all three columns fine"},{"name":"tasks","verdict":"PASS","evidence":"rows wrap at AX5"}]}}' ;;
  fail) echo '{"structured_output":{"screens":[{"name":"home","verdict":"PASS","evidence":"fine"},{"name":"tasks","verdict":"FAIL","evidence":"AX5 title cut to Pay th"}]}}' ;;
  missing) echo '{"structured_output":{"screens":[{"name":"home","verdict":"PASS","evidence":"fine"}]}}' ;;
  noevidence) echo '{"structured_output":{"screens":[{"name":"home","verdict":"PASS","evidence":""},{"name":"tasks","verdict":"PASS","evidence":"x"}]}}' ;;
  garbage) echo 'not json' ;;
esac
C
chmod +x "$w/bin/claude"; export CLAUDE_BIN="$w/bin/claude" CLAUDE_LOG="$w/claude.log"
g add -A; g commit -qm base
hist=$(git rev-parse --git-common-dir)/ios-ai/verify.tsv
H() { python3 scripts/ai/history.py "$@"; }

echo "judge.py through verify.sh"
out=$(FAKE_JUDGE=pass scripts/ai/verify.sh 2>&1)
ok "the AI judge's PASS makes the visual gate PASS" '[[ $out == *"6  visual  PASS"* && $out == *"verify: PASSED"* ]]'
ok "…and the commit is verified" 'H verified'
ok "the report carries the verdict per screen" 'grep -q "Visual verdict: PASS" .build/verify/report.md && grep -q "tasks: PASS. rows wrap at AX5" .build/verify/report.md'
ok "the judge was asked about both sheets, with the checklist and the intent" 'grep -q "home: " "$CLAUDE_LOG" && grep -q "tasks: " "$CLAUDE_LOG" && grep -q "Intended change" "$CLAUDE_LOG"'
ok "the judge may only read" 'grep -q -- "--allowedTools Read" "$CLAUDE_LOG"'
echo x >> README.md; g add README.md; g commit -qm x
out=$(FAKE_JUDGE=fail scripts/ai/verify.sh 2>&1)
ok "a FAIL from the judge fails the gate and the run" '[[ $out == *"6  visual  FAIL"* && $out == *"verify: FAILED"* ]] && ! H verified'
ok "the failing screen and what was seen are printed" '[[ $out == *"tasks: FAIL, AX5 title cut to Pay th"* ]]'
for bad in missing noevidence garbage; do
  echo "$bad" >> README.md; g add README.md; g commit -qm "$bad"
  out=$(FAKE_JUDGE=$bad scripts/ai/verify.sh 2>&1)
  ok "an invalid answer ($bad) is no verdict: the gate stays JUDGE, unverified" '[[ $out == *"6  visual  JUDGE"* ]] && ! H verified'
done
echo y >> README.md; g add README.md; g commit -qm y
out=$(VISUAL_JUDGE=human FAKE_JUDGE=pass scripts/ai/verify.sh 2>&1)
ok "VISUAL_JUDGE=human leaves the judging to a person" '[[ $out == *"6  visual  JUDGE"* && $out == *"await a judge"* ]] && ! H verified'
out=$(PATH=/usr/bin:/bin CLAUDE_BIN=/nonexistent/claude python3 scripts/ai/judge.py 2>&1); rc=$?
ok "without Claude Code the judge says so and records nothing" '[[ $rc == 3 && $out == *"not on PATH"* ]]'
printf -- '- Rows show one line at the default size.\n<!-- a comment -->\n' > .claude/judge-notes.md
out=$(python3 scripts/ai/judge.py --dry-run 2>&1)
ok "the app's judge notes reach the prompt, comments do not" '[[ $out == *"Rows show one line"* && $out != *"a comment"* ]]'

echo "merge.sh"
git init -q --bare -b main "$w/remote.git"; git remote add origin "$w/remote.git"; git push -q origin main 2>/dev/null
cat > "$w/bin/gh" <<'G'
#!/bin/bash
echo "$*" >> "$GH_LOG"
case "$1 $2" in
  "pr view") case "$*" in *headRefName*) echo claude/x ;; *baseRefName*) echo main ;; *state*) echo "${PR_STATE:-OPEN}" ;; esac ;;
  "pr merge") echo merged ;;
esac
G
chmod +x "$w/bin/gh"; export PATH="$w/bin:$PATH" GH_LOG="$w/gh.log"
cat > scripts/ai/prs.py <<'P'
import json, os, sys
v = os.environ.get("PR_VERDICT", "merge-ready")
print(json.dumps({"number": 7, "bucket": "healthy" if v == "healthy" else "needs-you", "action": "" if v == "healthy" else v, "why": "why: " + v}))
sys.exit(0 if v == "merge-ready" else 1)
P
: > "$GH_LOG"; out=$(scripts/ai/merge.sh 7 2>&1)
ok "without --yes nothing merges" '[[ $out == *"add --yes"* ]] && ! grep -q "pr merge" "$GH_LOG"'
out=$(CLAUDE_CODE_REMOTE=true scripts/ai/merge.sh 7 --yes 2>&1)
ok "a cloud session never merges" '[[ $out == *"cloud sessions never merge"* ]] && ! grep -q "pr merge" "$GH_LOG"'
out=$(PR_VERDICT=verify scripts/ai/merge.sh 7 --yes 2>&1)
ok "an unverified PR is refused, with the reason" '[[ $out == *"not merge-ready: verify"* ]] && ! grep -q "pr merge" "$GH_LOG"'
out=$(PR_VERDICT=healthy scripts/ai/merge.sh 7 --yes --wait 0 2>&1)
ok "still-running checks past the wait are refused, not merged" '[[ $out == *"not merge-ready"* ]] && ! grep -q "pr merge" "$GH_LOG"'
out=$(PR_STATE=MERGED scripts/ai/merge.sh 7 --yes 2>&1)
ok "a merge-ready PR merges and deletes its branch" '[[ $out == *"merged into main"* ]] && grep -q "pr merge 7 --merge --delete-branch" "$GH_LOG"'
: > "$GH_LOG"; out=$(PR_STATE=MERGED MERGE_METHOD=squash scripts/ai/merge.sh 7 --yes 2>&1)
ok "MERGE_METHOD picks the merge method" 'grep -q "pr merge 7 --squash" "$GH_LOG"'
out=$(PR_STATE=OPEN scripts/ai/merge.sh 7 --yes 2>&1)
ok "if GitHub did not merge, it says so" '[[ $out == *"GitHub did not merge"* ]]'
echo "$pass passed, $fail failed"; exit $fail
