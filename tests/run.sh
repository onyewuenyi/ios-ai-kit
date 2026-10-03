#!/usr/bin/env bash
# Every kit test that needs no simulator build. Usage: tests/run.sh
here=$(cd "$(dirname "$0")" && pwd); bad=0
echo "hooks"; "$here/hooks.sh" || bad=1
echo "cloud gate"; python3 "$here/cloud_gate.py" || bad=1
echo "pr"; "$here/pr.sh" || bad=1
echo "verify history"; "$here/verify_history.sh" || bad=1
echo "pr digest"; python3 "$here/prs.py" || bad=1
echo "installer"; "$here/install.sh" || bad=1
echo "syntax"
for f in "$here"/../template/scripts/ai/*.sh "$here"/../template/.claude/hooks/*.sh; do /bin/bash -n "$f" || { echo "  FAIL $f"; bad=1; }; done
for f in "$here"/../template/scripts/ai/*.py "$here"/../template/.claude/hooks/*.py "$here"/../install.py; do python3 -m py_compile "$f" || { echo "  FAIL $f"; bad=1; }; done
python3 -c 'import json,sys; [json.load(open(p)) for p in sys.argv[1:]]' "$here"/../template/.claude/settings.json "$here"/../template/.mcp.json || bad=1
echo "  ok   every script parses under /bin/bash 3.2 and python3"
exit $bad
