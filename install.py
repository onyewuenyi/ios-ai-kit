#!/usr/bin/env python3
"""Install (or upgrade) ios-ai-kit into an iOS repository.

usage: install.py <repo> [--scheme NAME] [--container PATH] [--dry-run]

Detects the project, writes .claude/ios.env, copies the kit's scripts, hooks, skills, agents and
rules, and MERGES into existing files instead of overwriting them:
  .claude/settings.json  permissions unioned, hooks appended unless an equivalent exists
                         (an existing swift-format hook is kept and ours skipped), worktree.baseRef set
  .claude/ios.env        created once; an upgrade appends only the keys it lacks
  .mcp.json              adds the `xcode` server if absent
  CLAUDE.md              the ios-ai-kit block between markers, replaced in place on upgrade
  docs/ai-workflow.md    the same: the kit's block is refreshed, the team's text around it kept
  .gitignore             adds the kit's local-only paths
Kit-owned files (scripts/ai/*, .claude/hooks/*, the kit's skills and agents, the Swift rule) are
replaced on every run: change them in ios-ai-kit, not here. Files a team edits (ios-screens.txt,
the PR template) are only created when missing. Idempotent: run it again to upgrade.
"""

from __future__ import annotations

import argparse
import hashlib
import time
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent / "template"
# Every kit skill and agent is kit-owned, derived from the template (never a hand-kept list: a list
# here drifted from the template twice). A repo's own skills and agents, with other names, are untouched.
KIT_OWNED = (["scripts/ai", ".claude/hooks", ".claude/rules/ios27-swift.md"]
             + sorted(f".claude/skills/{d.name}" for d in (KIT / ".claude/skills").iterdir() if d.is_dir())
             + sorted(f".claude/agents/{f.name}" for f in (KIT / ".claude/agents").glob("*.md")))
# Files an earlier kit version installed that a later one retired; an upgrade removes them.
RETIRED_FILES = [".claude/skills/ios-loop/playbooks/handoff.md", ".claude/skills/ios-loop/principles.md"]
CREATE_IF_MISSING = [".claude/ios-screens.txt", ".claude/judge-notes.md", ".github/pull_request_template.md"]
GITIGNORE = [".build/", "__pycache__/", ".claude/ios.local.env", "CLAUDE.local.md", ".claude/settings.local.json", ".claude/worktrees/"]
# Rules an earlier kit version wrote that were wrong; an upgrade removes them.
RETIRED_RULES = ["mcp__xcode__DeviceEventSynthesize", "mcp__xcode__XcodeListWindows",
                 "Write(**/*.pbxproj)"]  # file rules are Edit(...) only; Claude Code warns a Write rule never matches
BEGIN, END = "<!-- ios-ai-kit:begin", "<!-- ios-ai-kit:end -->"
log: list[str] = []


def run(*cmd: str, cwd: Path) -> str:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed: {(r.stderr or r.stdout).strip()[-400:]}")
    return r.stdout


def existing_env(repo: Path) -> dict[str, str]:
    vals = {}
    try:
        for line in (repo / ".claude/ios.env").read_text().splitlines():
            m = re.match(r"\s*([A-Z][A-Z0-9_]*)=(.*)", line)
            if m:
                vals[m.group(1)] = m.group(2).strip()
    except OSError:
        pass
    return vals


def detect(repo: Path, scheme: str | None, container: str | None) -> dict:
    # An existing .claude/ios.env is the team's word on scheme and container: a re-run must not
    # re-detect past it and leave the CLAUDE.md block disagreeing with it.
    env = existing_env(repo)
    explicit_scheme = scheme
    container = container or env.get("WORKSPACE") or env.get("PROJECT") or None
    scheme = scheme or env.get("SCHEME") or None
    if container:
        c = Path(container)
    else:
        ws = [p for p in repo.glob("*.xcworkspace")] + [p for p in repo.glob("*/*.xcworkspace") if ".xcodeproj" not in str(p)]
        pj = list(repo.glob("*.xcodeproj")) or list(repo.glob("*/*.xcodeproj"))
        cands = ws or pj
        if not cands:
            sys.exit(f"no .xcworkspace or .xcodeproj under {repo}; pass --container")
        c = sorted(cands, key=lambda p: (p.stem.lower() != repo.name.lower(), len(str(p))))[0]
    c = c if c.is_absolute() else repo / c
    kind = "-workspace" if c.suffix == ".xcworkspace" else "-project"
    lst = json.loads(run("xcodebuild", "-list", "-json", kind, str(c), cwd=repo))
    info = lst.get("workspace") or lst.get("project") or {}
    schemes = info.get("schemes", [])
    if not schemes:
        sys.exit("the project has no schemes: open it in Xcode once (or share a scheme), then re-run")
    if scheme and scheme not in schemes:
        if scheme == env.get("SCHEME") and scheme != explicit_scheme:
            log.append(f"warning  .claude/ios.env names scheme {scheme!r}, which the project does not have "
                       f"(available: {schemes}); detected one instead, fix ios.env if it is wrong")
            scheme = None
        else:
            sys.exit(f"scheme {scheme!r} not found; available: {schemes}")
    scheme = scheme or sorted(schemes, key=lambda s: (s.lower() != c.stem.lower(), "test" in s.lower(), s))[0]
    raw = run("xcodebuild", "-showBuildSettings", "-json", kind, str(c), "-scheme", scheme,
              "-destination", "generic/platform=iOS Simulator", cwd=repo)
    targets = json.loads(raw)
    app = next((t["buildSettings"] for t in targets if t["buildSettings"].get("WRAPPER_EXTENSION") == "app"), None)
    if app is None:
        sys.exit(f"scheme {scheme!r} builds no iOS app target")
    pbx = [repo / p for p in ([str(c.relative_to(repo))] if kind == "-project" else [])] or list(repo.glob("**/*.xcodeproj"))
    synced = any("PBXFileSystemSynchronizedRootGroup" in (p / "project.pbxproj").read_text(errors="replace")
                 for p in pbx if (p / "project.pbxproj").exists())
    product = app.get("PRODUCT_NAME", scheme)
    src = [d for d in (product, scheme, c.stem) if (repo / d).is_dir()]
    claude_md = (repo / "CLAUDE.md").read_text(errors="replace") if (repo / "CLAUDE.md").exists() else ""
    return {
        "kind": kind, "container": str(c.relative_to(repo)), "scheme": scheme,
        "bundle": app.get("PRODUCT_BUNDLE_IDENTIFIER", ""), "deployment": app.get("IPHONEOS_DEPLOYMENT_TARGET", ""),
        "synced": synced, "source_dirs": " ".join(dict.fromkeys(src)) or ".",
        "serial_tests": "-parallel-testing-enabled NO" in claude_md,
    }


def write(path: Path, text: str, dry: bool, what: str) -> None:
    log.append(f"{what:8} {path.name if path.parent.name in ('', '.') else path}")
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def copy_tree(rel: str, repo: Path, dry: bool, overwrite: bool) -> None:
    src = KIT / rel
    files = [src] if src.is_file() else [p for p in src.rglob("*")
                                         if p.is_file() and "__pycache__" not in p.parts and p.name != ".DS_Store"]
    for f in files:
        dst = repo / f.relative_to(KIT)
        if dst.exists() and not overwrite:
            log.append(f"kept     {dst.relative_to(repo)}")
            continue
        same = dst.exists() and dst.read_bytes() == f.read_bytes()
        log.append(f"{'same' if same else ('updated' if dst.exists() else 'added'):8} {dst.relative_to(repo)}")
        if not dry and not same:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)


def merge_settings(repo: Path, dry: bool) -> None:
    path = repo / ".claude/settings.json"
    ours = json.loads((KIT / ".claude/settings.json").read_text())
    cur = json.loads(path.read_text()) if path.exists() else {}
    perms = cur.setdefault("permissions", {})
    # A rule the team deleted stays deleted: only rules NEW to the kit since the last install are
    # added. The kit's rule set as last installed is remembered in .claude/ios-kit.json.
    memo_path = repo / ".claude/ios-kit.json"
    try:
        memo = json.loads(memo_path.read_text())
    except (OSError, ValueError):
        memo = {}
    seen = set(memo.get("rules", []))
    for k in ("allow", "ask", "deny"):
        have = perms.setdefault(k, [])
        have[:] = [r for r in have if r not in RETIRED_RULES]
        for r in ours["permissions"][k]:
            if r in have:
                continue
            if r in seen and seen:
                log.append(f"warning  settings.json: {r} is a kit rule you removed; left out")
                continue
            have.append(r)
    all_rules = sorted({r for k in ("allow", "ask", "deny") for r in ours["permissions"][k]})
    if memo.get("rules") != all_rules:
        write(memo_path, json.dumps({"rules": all_rules}, indent=1) + "\n", dry, "merged" if memo_path.exists() else "added")
    cur.setdefault("worktree", {}).setdefault("baseRef", "head")
    hooks = cur.setdefault("hooks", {})
    existing_cmds = json.dumps(hooks)
    for event, groups in ours["hooks"].items():
        for g in groups:
            for h in g["hooks"]:
                script = h["command"].rsplit("/", 1)[-1].strip('"')
                if script == "format-swift.sh" and script not in existing_cmds and "swift-format" in existing_cmds:
                    log.append("skipped  format hook (the repo already formats Swift on edit)")
                    continue
                placed = False
                for grp in hooks.get(event, []):  # ours from an earlier install: replace it in place
                    for i, old_h in enumerate(grp.get("hooks", [])):
                        if old_h.get("type") == "command" and old_h.get("command", "").rsplit("/", 1)[-1].strip('"') == script:
                            if old_h != h or grp.get("matcher") != g.get("matcher"):
                                grp["hooks"][i] = dict(h)
                                if "matcher" in g:
                                    grp["matcher"] = g["matcher"]
                            placed = True
                if not placed:
                    hooks.setdefault(event, []).append({**({"matcher": g["matcher"]} if "matcher" in g else {}), "hooks": [h]})
    text = json.dumps(cur, indent=2) + "\n"
    if path.exists() and path.read_text() == text:
        log.append("same     .claude/settings.json")
    else:
        write(path, text, dry, "merged" if path.exists() else "added")


def merge_mcp(repo: Path, dry: bool) -> None:
    path = repo / ".mcp.json"
    cur = json.loads(path.read_text()) if path.exists() else {}
    servers = cur.setdefault("mcpServers", {})
    if "xcode" in servers:
        log.append("kept     .mcp.json (xcode server already registered)")
        return
    servers["xcode"] = json.loads((KIT / ".mcp.json").read_text())["mcpServers"]["xcode"]
    write(path, json.dumps(cur, indent=2) + "\n", dry, "merged" if path.exists() else "added")


# docs/ai-workflow.md as earlier kit versions wrote it, unedited: safe to replace whole on upgrade.
KNOWN_DOC_VERSIONS = {
    "a52b1fc3360f30ae25549197ac1e9b5757eda3f2339d84375236c678917a5336",
    "cf8e1a0e847455757ff90a7dff07c4518cc6dfb5bc2f71f4ffa17160994c25e8",
    "b783343d5f00e70e172a4a85bde65507df6da30c8ce1e7e141c10bb5cd76fcd8",
}


def merge_block(path: Path, block: str, fresh: str, dry: bool, label: str, known: set[str] = frozenset()) -> None:
    """The kit's block between BEGIN/END markers, replaced in place; text outside it is the team's.
    A file without markers that is byte-for-byte an earlier kit version is replaced whole; one that
    was edited is left alone and named."""
    if not path.exists():
        write(path, fresh, dry, "added")
        return
    cur = path.read_text()
    if BEGIN in cur:
        new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", lambda _: block, cur, flags=re.S)
    elif hashlib.sha256(cur.encode()).hexdigest() in known:
        new = fresh
    elif known:
        log.append(f"kept     {label} (edited, and has no kit markers: wrap the kit's part in {BEGIN} … {END} to let upgrades refresh it)")
        return
    else:
        new = cur.rstrip() + "\n\n" + block
    if new == cur:
        log.append(f"same     {label}")
    else:
        write(path, new, dry, "merged")


def merge_claude_md(repo: Path, d: dict, dry: bool) -> None:
    block = (KIT / "CLAUDE.block.md").read_text()
    style = ("synchronized folders (a new .swift file in the target's folder compiles automatically)" if d["synced"]
             else "explicit groups (add files through Xcode or the Xcode MCP; confirm target membership)")
    for k, v in {"CONTAINER": d["container"], "SCHEME": d["scheme"], "BUNDLE_ID": d["bundle"],
                 "DEPLOYMENT": d["deployment"], "FILE_STYLE": style}.items():
        block = block.replace("{{" + k + "}}", v)
    merge_block(repo / "CLAUDE.md", block, "# CLAUDE.md\n\n" + block, dry, "CLAUDE.md (ios-ai-kit block)")


def add_statusline(repo: Path, dry: bool) -> None:
    """Opt-in, per developer: the workflow's status line in .claude/settings.local.json (gitignored),
    never over a status line already set there."""
    path = repo / ".claude/settings.local.json"
    cur = json.loads(path.read_text()) if path.exists() else {}
    if "statusLine" in cur:
        log.append("kept     .claude/settings.local.json (it already sets a status line)")
        return
    cur["statusLine"] = {"type": "command", "command": f'python3 "{repo.resolve()}/scripts/ai/statusline.py"'}
    write(path, json.dumps(cur, indent=2) + "\n", dry, "merged" if path.exists() else "added")


def merge_docs(repo: Path, dry: bool) -> None:
    fresh = (KIT / "docs/ai-workflow.md").read_text()
    block = fresh[fresh.index(BEGIN):fresh.index(END) + len(END)] + "\n"
    merge_block(repo / "docs/ai-workflow.md", block, fresh, dry, "docs/ai-workflow.md", KNOWN_DOC_VERSIONS)

ENV_DEFAULTS = ["# Cloud sessions (no human to answer a prompt): the gate pushes only branches under this prefix",
             "# and opens a PR; CLOUD_PUBLISH=0 refuses every push there (you publish by hand).",
             "CLOUD_BRANCH_PREFIX=claude/", "CLOUD_PUBLISH=1",
             "# /lead: post verify reports on PRs, push its fixes, rebase instead of merging the base (0 = ask/never);",
             "# a PR idle this many days is 'stalled'; a cloud task with no PR after this many hours needs you.",
             "LEAD_COMMENT=0", "LEAD_PUSH=0", "LEAD_REBASE=0", "LEAD_STALE_DAYS=3", "LEAD_NO_PR_HOURS=6",
             "# Who judges /verify's screenshots: ai (judge.py, a separate Claude call) or human (history.py judge).",
             "VISUAL_JUDGE=ai",
             "# Claude models per role (opus, sonnet, haiku, …); empty = Claude Code's default. JUDGE_MODEL overrides MODEL_JUDGMENT for the visual judge.",
             "MODEL_JUDGMENT=", "MODEL_CODE=", "MODEL_FAST=", "JUDGE_MODEL=",
             "# How merge.sh lands a PR: merge, squash or rebase.",
             "MERGE_METHOD=merge"]


def write_env(repo: Path, d: dict, dry: bool) -> None:
    path = repo / ".claude/ios.env"
    if path.exists():
        text = path.read_text()
        add, comments = [], []  # a comment travels only with the missing keys that follow it
        for line in ENV_DEFAULTS:
            if line.startswith("#"):
                comments.append(line)
                continue
            if not re.search(rf"^{re.escape(line.split('=')[0])}=", text, re.M):
                add += comments + [line]
            comments = []
        if add:
            write(path, text.rstrip("\n") + "\n" + "\n".join(add) + "\n", dry, "extended")
        else:
            log.append("kept     .claude/ios.env (edit it to change detected values)")
        return
    lines = ["# ios-ai-kit configuration (committed). Per-checkout values go in .claude/ios.local.env (gitignored).",
             f"{'WORKSPACE' if d['kind'] == '-workspace' else 'PROJECT'}={d['container']}",
             f"SCHEME={d['scheme']}", f"APP_BUNDLE_ID={d['bundle']}", f"IOS_VERSION=",
             "DEVICE_MODEL=iPhone 17 Pro", "MIN_XCODE=27", f"SOURCE_DIRS={d['source_dirs']}",
             f"TEST_FLAGS={'-parallel-testing-enabled NO' if d['serial_tests'] else ''}",
             "# Passed on every launch (guard, visual, xcui): a fixture seed or skip-onboarding flag, if the app needs one.",
             "BASE_LAUNCH_ARGS=", *ENV_DEFAULTS]
    write(path, "\n".join(lines) + "\n", dry, "added")


def ensure_swift_format(repo: Path, d: dict, dry: bool) -> None:
    """A .swift-format matching the code's existing indentation, so the format hook and the lint gate
    never impose swift-format's 2-space default on a codebase that chose otherwise."""
    path = repo / ".swift-format"
    if path.exists():
        log.append("kept     .swift-format")
        return
    counts: dict[int, int] = {}
    for f in list(repo.glob("**/*.swift"))[:200]:
        if any(p in f.parts for p in (".build", "DerivedData", "Pods", "SourcePackages")):
            continue
        for line in f.read_text(errors="replace").splitlines():
            m = re.match(r"^( +)\S", line)
            if m and len(m.group(1)) in (2, 3, 4, 8):
                counts[len(m.group(1))] = counts.get(len(m.group(1)), 0) + 1
    spaces = 4 if counts.get(4, 0) + counts.get(8, 0) >= counts.get(2, 0) else 2
    cfg = {"version": 1, "indentation": {"spaces": spaces}, "lineLength": 120,
           "respectsExistingLineBreaks": True, "lineBreakBeforeEachArgument": False}
    write(path, json.dumps(cfg, indent=2) + "\n", dry, "added")


def merge_lines(repo: Path, rel: str, wanted: list[str], dry: bool) -> None:
    path = repo / rel
    cur = path.read_text() if path.exists() else ""
    have = {l.strip() for l in cur.splitlines()}
    add = [w for w in wanted if w not in have]
    if not add:
        log.append(f"same     {rel}")
        return
    write(path, cur.rstrip("\n") + ("\n" if cur else "") + "\n".join(add) + "\n", dry, "merged" if cur else "added")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--scheme")
    ap.add_argument("--container")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--statusline", action="store_true", help="also show the workflow status line (this Mac only)")
    a = ap.parse_args()
    repo = Path(a.repo).resolve()
    d = detect(repo, a.scheme, a.container)
    print(f"detected: {d['container']} · scheme {d['scheme']} · {d['bundle']} · iOS {d['deployment']} · "
          f"{'synchronized folders' if d['synced'] else 'explicit groups'} · sources: {d['source_dirs']}"
          f"{' · serial tests' if d['serial_tests'] else ''}")
    for rel in KIT_OWNED:
        copy_tree(rel, repo, a.dry_run, overwrite=True)
    for rel in CREATE_IF_MISSING:
        copy_tree(rel, repo, a.dry_run, overwrite=False)
    for rel in RETIRED_FILES:
        if (repo / rel).exists():
            if not a.dry_run:
                (repo / rel).unlink()
            log.append(f"removed  {rel} (retired by the kit)")
    screens = repo / ".claude/ios-screens.txt"
    if not a.dry_run and screens.exists() and "#seen:TODAY" in screens.read_text():
        screens.write_text(screens.read_text().replace("#seen:TODAY", time.strftime("#seen:%Y-%m-%d")))
    write_env(repo, d, a.dry_run)
    merge_settings(repo, a.dry_run)
    merge_mcp(repo, a.dry_run)
    merge_claude_md(repo, d, a.dry_run)
    merge_docs(repo, a.dry_run)
    if a.statusline:
        add_statusline(repo, a.dry_run)
    ensure_swift_format(repo, d, a.dry_run)
    merge_lines(repo, ".gitignore", GITIGNORE, a.dry_run)
    include = ["CLAUDE.local.md"] + [str(p.relative_to(repo)) for p in repo.glob("**/GoogleService-Info.plist")
                                     if ".build" not in p.parts and "DerivedData" not in p.parts]
    merge_lines(repo, ".worktreeinclude", include, a.dry_run)
    # Routine "same"/"kept"/"skipped" lines collapse to a count; only changes and warnings are listed.
    routine = lambda l: l.startswith(("same ", "kept ")) and "edited" not in l and "already sets" not in l
    changed = [l for l in log if not routine(l)]
    print("\n".join("  " + l.replace(str(repo) + "/", "") for l in changed))
    if len(log) - len(changed):
        print(f"  {'same':8} {len(log) - len(changed)} file(s) already current")
    dry = "(dry run: nothing written) " if a.dry_run else ""
    bootstrapped = (repo / ".claude/ios.local.env").exists()
    upgrade = any(l.startswith(("updated ", "merged ", "extended ")) for l in log) and not any(l.startswith("added    scripts") for l in log)
    print()
    if not bootstrapped:
        print(f"{dry}Next, once per Mac:\n    cd {repo} && scripts/ai/bootstrap.sh")
        print("Then see what only you can set up (trust, gh auth login, protect-main.sh):\n    scripts/ai/doctor.sh")
    elif any(l.startswith(("added ", "updated ", "merged ", "extended ")) for l in log):
        print(f"{dry}{'Upgraded' if upgrade else 'Installed'}. Anything left to set up:\n    scripts/ai/doctor.sh")
    else:
        print(f"{dry}Already current. Nothing to do.")
        return 0
    if any(l.startswith(("added ", "updated ", "merged ", "extended ")) for l in log):
        print("Propose these files like any change (never push to the default branch):\n"
              "    git switch -c claude/ios-ai-kit && git add scripts/ai .claude CLAUDE.md docs && git commit -m 'ios-ai-kit' && scripts/ai/pr.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
