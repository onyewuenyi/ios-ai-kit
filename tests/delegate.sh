#!/usr/bin/env bash
# cloud.sh (delegation to a cloud session) and worktree.sh pr (steering an existing PR's branch),
# with stand-in `claude`, `script` and `gh` that record what they were asked.
set -uo pipefail
kit=$(cd "$(dirname "$0")/.." && pwd); pass=0; fail=0
ok() { if eval "$2"; then pass=$((pass+1)); echo "  ok   $1"; else fail=$((fail+1)); echo "  FAIL $1"; fi; }
g() { git -c user.email=t@t -c user.name=t "$@"; }

w=$(mktemp -d); git init -q --bare -b main "$w/remote.git"; git clone -q "$w/remote.git" "$w/app" 2>/dev/null
cd "$w/app" || exit 1
mkdir -p scripts .claude; cp -R "$kit/template/scripts/ai" scripts/; echo "SCHEME=App" > .claude/ios.env
g add -A; g commit -qm base; git push -q origin HEAD:main
g switch -qc claude/feature; echo f > f.txt; g add f.txt; g commit -qm feature; git push -q origin claude/feature; g switch -q main
mkdir "$w/bin"; export LOG="$w/calls.log"; : > "$LOG"
cat > "$w/bin/claude" <<'C'
#!/bin/bash
if [[ $1 == --help ]]; then [[ -n ${NO_CLOUD:-} ]] && echo "usage" || echo "  --cloud [description]"; exit 0; fi
printf '%s\n' "$*" >> "$LOG"; echo "Created cloud session: x"; echo "View: https://claude.ai/code/session_01TEST?from=cli"
C
cat > "$w/bin/script" <<'S'
#!/bin/bash
shift 2; exec "$@"
S
cat > "$w/bin/gh" <<'G'
#!/bin/bash
[[ "$1 $2" == "pr view" ]] && { [[ "$*" == *state* && "$*" != *headRefName* ]] && { echo "${PR_STATE:-OPEN}"; exit 0; }; [[ $3 == 5 ]] && echo claude/feature; exit 0; }
exit 1
G
chmod +x "$w/bin/"*; export PATH="$w/bin:$PATH"; unset CLAUDE_CODE_REMOTE
tsv=$(git rev-parse --git-common-dir)/ios-ai/cloud.tsv

echo "cloud.sh"
out=$(scripts/ai/cloud.sh "Fix the typo in the README intro" 2>&1)
ok "launches a cloud session and reports its URL" '[[ $out == *"https://claude.ai/code/session_01TEST"* ]]'
ok "the prompt carries the task and the no-Xcode footer" 'grep -q "Fix the typo" "$LOG" && grep -q "Never run xcodebuild" "$LOG"'
ok "the prompt names a claude/ branch and gh pr create" 'grep -q "branch claude/fix-the-typo-in-the-readme" "$LOG" && grep -q "gh pr create" "$LOG"'
ok "the session is recorded for /lead" 'grep -q "session_01TEST" "$tsv" && grep -q "claude/fix-the-typo" "$tsv"'
: > "$LOG"; scripts/ai/cloud.sh --branch claude/feature "Address the review comment" >/dev/null 2>&1
ok "--branch continues that PR's branch" 'grep -q "Work on branch claude/feature:" "$LOG"'
: > "$LOG"; out=$(scripts/ai/cloud.sh --dry-run "Write docs" 2>&1)
ok "--dry-run prints the prompt and launches nothing" '[[ $out == *"Delegated by ios-ai-kit"* && ! -s $LOG ]]'
out=$(scripts/ai/cloud.sh "Take a screenshot on the simulator" --dry-run 2>&1)
ok "a task needing a Mac is warned about" '[[ $out == *"warning"* ]]'
out=$(CLAUDE_CODE_REMOTE=true scripts/ai/cloud.sh "x" 2>&1)
ok "refuses inside a cloud session" '[[ $out == *"already in a cloud session"* ]]'
out=$(NO_CLOUD=1 scripts/ai/cloud.sh "x" 2>&1)
ok "names the fix when this Claude Code has no --cloud" '[[ $out == *"has no --cloud"* ]]'

echo "worktree.sh pr"
g branch claude/feature origin/claude/feature 2>/dev/null; g switch -q claude/feature; echo local > local.txt; g add local.txt; g commit -qm "unpushed"; g switch -q main
out=$(scripts/ai/worktree.sh pr 5 2>&1); dir="$w/app-pr5"
ok "an existing local branch is used as it is, never reset to origin" '[[ $(git -C "$dir" rev-list --count origin/claude/feature..HEAD) == 1 && $out == *"1 commit(s) ahead of origin"* ]]'
ok "checks out the PR's existing branch in its own worktree" '[[ -d $dir && $(git -C "$dir" rev-parse --abbrev-ref HEAD) == claude/feature ]]'
ok "the branch tracks origin, so a push updates the PR" '[[ $(git -C "$dir" rev-parse --abbrev-ref @{u}) == origin/claude/feature ]]'
out=$(scripts/ai/worktree.sh pr 5 2>&1)
ok "no stray ios.local.env.tmp is left behind" '[[ ! -e $dir/.claude/ios.local.env.tmp ]]'
ok "a second call reuses it (steer, don't respawn)" '[[ $out == *"existing, PR #5"* ]]'
out=$(scripts/ai/worktree.sh pr 9 2>&1)
ok "a PR that is not open is refused" '[[ $out == *"not open"* ]]'
out=$(scripts/ai/worktree.sh new topic 2>&1)
ok "new uses the claude/ prefix" '[[ $(git -C "$w/app-topic" rev-parse --abbrev-ref HEAD) == claude/topic ]]'
echo "worktree.sh prune"
out=$(PR_STATE=OPEN scripts/ai/worktree.sh prune 2>&1)
ok "an open PR's worktree is kept" '[[ -d $dir && $out == *"removed 0"* ]]'
echo dirty >> "$dir/f.txt"; out=$(PR_STATE=MERGED scripts/ai/worktree.sh prune 2>&1)
ok "a merged PR's worktree with uncommitted work is kept, and says why" '[[ -d $dir && $out == *"uncommitted or untracked"* ]]'
git -C "$dir" checkout -q f.txt; echo scratch > "$dir/notes.txt"; out=$(PR_STATE=MERGED scripts/ai/worktree.sh prune 2>&1)
ok "an untracked file keeps it too (git would refuse the removal)" '[[ -d $dir && $out == *"untracked"* ]]'
rm "$dir/notes.txt"; git -C "$dir" push -q origin claude/feature 2>/dev/null; out=$(PR_STATE=MERGED scripts/ai/worktree.sh prune 2>&1)
ok "a merged PR's clean worktree is removed" '[[ ! -d $dir && $out == *"removed 1"* ]]'
echo "$pass passed, $fail failed"; exit $fail
