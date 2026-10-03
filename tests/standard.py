#!/usr/bin/env python3
"""The one-job standard, as a test: every agent and skill states its job, its anti-jobs and its
quiet answer; agents carry only the tools they need and none of the kit's agents can edit; and no
doc points at a script that does not exist, while no script exists that nothing uses."""
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
T = KIT / "template"
MARKERS = ("**Job:**", "**Not my job:**", "**When there is nothing to report:**")
EDITING = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
passed = failed = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global passed, failed
    if ok:
        passed += 1
        print(f"  ok   {name}")
    else:
        failed += 1
        print(f"  FAIL {name}{': ' + detail if detail else ''}")


def front(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if re.match(r"^[a-z-]+:", line):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm, m.group(2)


agents = sorted((T / ".claude/agents").glob("*.md"))
skills = sorted((T / ".claude/skills").glob("*/SKILL.md")) + sorted((KIT / "skills").glob("*/SKILL.md"))
for a in agents:
    fm, body = front(a)
    rel = a.relative_to(KIT)
    check(f"{rel}: name, description and tools", all(fm.get(k) for k in ("name", "description", "tools")),
          f"missing {[k for k in ('name', 'description', 'tools') if not fm.get(k)]}")
    tools = {t.strip() for t in fm.get("tools", "").split(",")}
    check(f"{rel}: cannot edit (read-only by design)", not (tools & EDITING), f"has {tools & EDITING}")
    missing = [m for m in MARKERS if m not in body]
    check(f"{rel}: job, anti-jobs, quiet answer", not missing, f"missing {missing}")
for s in skills:
    fm, body = front(s)
    rel = s.relative_to(KIT)
    check(f"{rel}: name and description", bool(fm.get("name") and fm.get("description")))
    check(f"{rel}: description under 600 characters", len(fm.get("description", "")) <= 600,
          f"{len(fm.get('description', ''))}")
    missing = [m for m in MARKERS if m not in body]
    check(f"{rel}: job, anti-jobs, quiet answer", not missing, f"missing {missing}")

# no dangling script references, no orphan scripts
docs = [*agents, *skills, *(T / ".claude/skills").glob("*/playbooks/*.md"), *(T / ".claude/skills").glob("*/*.md"),
        T / "CLAUDE.block.md", T / "docs/ai-workflow.md", KIT / "README.md"]
scripts = {p.name for p in (T / "scripts/ai").iterdir() if p.is_file()}
dangling = set()
for d in docs:
    for ref in re.findall(r"scripts/ai/([A-Za-z0-9_.-]+\.(?:sh|py|swift))", d.read_text()):
        if ref not in scripts:
            dangling.add(f"{d.relative_to(KIT)} → {ref}")
check("every referenced scripts/ai file exists", not dangling, ", ".join(sorted(dangling)))
corpus = "\n".join(p.read_text(errors="replace") for p in [*T.rglob("*"), KIT / "README.md", KIT / "install.py"]
                   if p.is_file() and p.suffix in (".md", ".sh", ".py", ".json", ".swift", ".txt"))
orphans = []
for name in sorted(scripts):
    stem = name.rsplit(".", 1)[0]
    others = corpus.replace(f"# usage: {name}", "")
    uses = len(re.findall(rf"\b{re.escape(name)}\b", others)) + len(re.findall(rf"\bimport {stem}\b|from {stem} import", others))
    if uses == 0:
        orphans.append(name)
check("every script in scripts/ai is used or documented somewhere", not orphans, ", ".join(orphans))

# the playbook router and its files agree
router = (T / ".claude/skills/ios-loop/SKILL.md").read_text()
files = {p.name for p in (T / ".claude/skills/ios-loop/playbooks").glob("*.md")}
named = set(re.findall(r"playbooks/([a-z0-9-]+\.md)", router))
check("every playbook file is in the ios-loop router", files <= named, f"not routed: {sorted(files - named)}")
check("every routed playbook exists", named <= files, f"missing: {sorted(named - files)}")
print(f"{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
