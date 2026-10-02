#!/usr/bin/env python3
"""Assert what a screen SHOWS, through Xcode's device-interaction tools (xcrun mcpbridge).

Opens this checkout's project in Xcode if needed, starts a device-interaction session on THIS
checkout's simulator (by UDID), builds, installs and runs the app with the given launch arguments,
captures the UI hierarchy, and checks that each expected label is present.

usage: xcui.py --udid <UDID> --container <path.xcodeproj|.xcworkspace> --bundle <id>
               [--args="-Flag value"] (the = form: launch arguments start with -) [--expect "label"]… [--absent "label"]… [--name "Screen Name"]
Prints `hierarchy: <path>`, `screenshot: <path>`, then `ok`/`FAIL` per expectation.
Exit 0 all good · 1 an expectation failed · 3 Xcode's tools unavailable (not running, not approved).

Notes measured on Xcode 27.0: calls must use the workspaceIdentifier returned by
XcodeListWorkspaces / XcodeOpenWorkspace (a path is rejected despite the schema); the first
XcodeOpenWorkspace is what asks the user to approve the agent; deviceIdentifier accepts a UDID.
"""

import argparse
import json
import re
import select
import shlex
import subprocess
import sys
import time


class Bridge:
    def __init__(self) -> None:
        self.p = subprocess.Popen(["xcrun", "mcpbridge"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self.n = 0
        self.rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                "clientInfo": {"name": "ios-ai-kit", "version": "1"}}, 30)
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def send(self, msg: dict) -> None:
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()

    def rpc(self, method: str, params: dict, timeout: float) -> dict:
        self.n += 1
        self.send({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params})
        end = time.time() + timeout
        while time.time() < end:
            r, _, _ = select.select([self.p.stdout], [], [], 1)
            if not r:
                if self.p.poll() is not None:
                    raise RuntimeError("mcpbridge exited")
                continue
            line = self.p.stdout.readline()
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("id") == self.n:
                return d
        raise TimeoutError(method)

    def tool(self, name: str, args: dict, timeout: float = 300) -> str:
        d = self.rpc("tools/call", {"name": name, "arguments": args}, timeout)
        res = d.get("result") or {}
        text = "".join(c.get("text", "") for c in res.get("content", []))
        if res.get("isError") or "Error Domain=" in text:
            raise RuntimeError(f"{name}: {text[:400]}")
        return text

    def close(self) -> None:
        try:
            self.p.terminate()
        except Exception:
            pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--udid", required=True)
    ap.add_argument("--container", required=True)
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--args", default="")
    ap.add_argument("--expect", action="append", default=[])
    ap.add_argument("--absent", action="append", default=[])
    ap.add_argument("--name", default="Verify Screen")
    a = ap.parse_args()
    try:
        b = Bridge()
        lst = b.tool("XcodeListWorkspaces", {}, 30)
    except Exception as e:
        lst = ""
        if "isn't approved" not in str(e) and "not approved" not in str(e):
            print(f"xcui: Xcode tools unavailable ({str(e)[:160]})")
            return 3
    try:
        m = re.search(r"workspaceIdentifier: (\S+?),? workspacePath: " + re.escape(a.container) + r"\s*$", lst, re.M)
        ws = m.group(1) if m else json.loads(b.tool("XcodeOpenWorkspace", {"path": a.container}, 180))["workspaceIdentifier"]
        key = json.loads(b.tool("DeviceInteractionStartWorkspaceSession",
                                {"sessionIdentifier": a.name.title(), "deviceIdentifier": a.udid,
                                 "workspaceIdentifier": ws}, 300))["interactionSessionKey"]
    except Exception as e:
        print(f"xcui: Xcode tools unavailable ({str(e)[:200]})")
        b.close()
        return 3
    rc = 0
    try:
        b.tool("DeviceInteractionInstallAndRun", {"interactionSessionKey": key, "workspaceIdentifier": ws,
                                                  "commandLineArguments": ["$(inherited)", *shlex.split(a.args)]}, 900)
        time.sleep(2)
        cap = json.loads(b.tool("DeviceInteractionSynthesize", {"interactSessionKey": key, "activationBundleId": a.bundle}, 120))
        hier = open(cap["hierarchyPath"], errors="replace").read()
        print(f"hierarchy: {cap['hierarchyPath']}\nscreenshot: {cap['screenshotPath']}")
        labels = re.findall(r"label: '((?:[^'\\]|\\.)*)'", hier) + re.findall(r"identifier: '((?:[^'\\]|\\.)*)'", hier)
        for want in a.expect:
            hit = any(want in l for l in labels)
            print(f"{'ok  ' if hit else 'FAIL'} shows '{want}'")
            rc |= 0 if hit else 1
        for bad in a.absent:
            hit = any(bad in l for l in labels)
            print(f"{'FAIL' if hit else 'ok  '} does not show '{bad}'")
            rc |= 1 if hit else 0
    except Exception as e:
        print(f"xcui: {str(e)[:300]}")
        rc = 1
    finally:
        try:
            b.tool("DeviceInteractionEndSession", {"interactionSessionKey": key}, 60)
        except Exception:
            pass
        b.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
