#!/usr/bin/env python3
"""friction.py on synthetic transcripts shaped like real Claude Code records: each kind fires at its
threshold and not below, a clean week is silent, covered rules suppress, and a changed format is
named instead of guessed at."""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

AI = Path(__file__).resolve().parent.parent / "template/scripts/ai"
sys.path.insert(0, str(AI))
sys.dont_write_bytecode = True
import friction  # noqa: E402

passed = failed = 0
NOW = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())


def check(name, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  ok   {name}")
    else:
        failed += 1
        print(f"  FAIL {name}: got {got}, want {want}")


def use(i, name, **inp):
    return {"type": "assistant", "timestamp": NOW, "message": {"usage": {"output_tokens": 100},
            "content": [{"type": "tool_use", "id": f"t{i}", "name": name, "input": inp}]}}


def result(i, text, err=False):
    return {"type": "user", "timestamp": NOW, "message": {"content": [
        {"type": "tool_result", "tool_use_id": f"t{i}", "content": text, "is_error": err}]}}


def session(d: Path, sid: str, records: list) -> None:
    (d / f"{sid}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))


def run(d: Path, repo: Path, *extra) -> str:
    return subprocess.run([sys.executable, str(AI / "friction.py"), "--transcripts", str(d), *extra], cwd=repo,
                          capture_output=True, text=True).stdout


repo = Path(tempfile.mkdtemp())
subprocess.run(["git", "init", "-q", str(repo)], check=True)
(repo / ".claude").mkdir()
(repo / ".claude/settings.json").write_text(json.dumps({"permissions": {"allow": ["Bash(git log:*)"]}}))

d = Path(tempfile.mkdtemp())
session(d, "clean", [use(1, "Bash", command="scripts/ai/build.sh"), result(1, "build: succeeded")])
check("a clean week is silent", run(d, repo, "--since", "7d").strip(), "")
check("…and stamps friction.last", (repo / ".git/ios-ai/friction.last").exists(), True)

d = Path(tempfile.mkdtemp())
for sid in ("a", "b"):
    recs = []
    for i in range(3):
        recs += [use(i, "Bash", command="cd /x && git fetch origin"), result(i, "ok")]
        recs += [use(10 + i, "Bash", command="git log -3"), result(10 + i, "ok")]
    recs += [use(20, "Bash", command="cd app && gh pr merge 3"), result(20, "The user doesn't want to proceed with this tool use.", True)]
    for i in range(2):
        recs += [use(30 + i, "Bash", command="git push origin main"),
                 result(30 + i, "PreToolUse:Bash hook error: Every change reaches 'main' through a pull request", True)]
    recs += [use(40, "Bash", command="scripts/ai/build.sh"),
             result(40, "error App/Home.swift:12: cannot find 'Palette' in scope\nbuild: failed")]
    recs += [{"type": "user", "timestamp": NOW, "message": {"content": "Stop hook feedback:\nios-ai stop check FAILED on this change"}}] * 2
    recs += [use(50, "Read", file_path="/r/Big.swift")] * 6
    recs += [use(60, "Bash", command="cat huge.log"), result(60, "x" * 25000)]
    recs += [{"type": "system", "subtype": "compact_boundary", "timestamp": NOW}]
    session(d, sid, recs)
out = json.loads(run(d, repo, "--json", "--waste"))
kinds = [p["kind"] for p in out["proposals"]]
ev = " | ".join(p["evidence"] for p in out["proposals"])
check("allow: a read-only subcommand in 2+ sessions, 5+ times", "`git fetch …` ran 6 times in 2 sessions" in ev, True)
check("allow: a command an allow rule covers is not proposed", "git log" not in ev, True)
check("rejected: named by the real command, not the cd before it", "rejected 2 times: Bash: gh pr" in ev, True)
check("guard: the same refusal 3+ times", any(k == "guard" for k in kinds) and "4 refusals" in ev, True)
check("stop: the Stop hook's build check failing 3+ turns", "failed 4 turns" in ev, True)
check("build-error: the same error in 2+ sessions, line numbers stripped", "cannot find _ in scope" in ev, True)
check("waste: oversized outputs", "tool outputs over 20k characters from `cat`" in ev, True)
check("waste: a file re-read in one session", "Big.swift read 6 times" in ev, True)
check("waste: compactions and output tokens", "2 compaction(s)" in ev, True)
out2 = json.loads(run(d, repo, "--json"))
check("waste is only reported with --waste (or on Mondays)",
      any(p["kind"] == "waste" for p in out2["proposals"]), time.localtime().tm_wday == 0)

d = Path(tempfile.mkdtemp())
session(d, "one", [use(i, "Bash", command="git fetch") for i in range(9)])
check("allow: one session is not a pattern", run(d, repo).strip(), "")

hist = repo / ".git/ios-ai/verify.tsv"
rows = []
for k, fails in enumerate([["T/a()"], [], ["T/a()"]]):
    rows.append(f"{k}\tr{k}\tSHA\tb\t0\ttests\t{'FAIL' if fails else 'PASS'}\t30\tx")
    rows += [f"{k}\tr{k}\tSHA\tb\t0\tfail:{t}\tFAIL\t0\tboom" for t in fails]
for k in range(12):
    rows.append(f"{100 + k}\ts{k}\tS{k}\tb\t0\tbuild\tPASS\t{40 if k < 6 else 100}\tok")
hist.write_text("\n".join(rows) + "\n")
d = Path(tempfile.mkdtemp())
session(d, "x", [])
ev = run(d, repo)
check("flaky: failed and passed on the same commit", "T/a() failed and passed on the same commit" in ev, True)
check("slow-gate: a gate's median grew by half and past a minute", "build median 40s → 100s" in ev, True)

d = Path(tempfile.mkdtemp())
(d / "s.jsonl").write_text("not json\n" * 8 + json.dumps({"type": "user"}) + "\n")
check("a changed transcript format is named, nothing is guessed", "format changed" in run(d, repo), True)
check("mangling matches Claude Code's project directories",
      friction.mangle(Path("/Users/me/Projects/My App")), "-Users-me-Projects-My-App")
print(f"{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
