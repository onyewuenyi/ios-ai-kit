#!/usr/bin/env python3
"""prs.py's classifier and digest on recorded PR shapes: every bucket, done-once, quiet mode."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

AI = Path(__file__).resolve().parent.parent / "template/scripts/ai"
sys.path.insert(0, str(AI))
spec = importlib.util.spec_from_file_location("prs", AI / "prs.py")
prs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prs)

NOW = time.time()
iso = lambda days_ago: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(NOW - days_ago * 86400))
SWIFT = [{"path": "App/Views/Home.swift"}]
DOCS = [{"path": "docs/guide.md"}]


def pr(**kw):
    base = {"number": 1, "title": "t", "url": "u", "headRefName": "claude/x", "headRefOid": "a" * 40,
            "baseRefName": "main", "isDraft": False, "mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN",
            "reviewDecision": "", "reviewRequests": [], "statusCheckRollup": [], "labels": [], "body": "",
            "commits": [], "files": SWIFT, "updatedAt": iso(0.1)}
    base.update(kw)
    return base


def ctx(**kw):
    base = {"now": NOW, "stale_days": 3, "me": "owner", "lead": {}, "threads": 0, "verified": True,
            "unpushed": 0, "cloud_authored": False}
    base.update(kw)
    return base


CASES = [
    ("verified, green, mergeable → merge-ready", pr(), ctx(), ("needs-you", "merge-ready")),
    ("docs-only needs no verify → merge-ready", pr(files=DOCS), ctx(verified=False), ("needs-you", "merge-ready")),
    ("files unknown (old gh) → must verify", pr(files=None), ctx(verified=False), ("needs-work", "verify")),
    ("app code unverified → verify", pr(), ctx(verified=False), ("needs-work", "verify")),
    ("cloud-authored unverified says so", pr(), ctx(verified=False, cloud_authored=True), ("needs-work", "verify")),
    ("conflicts → resolve", pr(mergeable="CONFLICTING"), ctx(), ("needs-work", "resolve")),
    ("DIRTY state → resolve", pr(mergeStateStatus="DIRTY"), ctx(), ("needs-work", "resolve")),
    ("failing CheckRun → fix-checks", pr(statusCheckRollup=[{"status": "COMPLETED", "conclusion": "FAILURE"}]), ctx(),
     ("needs-work", "fix-checks")),
    ("failing StatusContext → fix-checks", pr(statusCheckRollup=[{"state": "ERROR"}]), ctx(), ("needs-work", "fix-checks")),
    ("pending check → healthy", pr(statusCheckRollup=[{"status": "IN_PROGRESS", "conclusion": ""}]), ctx(),
     ("healthy", "")),
    ("pending status → healthy", pr(statusCheckRollup=[{"state": "PENDING"}]), ctx(), ("healthy", "")),
    ("green checks still merge-ready", pr(statusCheckRollup=[{"status": "COMPLETED", "conclusion": "SUCCESS"}]), ctx(),
     ("needs-you", "merge-ready")),
    ("changes requested → address-threads", pr(reviewDecision="CHANGES_REQUESTED"), ctx(), ("needs-work", "address-threads")),
    ("unresolved threads → address-threads", pr(), ctx(threads=2), ("needs-work", "address-threads")),
    ("required up-to-date and behind → update-branch", pr(mergeStateStatus="BEHIND"), ctx(), ("needs-work", "update-branch")),
    ("mergeability computing → healthy", pr(mergeable="UNKNOWN"), ctx(), ("healthy", "")),
    ("review requested from me → review", pr(reviewRequests=[{"login": "owner"}]), ctx(), ("needs-you", "review")),
    ("review requested from someone else → not mine", pr(reviewRequests=[{"login": "other"}]), ctx(),
     ("needs-you", "merge-ready")),
    ("fresh draft → healthy", pr(isDraft=True), ctx(), ("healthy", "")),
    ("older draft, verified → healthy, never merge-ready", pr(isDraft=True, updatedAt=iso(2)), ctx(), ("healthy", "")),
    ("idle past stale days → abandon-or-take-back", pr(updatedAt=iso(5)), ctx(), ("needs-you", "abandon-or-take-back")),
    ("stale wins over conflicts", pr(updatedAt=iso(5), mergeable="CONFLICTING"), ctx(), ("needs-you", "abandon-or-take-back")),
    ("unpushed local fix → push-ready", pr(mergeable="CONFLICTING"), ctx(unpushed=2), ("needs-you", "push-ready")),
    ("abandoned → done", pr(), ctx(lead={"abandoned": [1]}), ("done", "abandoned")),
    ("taken back → skipped", pr(), ctx(lead={"taken_back": [1]}), ("skip", "")),
    ("ignored → skipped", pr(), ctx(lead={"ignored": [1]}), ("skip", "")),
]

passed = failed = 0


def check(name, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  ok   {name}")
    else:
        failed += 1
        print(f"  FAIL {name}: got {got}, want {want}")


for name, p, c, want in CASES:
    b, a, _ = prs.classify(p, c)
    check(name, (b, a), want)

# verified at an earlier commit: holds only while later commits touch no app code
V = "v" * 40
vrows = [{"ts": "1", "run_id": "r", "sha": V, "branch": "b", "dirty": "0", "gate": "build", "result": "PASS",
          "secs": "1", "summary": ""}]
later = pr(commits=[{"oid": V}, {"oid": "a" * 40}])
check("verified earlier, later commits only docs/scripts → still verified",
      prs.verified_at(later, vrows, lambda a, b: ["scripts/ai/pr.sh", "docs/x.md"]), (V, True))
check("verified earlier, a later commit changes Swift → not verified",
      prs.verified_at(later, vrows, lambda a, b: ["App/Home.swift"]), (V, False))
check("verified earlier, but git cannot tell → not verified",
      prs.verified_at(later, vrows, lambda a, b: None), (V, False))
check("never verified → not verified", prs.verified_at(pr(commits=[{"oid": "c" * 40}]), vrows), (None, False))
b, a, why = prs.classify(pr(), ctx(verified=True, verified_sha=V))
check("its reason says why it still counts", "later commits touch no app code" in why, True)

# session links: in the body or a commit trailer
check("session link from the body", prs.session_link(pr(body="see https://claude.ai/code/session_01ABC")),
      "https://claude.ai/code/session_01ABC")
check("session link from a Claude-Session trailer",
      prs.session_link(pr(commits=[{"messageBody": "x\n\nClaude-Session: https://claude.ai/code/session_09Z"}])),
      "https://claude.ai/code/session_09Z")

# the digest: done reported once, no-PR cloud tasks, quiet mode
data = {"prs": [pr(number=5), pr(number=6, files=DOCS, updatedAt=iso(9))], "me": "owner", "threads": {},
        "closed": [{"number": 4, "title": "old", "state": "MERGED", "url": "u4", "headRefName": "claude/old",
                    "body": "", "updatedAt": iso(0.2)}]}
cloud = [{"ts": NOW - 10 * 3600, "slug": "s", "branch": "claude/never", "url": "https://claude.ai/code/session_X",
          "task": "write the docs"},
         {"ts": NOW - 1 * 3600, "slug": "s2", "branch": "claude/new", "url": "https://claude.ai/code/session_Y",
          "task": "fresh"}]
rows = [{"ts": "1", "run_id": "r", "sha": "a" * 40, "branch": "claude/x", "dirty": "0", "gate": "build",
         "result": "PASS", "secs": "1", "summary": ""}]
d = prs.digest(data, {}, {}, rows, cloud, {}, NOW)
by = {(i["number"], i["action"]) for i in d["items"]}
check("digest: verified PR is merge-ready", (5, "merge-ready") in by, True)
check("digest: idle PR is stalled", (6, "abandon-or-take-back") in by, True)
check("digest: merged since last look is done", (4, "merged") in by, True)
check("digest: cloud task with no PR after 6h → no-pr", (None, "no-pr") in by, True)
check("digest: a fresh cloud task is not flagged", sum(1 for i in d["items"] if i["action"] == "no-pr"), 1)
d2 = prs.digest(data, {}, {"reported_done": [4], "seen_at": NOW - 3600}, rows, cloud, {}, NOW)
check("digest: done is reported once", any(i["number"] == 4 for i in d2["items"]), False)

# the CLI on a recorded fixture: quiet after --mark-seen, loud again when something changes
repo = tempfile.mkdtemp()
subprocess.run(["git", "init", "-q", repo], check=True)
fx = Path(repo) / "fx.json"
fx.write_text(json.dumps(data))
run = lambda *a: subprocess.run([sys.executable, str(AI / "prs.py"), "--from", str(fx), *a], cwd=repo,
                                capture_output=True, text=True).stdout
check("cli prints the digest", "Needs you" in run(), True)
run("--mark-seen")
check("cli --quiet is silent when nothing changed", run("--quiet").strip(), "")
data["closed"].append({"number": 7, "title": "landed", "state": "MERGED", "url": "u7", "headRefName": "claude/l",
                       "body": "", "updatedAt": iso(-0.01)})  # merged after the last look
fx.write_text(json.dumps(data))
check("cli --quiet speaks once when a PR merges", "#7 merged" in run("--quiet", "--mark-seen"), True)
check("…and is silent again after", run("--quiet").strip(), "")
data["prs"][0]["mergeable"] = "CONFLICTING"
fx.write_text(json.dumps(data))
check("cli --quiet speaks when something changed", "resolve" in run("--quiet"), True)
check("cli caches prs.json for the bearings", (Path(repo) / ".git/ios-ai/prs.json").exists(), True)
out = subprocess.run([sys.executable, str(AI / "prs.py"), "--abandon", "6"], cwd=repo, capture_output=True, text=True).stdout
check("--abandon records it and names gh pr close", "gh pr close 6" in out, True)
env = {**os.environ, "PATH": "/nonexistent"}
out = subprocess.run([sys.executable, str(AI / "prs.py")], cwd=repo, capture_output=True, text=True, env=env)
check("no gh: one line, exit 0", (out.returncode, out.stdout.count("\n")), (0, 1))
print(f"{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
