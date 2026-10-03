#!/usr/bin/env python3
"""screens-drift.py: a screen whose seam the app no longer reads is broken (exit 1), an old #seen is
stale, unused seams are listed on request, and agreement is silent."""
import subprocess
import sys
import tempfile
import time
from pathlib import Path

AI = Path(__file__).resolve().parent.parent / "template/scripts/ai"
passed = failed = 0


def check(name, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  ok   {name}")
    else:
        failed += 1
        print(f"  FAIL {name}: got {got!r}, want {want!r}")


repo = Path(tempfile.mkdtemp())
subprocess.run(["git", "init", "-q", str(repo)], check=True)
(repo / ".claude").mkdir()
(repo / "App").mkdir()
(repo / ".claude/ios.env").write_text("SCHEME=App\nSOURCE_DIRS=App\n")
(repo / "App/Seams.swift").write_text('#if DEBUG\nlet a = ProcessInfo.processInfo.arguments\n'
                                      'if a.contains("-OpenSettings") {}\nif a.contains("-SeedData") {}\n'
                                      'if a.contains("-RunEval") {}\n#endif\n')
(repo / "App/Other.swift").write_text('let notASeam = "-LooksLikeOne"\n')
today = time.strftime("%Y-%m-%d")
old = time.strftime("%Y-%m-%d", time.localtime(time.time() - 90 * 86400))
screens = repo / ".claude/ios-screens.txt"


def run(*a):
    r = subprocess.run([sys.executable, str(AI / "screens-drift.py"), *a], cwd=repo, capture_output=True, text=True)
    return r.returncode, r.stdout


screens.write_text(f"# comment\n#seen:{today}\nsettings | -OpenSettings -SeedData | expect: Settings\nhome | |\n")
check("agreement is silent", run(), (0, ""))
screens.write_text(f"#seen:{today}\ntasks | -OpenTasks 3 | expect: Tasks\n")
rc, out = run()
check("a seam the app no longer reads is broken (exit 1)", (rc, "broken  tasks" in out and "-OpenTasks" in out), (1, True))
check("a literal outside a seam-reading file does not count", "-LooksLikeOne" in run("--seams")[1], False)
screens.write_text(f"#seen:{old}\nsettings | -OpenSettings | expect: Settings\n")
rc, out = run()
check("an old #seen is stale, not broken", (rc, "stale   settings" in out), (0, True))
rc, out = run("--seams")
check("--seams lists what no screen uses", "seams not in the matrix (2): -RunEval -SeedData" in out, True)
screens.unlink()
check("no screens file: nothing to say", run(), (0, ""))
print(f"{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
