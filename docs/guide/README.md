# The ios-ai-kit guide

The kit works best when you stop micromanaging the agent. You say what you want and how you will know it is done. `/ios-loop` picks the playbook, runs the other skills as the steps need them, and shows you the evidence from this checkout's own simulator. This guide teaches that habit with realistic iOS prompts.

Here is what you will learn.

1. [Set up the kit](./01-setup.md). Install it, bootstrap the Mac, and pick your Claude models.
2. [Route work through `/ios-loop`](./02-ios-loop.md). Give it a goal and watch it pick a playbook.
3. [Understand the code](./03-understand.md). `/how`, `/why`, `/teach` and `/recall` before you edit anything.
4. [Design the change](./04-design.md). `/architect`, `/arena`, `/swarm` and `/interrogate` before code locks in a shape.
5. [Build and clean the change](./05-build-and-clean.md). The build playbooks, `/tdd`, `/unslop` and `/no-comments`.
6. [Verify and ship](./06-verify-and-ship.md). From an idea to a merged PR with `/ship`, `/verify`, the AI judge, `pr.sh`, `merge.sh` and `/lead`.
7. [Run work while you sleep](./07-overnight.md). An overnight contract, a decision log you can audit, and the playbooks that scale past one agent.
8. [Steer with principle names](./08-principles.md). The names that redirect an agent mid-task.
9. [Make it yours](./09-make-it-yours.md). Your own mode, lessons kept in structure, and how to test a skill change.
10. [Recipes and pitfalls](./10-recipes-and-pitfalls.md). Prompts to copy and mistakes to skip.

Read the pages in order the first time. After that, each page stands alone.

## If you only remember one thing

Give the agent a goal and a way to check it, in your own words.

```text
/ios-loop the task list shows a row twice after a CloudKit sync lands mid-edit. repro first, then fix and verify.
```

You do not need to name a playbook or list skills. "repro first" and a checkable outcome are all the routing signal `/ios-loop` needs. It matches the Bug fix playbook, copies the steps into the todo list, and calls the right skills as each step fires. It ends with `/verify`'s report, the screenshots it judged, and what it could not verify on a simulator.

Next is [Set up the kit](./01-setup.md).
