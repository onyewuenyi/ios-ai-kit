#!/usr/bin/env bash
# Every kit test that needs no simulator build. Usage: tests/run.sh
here=$(cd "$(dirname "$0")" && pwd); bad=0
echo "hooks"; "$here/hooks.sh" || bad=1
echo "cloud gate"; python3 "$here/cloud_gate.py" || bad=1
echo "pr"; "$here/pr.sh" || bad=1
echo "verify history"; "$here/verify_history.sh" || bad=1
echo "gate scope"; "$here/scope.sh" || bad=1
echo "pr digest"; python3 "$here/prs.py" || bad=1
echo "delegate"; "$here/delegate.sh" || bad=1
echo "ship"; "$here/ship.sh" || bad=1
echo "bearings"; "$here/bearings.sh" || bad=1
echo "friction"; python3 "$here/friction.py" || bad=1
echo "screens drift"; python3 "$here/screens_drift.py" || bad=1
echo "one-job standard"; python3 "$here/standard.py" || bad=1
echo "installer"; "$here/install.sh" || bad=1
echo "syntax"
for f in "$here"/../template/scripts/ai/*.sh "$here"/../template/.claude/hooks/*.sh; do /bin/bash -n "$f" || { echo "  FAIL $f"; bad=1; }; done
for f in "$here"/../template/scripts/ai/*.py "$here"/../template/.claude/hooks/*.py "$here"/../install.py; do python3 -m py_compile "$f" || { echo "  FAIL $f"; bad=1; }; done
python3 -c 'import json,sys; [json.load(open(p)) for p in sys.argv[1:]]' "$here"/../template/.claude/settings.json "$here"/../template/.mcp.json || bad=1
# macOS's own python3 (Xcode's command-line tools) is 3.9: every kit module must load there too
if [[ -x /usr/bin/python3 ]]; then
  for m in "$here"/../template/scripts/ai/*.py "$here"/../template/.claude/hooks/*.py "$here"/../template/.claude/skills/*/scripts/*.py "$here"/../install.py; do
    /usr/bin/python3 -c "import ast,sys; compile(open(sys.argv[1]).read(), sys.argv[1], 'exec')" "$m" || { echo "  FAIL $m on $(/usr/bin/python3 --version)"; bad=1; }
  done
  (cd "$here/../template/scripts/ai" && for m in kit history prs friction judge statusline; do /usr/bin/python3 -c "import $m" >/dev/null 2>&1 || { echo "  FAIL import $m on $(/usr/bin/python3 --version)"; bad=1; }; done)
fi
echo "  ok   every script parses under /bin/bash 3.2, python3 and macOS's system python3"
exit $bad
