#!/usr/bin/env python3
"""The AI judge: a separate Claude call looks at every visual sheet /verify captured and says what it saw.

The model only judges; this script decides. It sends the sheets (each one screen at default, dark
and the largest text size, side by side) and the intended change to `claude -p` with a JSON
schema, then validates the answer: one verdict per sheet it was shown, PASS or FAIL, each with an
observation. Anything else is no verdict, and the gate stays JUDGE. A valid answer is recorded with
`history.py judge`, so the commit counts as verified only after a PASS.

usage: judge.py [--intent "what this change should make visible"] [--sheets visual.txt] [--dry-run]
  --intent    defaults to $VERIFY_INTENT, else this branch's commit subjects
  --dry-run   print the prompt; call nothing, record nothing
Exit: 0 PASS · 1 FAIL (an observed defect) · 3 no verdict (no claude, no sheets, an invalid answer).
Model: JUDGE_MODEL, else MODEL_JUDGMENT, from .claude/ios.env (empty = Claude Code's default).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # never leave __pycache__ in the project's scripts/ai
sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit import env, git, repo_root  # noqa: E402

SCHEMA = {
    "type": "object",
    "properties": {"screens": {"type": "array", "items": {
        "type": "object",
        "properties": {"name": {"type": "string"}, "verdict": {"type": "string", "enum": ["PASS", "FAIL"]},
                       "evidence": {"type": "string"}},
        "required": ["name", "verdict", "evidence"]}}},
    "required": ["screens"],
}

CHECKLIST = """Judge each sheet the way a careful iOS reviewer would. FAIL a screen only for a defect a person would
hit. FAIL when you see:
- text clipped so it cannot be read anywhere: the screen's subject or a name cut mid-word, text running
  off an edge, or a title truncated at the LARGEST size where the layout should wrap it;
- elements drawn on top of each other in a way no scroll resolves, or a control that cannot be reached;
- unreadable contrast in the dark column, or a light-only color left in dark mode;
- a blank or broken area where content, an empty state, a loading state or an error should be;
- the intended change below NOT visible on a screen it should affect.
Do NOT fail for platform conventions: a list row whose long title ends in an ellipsis on one line at the
default size; content scrolled partly under a floating button, a tab bar, the home indicator or the
bottom edge; a section cut off at the bottom of a scrollable screen. A design choice you would make
differently is not a FAIL. The app's own conventions, if any, follow and win over this list."""


def sheets(path: Path) -> list[Path]:
    try:
        return [Path(l[6:].strip()) for l in path.read_text().splitlines() if l.startswith("JUDGE ")]
    except OSError:
        return []


def default_intent(root: Path) -> str:
    base = git("merge-base", "HEAD", "origin/HEAD", cwd=root)
    subjects = git("log", "--format=- %s", f"{base}..HEAD", cwd=root) if base else ""
    return subjects or "(no stated intent: judge the screens on the checklist alone)"


def notes(root: Path) -> str:
    try:
        text = (root / ".claude/judge-notes.md").read_text()
    except OSError:
        return ""
    lines = [l for l in text.splitlines() if l.strip() and not l.lstrip().startswith("<!--")]
    return "\n".join(lines).strip()


def prompt(paths: list[Path], intent: str, conventions: str = "") -> str:
    listing = "\n".join(f"- {p.stem}: {p}" for p in paths)
    return (f"You are the visual judge for an iOS app's verification gate. Read each image file below with "
            f"the Read tool. Each image is one screen captured three times side by side: default, dark, "
            f"and the largest accessibility text size (AX5), labelled under each column.\n\n"
            f"Sheets:\n{listing}\n\nIntended change:\n{intent}\n\n{CHECKLIST}\n\n"
            + (f"This app's conventions (deliberate, not defects):\n{conventions}\n\n" if conventions else "") +
            f"Answer with one entry per sheet: name (exactly the name before the colon above), verdict, and "
            f"evidence (one sentence on what you actually saw, naming the column for a FAIL). Judge only what "
            f"is in the images.")


def validate(answer, names: list[str]) -> tuple[str, list[dict]] | None:
    """(overall, per-screen) when the answer covers exactly the sheets shown, else None."""
    try:
        screens = answer["screens"]
    except (TypeError, KeyError):
        return None
    by = {}
    for s in screens:
        if not isinstance(s, dict) or s.get("verdict") not in ("PASS", "FAIL") or not str(s.get("evidence", "")).strip():
            return None
        by[s.get("name")] = s
    if sorted(by) != sorted(names):
        return None
    ordered = [by[n] for n in names]
    return ("FAIL" if any(s["verdict"] == "FAIL" for s in ordered) else "PASS"), ordered


def main(argv: list[str]) -> int:
    args = argv[1:]
    root = repo_root()
    cfg = env(root)
    rep = root / ".build/verify"
    sheet_file = Path(args[args.index("--sheets") + 1]) if "--sheets" in args else rep / "visual.txt"
    paths = [p for p in sheets(sheet_file) if p.exists()]
    if not paths:
        print("judge: no sheets to judge (run /verify first; it lists them in .build/verify/visual.txt)")
        return 3
    intent = args[args.index("--intent") + 1] if "--intent" in args else (cfg.get("VERIFY_INTENT") or default_intent(root))
    text = prompt(paths, intent, notes(root))
    if "--dry-run" in args:
        print(text)
        return 0
    model = cfg.get("JUDGE_MODEL") or cfg.get("MODEL_JUDGMENT") or ""
    cmd = [cfg.get("CLAUDE_BIN") or "claude", "-p", text, "--output-format", "json", "--json-schema", json.dumps(SCHEMA),
           "--allowedTools", "Read", "--max-turns", str(len(paths) * 2 + 4)]
    if model:
        cmd += ["--model", model]
    child_env = {**os.environ, "IOS_AI_STOP_CHECK": "0"}  # the judge must not run the Stop hook's build
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, cwd=root, env=child_env)
    except FileNotFoundError:
        print("judge: Claude Code (`claude`) is not on PATH, so nothing was judged; the gate stays JUDGE")
        return 3
    except subprocess.TimeoutExpired:
        print("judge: the judge did not answer within 15 minutes; nothing was judged")
        return 3
    try:
        envelope = json.loads(r.stdout)
    except ValueError:
        print(f"judge: no answer from Claude ({(r.stderr or r.stdout).strip()[:200]}); nothing was judged")
        return 3
    result = validate(envelope.get("structured_output"), [p.stem for p in paths])
    if result is None:
        print("judge: the answer did not give one PASS or FAIL with evidence per sheet; nothing was judged")
        return 3
    overall, screens = result
    who = f"AI judge ({model or 'default model'})"
    lines = [f"{s['name']}: {s['verdict']}, {s['evidence'].strip()}" for s in screens]
    rep.mkdir(parents=True, exist_ok=True)
    (rep / "judge.json").write_text(json.dumps({"verdict": overall, "by": who, "intent": intent, "screens": screens}, indent=1))
    for l in lines:
        print(f"judge: {l}")
    summary = f"{who}. " + " | ".join(lines)
    rec = subprocess.run([sys.executable, str(Path(__file__).with_name("history.py")), "judge", overall, summary],
                         capture_output=True, text=True, cwd=root)
    print(rec.stdout.strip() or rec.stderr.strip())
    print(f"judge: {overall}")
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
