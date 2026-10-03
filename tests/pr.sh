#!/usr/bin/env bash
# scripts/ai/pr.sh against a local bare remote and a stand-in `gh` that records what it was asked.
set -uo pipefail
kit=$(cd "$(dirname "$0")/.." && pwd); pass=0; fail=0
ok() { if eval "$2"; then pass=$((pass+1)); echo "  ok   $1"; else fail=$((fail+1)); echo "  FAIL $1"; fi; }
g() { git -c user.email=t@t -c user.name=t "$@"; }

setup() {  # a repo whose origin is a bare remote with main, kit scripts committed, and a fake gh
  w=$(mktemp -d); git init -q --bare -b main "$w/remote.git"
  git clone -q "$w/remote.git" "$w/app" 2>/dev/null; cd "$w/app" || exit 1
  mkdir -p scripts .claude; cp -R "$kit/template/scripts/ai" scripts/; echo base > README.md; echo "SCHEME=App" > .claude/ios.env
  g add -A; g commit -qm base; git push -q origin HEAD:main; git remote set-head origin -a >/dev/null
  mkdir -p "$w/bin"; cat > "$w/bin/gh" <<'G'
#!/bin/bash
echo "$*" >> "$GH_LOG"
case "$1 $2" in
  "auth status") exit 0 ;;
  "pr view") [[ -n ${GH_HAS_PR:-} ]] && { echo "https://github.com/o/r/pull/7"; exit 0; }; exit 1 ;;
  "pr create") echo "https://github.com/o/r/pull/8" ;;
esac
G
  chmod +x "$w/bin/gh"; export PATH="$w/bin:$PATH" GH_LOG="$w/gh.log"; : > "$GH_LOG"; unset GH_HAS_PR CLAUDECODE
}
pr() { scripts/ai/pr.sh "$@" 2>&1; }

echo "commits made on main"
setup; echo a > a.txt; g add a.txt; g commit -qm "Fix the empty state"; echo b > b.txt; g add b.txt; g commit -qm "Second step"
head=$(git rev-parse HEAD); out=$(pr)
br=$(git rev-parse --abbrev-ref HEAD)
ok "moves them to a new claude/ branch named for the first commit" '[[ $br == claude/fix-the-empty-state-* ]]'
ok "the commits live on the new branch" '[[ $(git rev-parse HEAD) == "$head" ]]'
ok "main goes back to origin/main" '[[ $(git rev-parse main) == $(git rev-parse origin/main) ]]'
ok "main on the remote is untouched" '[[ $(git --git-dir="$w/remote.git" rev-parse main) == $(git rev-parse origin/main) ]]'
ok "the branch is pushed" '[[ $(git --git-dir="$w/remote.git" rev-parse "$br") == "$head" ]]'
ok "the PR targets main from that branch" 'grep -q -- "pr create --base main --head $br" "$GH_LOG"'
ok "without a fresh /verify report the body says so" 'grep -q "/verify has not run on this commit" "$GH_LOG"'
ok "it prints the PR url" '[[ $out == *"opened https://github.com/o/r/pull/8"* ]]'

echo "uncommitted files are named and left alone"
setup; echo e > README.md; echo a > a.txt; g add a.txt; g commit -qm "Only this"; out=$(pr)
ok "names the uncommitted file" '[[ $out == *"not in this PR"*README.md* ]]'
ok "the PR still opens" '[[ $out == *"opened https://github.com/o/r/pull/8"* ]]'
ok "the uncommitted edit is still there" '[[ $(cat README.md) == e ]]'
ok "the uncommitted edit is not in the pushed branch" '[[ $(git show "$(git rev-parse --abbrev-ref HEAD)":README.md) == base ]]'

echo "a feature branch with a fresh /verify report"
setup; g switch -qc feature/thing; echo c > c.txt; g add c.txt; g commit -qm "Thing"
mkdir -p .build/verify; echo "| 1 | format | PASS |" > .build/verify/report.md
out=$(pr)
ok "uses the current branch" 'grep -q -- "--head feature/thing" "$GH_LOG"'
ok "the body is the /verify report" 'grep -q "| 1 | format | PASS |" "$GH_LOG"'
ok "a single commit titles the PR" 'grep -q -- "--title Thing" "$GH_LOG"'

echo "an open PR is updated, not duplicated"
setup; g switch -qc feature/again; echo d > d.txt; g add d.txt; g commit -qm "Again"; export GH_HAS_PR=1
out=$(pr)
ok "reports the existing PR" '[[ $out == *"updated https://github.com/o/r/pull/7"* ]]'
ok "never calls pr create" '! grep -q "pr create" "$GH_LOG"'

echo "refusals"
setup; out=$(pr)
ok "nothing to propose" '[[ $out == *"nothing to propose"* ]]'
echo f > f.txt; g add f.txt; g commit -qm "Dry"; out=$(pr --dry-run)
ok "--dry-run changes nothing" '[[ $(git rev-parse --abbrev-ref HEAD) == main && $out == *"nothing changed"* ]]'

echo "$pass passed, $fail failed"; exit $fail
