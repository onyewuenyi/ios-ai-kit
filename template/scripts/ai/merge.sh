#!/usr/bin/env bash
# Land one pull request, only once it is proven. The last step of /ship.
#
# Merges PR <n> only when the digest calls it merge-ready (`prs.py --check`): verified at its exact head
# commit by /verify with the visual sheets judged, mergeable, checks green, no open review threads.
# While checks run or GitHub is still computing mergeability it waits (up to --wait seconds); anything
# else (a failing check, a conflict, a thread, an unverified head) stops it with the reason, and the
# fix belongs to the work, never to this script. Refused in cloud sessions: a Mac verifies, a Mac merges.
#   --yes            required: the person asked for this PR to land (/ship passes it)
#   --wait <secs>    how long to wait for checks and mergeability (default 600)
# After the merge: the remote branch is deleted, the local default branch fast-forwards, the merged
# local branch is removed when it is safe (git branch -d), and merged PR worktrees are pruned.
# usage: merge.sh <n> --yes [--wait <secs>]
source "$(dirname "$0")/lib.sh"
set +e -uo pipefail
n=""; yes=0; wait_s=600
while (( $# )); do case $1 in
  --yes) yes=1 ;; --wait) wait_s=${2:-600}; shift ;;
  -*) echo "usage: merge.sh <n> --yes [--wait <secs>]"; exit 2 ;; *) n=$1 ;; esac; shift; done
die() { echo "merge: $*"; exit 1; }
[[ $n =~ ^[0-9]+$ ]] || die "which pull request? merge.sh <n> --yes"
[[ ${CLAUDE_CODE_REMOTE:-} == true ]] && die "cloud sessions never merge; a Mac verifies and merges"
(( yes )) || die "add --yes to confirm the person asked for #$n to land"
command -v gh >/dev/null || die "needs the GitHub CLI: brew install gh && gh auth login"
cd "$AI_ROOT" || exit 1
waited=0
while :; do
  verdict=$(python3 "$AI_DIR/prs.py" --check "$n" 2>/dev/null); rc=$?
  action=$(printf '%s' "$verdict" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("action","") or d.get("bucket",""))' 2>/dev/null)
  why=$(printf '%s' "$verdict" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("why",""))' 2>/dev/null)
  (( rc == 0 )) && break
  if [[ $action == healthy && $waited -lt $wait_s ]]; then
    (( waited == 0 )) && echo "merge: #$n is not ready yet ($why); waiting up to ${wait_s}s"
    sleep 15; waited=$((waited + 15)); continue
  fi
  die "#$n is not merge-ready: ${action:-unknown}: ${why:-no verdict}. Fix that, then run merge.sh again."
done
head=$(gh pr view "$n" --json headRefName -q .headRefName 2>/dev/null)
base=$(gh pr view "$n" --json baseRefName -q .baseRefName 2>/dev/null)
out=$(gh pr merge "$n" "--${MERGE_METHOD:-merge}" --delete-branch 2>&1)
[[ $(gh pr view "$n" --json state -q .state 2>/dev/null) == MERGED ]] || die "GitHub did not merge #$n: $out"
echo "merge: #$n merged into $base ($why)"
git fetch -q origin 2>/dev/null
if [[ $(git rev-parse --abbrev-ref HEAD) == "$head" ]]; then git switch -q "$base" 2>/dev/null; fi
if [[ $(git rev-parse --abbrev-ref HEAD) == "$base" ]]; then git merge -q --ff-only "origin/$base" 2>/dev/null && echo "merge: local $base is at origin/$base"; fi
git show-ref -q --verify "refs/heads/$head" && git branch -q -d "$head" 2>/dev/null && echo "merge: removed the merged local branch $head"
"$AI_DIR/worktree.sh" prune 2>/dev/null | grep -v "removed 0" || true
exit 0
