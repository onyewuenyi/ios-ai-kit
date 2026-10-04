#!/usr/bin/env python3
"""List and digest this repo's Claude Code sessions, for /recall, /automate-me, /reflect and
/show-me-your-work. Reads ~/.claude/projects/<repo path with every non-alphanumeric as ->/*.jsonl
(and the repo's worktrees), keeps only sessions whose cwd is this repo or one of its worktrees, and
never reads another project's transcripts.

usage:
  sessions.py list [--since 7d] [--grep TEXT] [--all]   newest first: mtime, id, turns, first prompt
  sessions.py find "<opening words of a prompt>"        the session whose first prompt starts so
  sessions.py digest <id> [--grep TEXT]                  user turns, skills, tool calls, one line each
  sessions.py path <id>                                  the transcript's absolute path
--all keeps subagent transcripts in `list`; by default they are skipped as noise.
"""
from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True


def repo_root() -> Path | None:
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        return Path(out.stdout.strip()).resolve()
    except (OSError, subprocess.CalledProcessError):
        return None


def mangle(p: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(p))


def base() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "projects"


def candidates(root: Path, subagents: bool) -> list[Path]:
    name = mangle(root)
    files = []
    for d in base().glob(name + "*"):
        if d.name != name and not d.name.startswith(name + "-"):
            continue
        files += d.glob("*.jsonl")
        if subagents:
            files += d.glob("*/subagents/*.jsonl")
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def events(path: Path):
    with path.open(errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if isinstance(d, dict):
                yield d


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
    return ""


COMMAND = re.compile(r"<command-name>(.*?)</command-name>.*?(?:<command-args>(.*?)</command-args>|$)", re.S)


def prompt_text(d: dict) -> str:
    """A person's prompt as one line, with a slash command shown as `/name args`; "" for anything else."""
    if d.get("type") != "user" or d.get("isMeta"):
        return ""
    t = text_of((d.get("message") or {}).get("content")).strip()
    if not t or t.startswith(("<local-command", "<system-reminder", "Caveat:", "<task-notification")):
        return ""
    m = COMMAND.search(t)
    if m:
        t = f"{m.group(1).strip()} {(m.group(2) or '').strip()}"
    return " ".join(t.split())


def is_prompt(d: dict) -> bool:
    return bool(prompt_text(d))


def worktrees(root: Path) -> list[Path]:
    try:
        out = subprocess.run(["git", "-C", str(root), "worktree", "list", "--porcelain"],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return [root]
    return [Path(line[9:]).resolve() for line in out.splitlines() if line.startswith("worktree ")] or [root]


def belongs(cwd: str, root: Path, trees: list[Path]) -> bool:
    """This repo, one of its live worktrees, or a removed worktree (<repo>-<name> that no longer
    exists). A live sibling repo whose name extends this one is never read."""
    c = Path(cwd).resolve()
    if any(c == t or str(c).startswith(str(t) + "/") for t in trees):
        return True
    sibling = str(root.parent / root.name) + "-"
    return str(c).startswith(sibling) and not Path(str(c)[: len(sibling)] + str(c)[len(sibling):].split("/")[0]).exists()


def summary(path: Path, root: Path, trees: list[Path]) -> dict | None:
    first, turns, cwd = "", 0, ""
    for d in events(path):
        if not cwd and isinstance(d.get("cwd"), str):
            cwd = d["cwd"]
        t = prompt_text(d)
        if t:
            turns += 1
            if not first and (not t.startswith("/") or " " in t):
                first = t
    if cwd and not belongs(cwd, root, trees):
        return None
    return {"id": path.stem, "path": str(path), "mtime": path.stat().st_mtime, "turns": turns,
            "cwd": cwd, "first": first}


def since(arg: str) -> float:
    m = re.fullmatch(r"(\d+)([dh])", arg)
    return time.time() - (int(m.group(1)) * (86400 if m.group(2) == "d" else 3600) if m else 7 * 86400)


def opt(args: list[str], flag: str, default: str | None = None) -> str | None:
    return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else default


def locate(root: Path, sid: str) -> Path | None:
    for p in candidates(root, subagents=True):
        if p.stem == sid:
            return p
    return None


def digest(path: Path, grep: str | None) -> None:
    n = 0
    for d in events(path):
        t, msg = d.get("type"), d.get("message") or {}
        ts = str(d.get("timestamp", ""))[:16]
        body = prompt_text(d)
        if body:
            n += 1
            if not grep or grep.lower() in body.lower():
                print(f"{ts} U{n}: {body[:400]}")
        elif t == "assistant" and isinstance(msg.get("content"), list):
            for b in msg["content"]:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text" and not grep:
                    line = " ".join(b.get("text", "").split())
                    if line:
                        print(f"{ts}   A: {line[:240]}")
                if b.get("type") == "tool_use":
                    inp = b.get("input") or {}
                    what = (inp.get("skill") or inp.get("command") or inp.get("file_path") or inp.get("pattern")
                            or inp.get("description") or inp.get("subagent_type") or "")
                    line = f"{b.get('name')}: {' '.join(str(what).split())}"
                    if not grep or grep.lower() in line.lower():
                        print(f"{ts}   T {line[:240]}")
        elif t == "system" and d.get("subtype") == "compact_boundary":
            print(f"{ts}   -- compacted here; detail before this point is summarized --")


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] not in ("list", "find", "digest", "path"):
        print(__doc__.strip())
        return 2
    cmd, args, root = argv[1], argv[2:], repo_root()
    if root is None:
        print("sessions: run this inside a git repository; it reads only that repo's sessions", file=sys.stderr)
        return 2
    trees = worktrees(root)
    if cmd == "list":
        cutoff, grep = since(opt(args, "--since", "7d")), opt(args, "--grep")
        for p in candidates(root, subagents="--all" in args):
            if p.stat().st_mtime < cutoff:
                break
            if grep and grep.lower() not in p.read_text(errors="replace").lower():
                continue
            s = summary(p, root, trees)
            if s and s["turns"]:
                stamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(s["mtime"]))
                print(f"{stamp}  {s['id']}  {s['turns']:>3} turns  {s['first'][:100]}")
        return 0
    if cmd == "find":
        want = " ".join(" ".join(args).split()).lower()
        for p in candidates(root, subagents=True):
            s = summary(p, root, trees)
            if s and want and s["first"].lower().startswith(want[:200]):
                print(s["path"])
                return 0
        print("sessions: no session of this repo opens with that prompt", file=sys.stderr)
        return 1
    if not args:
        print("sessions: give a session id", file=sys.stderr)
        return 2
    p = locate(root, args[0])
    if p is None or summary(p, root, trees) is None:
        print(f"sessions: no transcript {args[0]} for this repo", file=sys.stderr)
        return 1
    if cmd == "path":
        print(p)
    else:
        digest(p, opt(args, "--grep"))
    return 0


if __name__ == "__main__":
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    sys.exit(main(sys.argv))
