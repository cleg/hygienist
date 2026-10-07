---
name: hygyenist
description: Manual-only. Run Hygyenist only when the user explicitly requests it. Delegate repository tasks to independent checker subagents and combine their results. Never auto-select for ordinary repository work or mentions of Hygyenist.
disable-model-invocation: true
user-invocable: true
---

# Hygyenist

This repository uses Hygyenist.

## Manual invocation only

Run this workflow only when the user explicitly requests a Hygyenist run,
using their agent's skill command or a direct request such as "Run Hygyenist".
Examples include `/hygyenist`, `/skills hygyenist`, and `$hygyenist`, depending
on the agent.

Creating, editing, discussing, or mentioning this skill is not an invocation.
Do not infer a request to run it from ordinary repository work, reviews,
commits, or the presence of `.hygyenist` files. If automatically loaded without
an explicit user request to run Hygyenist, stop before discovery, commands,
or checker delegation.

The frontmatter disables model invocation in agents that support that field.
`agents/openai.yaml` disables implicit invocation in Codex. Agents that ignore
these settings must still follow the manual-only instructions above.

## Discover tasks

From the repository root:

1. Read `.hygyenist/CHECKER.md` and `.hygyenist/checker-result.schema.json`.
2. Run `.hygyenist/list-tasks.sh` (requires Bash and Python 3).
3. Parse its JSON output. Require a `tasks` array of unique repository-relative
   paths matching `.hygyenist/XX-name.md`, where `XX` is two digits. Preserve
   the returned order and keep this task list fixed for the run.

If the contract or schema cannot be read, discovery fails, or the task list is invalid,
report an orchestration failure and stop. Do not invent a task list.

## Run checkers

For each discovered task, in order:

- Start exactly one new, independent checker subagent with repository access
  and the repository root as its working directory. Explicitly provide the
  repository root, task path, and the contents and paths of
  `.hygyenist/CHECKER.md`, `.hygyenist/checker-result.schema.json`, and that task
  file. Pass the contract and task contents verbatim; do not summarize or
  rewrite them. Use a fresh context without other task files or previous
  checker results.
- Tell it to execute only its assigned task and read that task's rule for what
  to return in `message`. Require the final JSON object defined by the contract.
  If the agent supports a native output schema, supply the same JSON Schema.
- Wait for its final result before starting the next task. Extract the final
  checker response from any tool envelope without rewriting its contents.
  Validate it against `.hygyenist/checker-result.schema.json` and the contract,
  and associate it with the assigned task path. Schema validation checks format;
  it does not prove that the task was executed correctly.

Do not execute checker tasks in the parent context. Do not merge, skip, retry,
or reuse checker runs. A failed task does not prevent the remaining tasks
from running.

If a task file cannot be read, pass its path to its checker so the checker can
attempt to read it and report `FAIL` if unavailable. If a checker cannot be
started, crashes, or returns an invalid result, record `FAIL` for that task
with a message beginning `Orchestration failure:`. Such an entry is a parent
diagnostic, not a successful structured checker response. Do not substitute
your own execution. If subagents are unavailable altogether, report this
limitation and stop without executing any tasks.

## Combined report

After all runs finish, verify that every discovered task has exactly one report
entry, with no missing, duplicate, or extra entries. Also verify that each task
received exactly one checker run and a valid structured response; explicitly
report any exception as an orchestration failure.

Return a combined JSON report in discovery order. Each entry contains `task`,
`status`, and the optional `message` from the checker or the orchestration
diagnostic. Set the overall `status` to `OK` only when coverage is complete
and every task returned a valid `OK`; otherwise use `FAIL`.

Report shape (illustrative):

```json
{
  "status": "OK",
  "results": [
    {"task": ".hygyenist/10-first.md", "status": "OK", "message": "привіт"}
  ]
}
```

For an empty task list, return `{"status":"OK","results":[]}`. Do not claim
checks ran.
