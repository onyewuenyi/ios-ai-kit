# Set up the kit

In this page you install the kit into your iOS repo, bootstrap this Mac, pick which Claude models the kit's subagents use, and run your first task. Setup is two commands plus a short conversation.

## Install the plugin

In Claude Code, run these two commands.

```text
/plugin marketplace add onyewuenyi/ios-ai-kit
/plugin install ios-ai-kit@ios-ai-kit
```

Then, inside your iOS repo, run this.

```text
/ios-ai-kit:setup
```

`/ios-ai-kit:setup` installs the kit into the repo, bootstraps this Mac, runs the doctor, lists the steps only you can take, and proposes the new files as a pull request. Run it again to upgrade.

If you prefer to skip the marketplace, clone the kit and run the installer yourself.

```bash
git clone https://github.com/onyewuenyi/ios-ai-kit ~/ios-ai-kit
python3 ~/ios-ai-kit/install.py /path/to/YourApp   # detects project/workspace, scheme, bundle id, deployment target
cd /path/to/YourApp && scripts/ai/bootstrap.sh     # once per Mac: toolchain, Apple's skills, simulator, smoke test
```

`git pull` in the clone and re-run `install.py` to upgrade. Both routes install the same files. The plugin carries only the `setup` skill. The workflow itself lives in your repo, so a teammate or a cloud session that never installed the plugin gets the same behavior.

## Do the steps only you can do

Some steps need a person, a browser, or a decision about your accounts. Setup lists the ones still open, and `scripts/ai/doctor.sh` checks every one it can see, so you can run it any time.

- Select Xcode 27 with `sudo xcode-select -s /Applications/Xcode.app`.
- Sign in to GitHub with `gh auth login`.
- Run `claude` in the repo once and choose **Yes** on the trust prompt. Until then the committed permission rules are ignored.
- Run `scripts/ai/protect-main.sh` once per repo, so GitHub itself refuses direct pushes to the default branch.
- Run `/web-setup` if you want cloud sessions.
- Optionally turn on Xcode ▸ Settings ▸ Intelligence ▸ Model Context Protocol ▸ **Xcode Tools**, so `/verify` can assert on the live UI hierarchy. Without it those assertions are reported as skipped, never as passed.

## Pick your models

Setup asks which Claude model fills each role. It writes the answers to `.claude/ios.env`, a small file every kit skill reads.

| Role | Key | Suggested | Used for |
|---|---|---|---|
| Judgment | `MODEL_JUDGMENT` | `opus` | design, review, the AI judge, the hardest code |
| Code | `MODEL_CODE` | `sonnet` | routine code and second opinions |
| Fast | `MODEL_FAST` | `haiku` | mechanical work, such as reading a build log |

You only set what you care about. A role left empty falls back to Claude Code's default model. To restore that, delete the value. A second opinion in this kit is the same prompt against a different Claude model, so `/interrogate` and `/arena` read these roles to pick the second model.

You might wonder what happens if you put a model name in a prompt instead. It works for that one call. It does not survive the next session, and it does not reach a teammate. Put a lasting choice in `.claude/ios.env`.

## Turn on the status line, or don't

Setup offers one more thing, a status line under the prompt.

```text
⎇ claude/topic · ✓ verified 3171e3c · 2 PRs need you · 3 uncommitted
```

Say yes and it is written to your gitignored `.claude/settings.local.json`, for this Mac only. It never replaces a status line you already have.

## Map your screens

The visual gate in `/verify` needs to know which screens your app has and how to reach each one. If `.claude/ios-screens.txt` is empty, run this.

```text
/map
```

`/map` builds the screen list from the app's own launch seams and its live accessibility labels. [Verify and ship](./06-verify-and-ship.md) covers when and why.

After setup, start a new session. The permission rules and hooks apply to new sessions.

## Run your first task

Pick something real but small, and describe it the way you would describe it to a colleague.

```text
/ios-loop add a "Sort by due date" option to the task list menu. the current order stays the default. verify both orders on the simulator.
```

Watch the todo list. Its first items are the matched playbook's steps copied in, the Feature playbook for this prompt. If `/ios-loop` skips a step, the step stays in the list with `skip: <reason>`, so you can see what it chose not to do.

From here you can type normal follow-ups. Once loaded, `ios-loop` stays in charge for the rest of the conversation until you say otherwise.

Next is [Route work through `/ios-loop`](./02-ios-loop.md).
