# Hygyenist

Hygyenist is a manually invoked agent skill that runs repository-defined tasks
through independent checker subagents and combines their structured results.

The MVP has been exercised in **Goose and Codex**. Its instructions and JSON
contract are shared across agents; discovery, delegation, and invocation controls
depend on the agent running the skill.

## Quick start

Open your agent in this repository with subagent delegation and repository access
enabled. Task discovery requires **Bash and Python 3**.

Explicitly invoke the local `hygyenist` skill:

- **Goose:** `/skills hygyenist` (`/skill hygyenist` also worked in the tested CLI).
- **Codex:** `$hygyenist`.
- **Other agents:** use the agent's skill invocation mechanism. If it does not
  discover this directory, explicitly ask it to read and follow
  `.agents/skills/hygyenist/SKILL.md` to run Hygyenist.

The current tasks are test fixtures. **The first task intentionally returns
`FAIL`, so the expected overall status is `FAIL`.** The remaining tasks should
still run.

To inspect the discovered tasks without running any checker:

```sh
bash .hygyenist/list-tasks.sh
```

## Repository layout

```text
.agents/skills/hygyenist/
├── SKILL.md                     # Parent agent's orchestration instructions
└── agents/openai.yaml            # Codex invocation policy
.hygyenist/
├── CHECKER.md                   # Shared checker instructions and result contract
├── checker-result.schema.json   # JSON Schema for one checker result
├── list-tasks.sh                # Ordered task discovery
├── 10-first.md                  # Intentional failure returning "hello"
├── 20-second.md                 # Current time from a clock
├── 30-isolation-source.md       # Canary token source
└── 40-isolation-probe.md        # Probe for another checker's token
```

## How a run works

1. The parent reads the checker contract and result schema, then discovers tasks.
2. It keeps that ordered list fixed for the run.
3. For each task, it starts exactly one fresh checker and provides the repository
   root, task path, contract, schema, and task contents. The contract and task are
   passed verbatim, without other task contents or previous checker results.
4. It waits for the result before starting the next checker.
5. It validates each response and returns one combined report in discovery order.

The parent may read task files to prepare delegation, but executes no checker
tasks itself. Tasks are not merged, skipped, retried, or assigned to a reused
checker. A failed task does not stop the remaining tasks.

A checker startup failure, crash, or invalid response becomes a `FAIL` entry with
an `Orchestration failure:` message. Discovery failures or unavailable delegation
stop the workflow rather than falling back to execution in the parent.

## Writing tasks

Add a Markdown file to `.hygyenist` named `XX-name.md`, where `XX` is exactly two
digits. Files are sorted by filename, so the number determines execution order.
Contract files, schemas, and other files without that naming pattern are excluded.

Each task defines what to do, what counts as success, and what to return in
`message`. For example, `.hygyenist/50-example.md` could contain:

```markdown
Return OK with message set to exactly "example completed".
```

A task can involve files, commands, or other resources available to the checker.
The shared contract does not require file paths, line numbers, or a particular
message format. Checkers may inspect supporting resources, but may modify
repository files only when the assigned task explicitly requests it.

## Results

Each checker returns one JSON object with no surrounding text:

```json
{"status": "OK", "message": "example completed"}
```

- `status` is required and must be `OK` or `FAIL`.
- `message` is a string, optional for `OK` and required for `FAIL`.
- The task determines the contents of `message`. If no failure message is
  specified, the checker briefly explains the failure.
- Extra fields and `null` messages are not allowed.
- `OK` means the task completed and all required checks were performed and passed.
  Missing inputs, unavailable tools, or unverifiable completion produce `FAIL`.

See [CHECKER.md](.hygyenist/CHECKER.md) and the
[result schema](.hygyenist/checker-result.schema.json) for the complete contract.
Native output-schema support is used when available. Schema validation verifies
the response format; it does not establish that the task was executed correctly.

The parent adds the task path to each result. A shortened report illustrating the
intentional failure fixture:

```json
{
  "status": "FAIL",
  "results": [
    {"task": ".hygyenist/10-first.md", "status": "FAIL", "message": "hello"}
  ]
}
```

An actual run includes every discovered task. The overall status is `OK` only
when every task has exactly one valid checker response and all statuses are `OK`.
An empty task list returns `{"status":"OK","results":[]}` without running checks.

## Manual invocation

The skill combines several controls:

- `disable-model-invocation: true` and `user-invocable: true` in `SKILL.md`.
- `policy.allow_implicit_invocation: false` in `agents/openai.yaml` for Codex.
- Explicit manual-only instructions in the skill description and body.

Creating, editing, or discussing Hygyenist is not a request to run it. An agent
that loads the skill automatically is instructed to stop before discovery or
delegation unless the user explicitly requested a run.

Invocation controls and skill locations vary between agents. These settings
provide technical controls where supported and instruction-based behavior
elsewhere; manual-only invocation is not guaranteed across every agent.

## MVP validation

Manual runs established the following behavior:

| Scenario | Goose | Codex |
| --- | --- | --- |
| Explicit invocation and structured report | Passed | Passed |
| One checker per task, sequential execution | Passed | Passed |
| Intentional failure, remaining tasks continue | Passed | Passed |
| Canary probe reports no other token visible | Passed | Passed |
| Deliberately injected canary produces `FAIL` | Passed | Not tested |
| Ordinary request does not invoke the skill | Passed | Not tested |

For the negative isolation test, independently launch only the probe checker and
include the source canary in its invocation context, outside the assigned task's
text. Do not tell the checker the expected answer. It should return `FAIL` and
identify the token. This is a separate test, not part of the normal workflow.

The isolation probe is behavioral evidence, not proof of isolation. Inspect
actual delegation inputs and checker logs as well. Goose logs were inspected;
the supplied Codex transcript confirms sequential delegation and results, but
truncates the full delegation prompts.

Fresh checker contexts also share repository access. This workflow targets
conversation-context isolation; it does not provide filesystem isolation.
Validation currently consists of manual runs rather than an automated test suite.
