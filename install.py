#!/usr/bin/env python3
"""Install (or upgrade) ios-ai-kit into an iOS repository.

usage: install.py <repo> [--scheme NAME] [--container PATH] [--dry-run]

Detects the project, writes .claude/ios.env, copies the kit's scripts, hooks, skills, agents and
rules, and MERGES into existing files instead of overwriting them:
  .claude/settings.json  permissions unioned, hooks appended unless an equivalent exists
                         (an existing swift-format hook is kept and ours skipped), worktree.baseRef set
  .mcp.json              adds the `xcode` server if absent
  CLAUDE.md              the ios-ai-kit block between markers, replaced in place on upgrade
  .gitignore             adds the kit's local-only paths
Kit-owned files (scripts/ai/*, .claude/hooks/*, the ios-loop and verify skills) are updated on every
run; files a team is expected to edit (.claude/ios.env, ios-screens.txt, agents, PR template, docs)
are only created when missing. Idempotent: run it again to upgrade.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent / "template"
KIT_OWNED = ["scripts/ai", ".claude/hooks", ".claude/skills/ios-loop", ".claude/skills/verify",
             ".claude/rules/ios27-swift.md", ".claude/agents/build-verify.md", ".claude/agents/ui-verify.md"]
CREATE_IF_MISSING = [".claude/ios-screens.txt",
                     ".github/pull_request_template.md", "docs/ai-workflow.md"]
GITIGNORE = [".build/", ".claude/ios.local.env", "CLAUDE.local.md", ".claude/settings.local.json", ".claude/worktrees/"]
# Rules an earlier kit version wrote that were wrong; an upgrade removes them.
RETIRED_RULES = ["mcp__xcode__DeviceEventSynthesize", "mcp__xcode__XcodeListWindows"]
BEGIN, END = "<!-- ios-ai-kit:begin", "<!-- ios-ai-kit:end -->"
log: list[str] = []


def run(*cmd: str, cwd: Path) -> str:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed: {(r.stderr or r.stdout).strip()[-400:]}")
    return r.stdout


def detect(repo: Path, scheme: str | None, container: str | None) -> dict:
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
    files = [src] if src.is_file() else [p for p in src.rglob("*") if p.is_file()]
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
    for k in ("allow", "ask", "deny"):
        have = perms.setdefault(k, [])
        have[:] = [r for r in have if r not in RETIRED_RULES]
        have += [r for r in ours["permissions"][k] if r not in have]
    cur.setdefault("worktree", {}).setdefault("baseRef", "head")
    hooks = cur.setdefault("hooks", {})
    existing_cmds = json.dumps(hooks)
    for event, groups in ours["hooks"].items():
        for g in groups:
            for h in g["hooks"]:
                script = h["command"].rsplit("/", 1)[-1].strip('"')
                if script in existing_cmds:
                    continue  # ours, from an earlier install
                if script == "format-swift.sh" and "swift-format" in existing_cmds:
                    log.append("skipped  format hook (the repo already formats Swift on edit)")
                    continue
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


def merge_claude_md(repo: Path, d: dict, dry: bool) -> None:
    block = (KIT / "CLAUDE.block.md").read_text()
    style = ("synchronized folders (a new .swift file in the target's folder compiles automatically)" if d["synced"]
             else "explicit groups (add files through Xcode or the Xcode MCP; confirm target membership)")
    for k, v in {"CONTAINER": d["container"], "SCHEME": d["scheme"], "BUNDLE_ID": d["bundle"],
                 "DEPLOYMENT": d["deployment"], "FILE_STYLE": style}.items():
        block = block.replace("{{" + k + "}}", v)
    path = repo / "CLAUDE.md"
    cur = path.read_text() if path.exists() else f"# CLAUDE.md\n\n"
    if BEGIN in cur:
        new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", block, cur, flags=re.S)
    else:
        new = cur.rstrip() + "\n\n" + block
    if new == cur:
        log.append("same     CLAUDE.md (ios-ai-kit block)")
    else:
        write(path, new, dry, "merged" if path.exists() else "added")


def write_env(repo: Path, d: dict, dry: bool) -> None:
    path = repo / ".claude/ios.env"
    if path.exists():
        log.append("kept     .claude/ios.env (edit it to change detected values)")
        return
    lines = ["# ios-ai-kit configuration (committed). Per-checkout values go in .claude/ios.local.env (gitignored).",
             f"{'WORKSPACE' if d['kind'] == '-workspace' else 'PROJECT'}={d['container']}",
             f"SCHEME={d['scheme']}", f"APP_BUNDLE_ID={d['bundle']}", f"IOS_VERSION=",
             "DEVICE_MODEL=iPhone 17 Pro", "MIN_XCODE=27", f"SOURCE_DIRS={d['source_dirs']}",
             f"TEST_FLAGS={'-parallel-testing-enabled NO' if d['serial_tests'] else ''}",
             "# Passed on every launch (guard, visual, xcui): a fixture seed or skip-onboarding flag, if the app needs one.",
             "BASE_LAUNCH_ARGS="]
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
    write_env(repo, d, a.dry_run)
    merge_settings(repo, a.dry_run)
    merge_mcp(repo, a.dry_run)
    merge_claude_md(repo, d, a.dry_run)
    ensure_swift_format(repo, d, a.dry_run)
    merge_lines(repo, ".gitignore", GITIGNORE, a.dry_run)
    include = ["CLAUDE.local.md"] + [str(p.relative_to(repo)) for p in repo.glob("**/GoogleService-Info.plist")
                                     if ".build" not in p.parts and "DerivedData" not in p.parts]
    merge_lines(repo, ".worktreeinclude", include, a.dry_run)
    print("\n".join("  " + l.replace(str(repo) + "/", "") for l in log))
    print(f"\n{'(dry run: nothing written) ' if a.dry_run else ''}Next: cd {repo} && scripts/ai/bootstrap.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
