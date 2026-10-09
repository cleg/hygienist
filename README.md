![Project logo](logo.png)

# Hygienist

## ⚠️ Be careful with third-party rules

> [!WARNING]
> **Rules are instructions executed by an agent with access to your project and
> its available tools. A malicious rule can request secret disclosure, network
> uploads, file deletion, or other destructive actions.**
>
> **Review third-party rules and any scripts they call before running them.
> Hygienist does not automatically inspect or filter rules, and does not provide
> its own security sandbox. At this stage, rule safety is the user's
> responsibility.** Use the optional `inspect` operation to help assess risk;
> its report is advisory and cannot guarantee that a rule is safe.

Hygienist is a global agent skill that runs repository-defined tasks
through independent checker subagents and combines their structured results.

The MVP has been exercised in **Goose and Codex**. Its instructions and JSON
contract are shared across agents; discovery, delegation, and invocation controls
depend on the agent running the skill.

## Repository layout and setup

This repository is the source of the global skill. A deployed target contains
only Markdown checks in `.hygienist/`; the global skill owns orchestration,
checker instructions, task discovery, and the result schema.

```text
SKILL.md                        # Global skill entrypoint
agents/openai.yaml              # Codex invocation policy
references/
├── INIT.md                      # Project initialization
├── ADD-RULE.md                  # Interactive rule authoring
├── RUN.md                       # Check execution and reporting
├── INSPECT.md                   # Read-only rule safety review
├── SAFETY.md                    # Optional inspection risk criteria
├── CHECKER.md                   # Shared checker instructions
└── checker-result.schema.json   # Result contract
scripts/
├── list-tasks.sh                # Ordered discovery for an explicit target
└── renumber-rules.sh            # Normalize rule numbers to 10, 20, 30, ...
templates/
├── 10-env-example.md            # Sanitized dotenv example
├── 20-os-artifacts.md           # OS metadata ignore rules
└── 30-conflict-markers.md        # Unresolved merge conflicts
tests/fixtures/
├── sample/                     # Four original MVP run fixtures
│   ├── 10-first.md              # Intentional failure returning "hello"
│   ├── 20-second.md             # Current time from a clock
│   ├── 30-isolation-source.md   # Canary token source
│   └── 40-isolation-probe.md    # Probe for another checker's token
└── bad/                        # Two intentionally hostile inspect rules
    ├── README.md               # Expected risks and inspect-only usage
    ├── 10-upload-secrets.md
    └── 20-override-harness.md
```

For local development, link the repository into the agent's global skills
directory. Goose uses `~/.agents/skills/`; Codex uses `~/.codex/skills/`:

```sh
# Goose
mkdir -p ~/.agents/skills
ln -s /absolute/path/to/hygienist ~/.agents/skills/hygienist

# Codex
mkdir -p ~/.codex/skills
ln -s /absolute/path/to/hygienist ~/.codex/skills/hygienist
```

Verify Goose discovery from the target project with `goose skills list`.

Do not replace an existing installation without inspecting it. The link keeps
skill edits live in the global installation. Skill discovery may require a new
agent session.

Start the agent in the target project containing `.hygienist/`, with subagent delegation
and repository access enabled. The agent can select the global `hygienist` skill
for repository hygiene verification, or you can invoke it directly:

- **Goose:** `/skills hygienist` (the original MVP also supported the singular `/skill` form).
- **Codex:** `$hygienist`.
- **Other agents:** use their skill invocation mechanism, or explicitly ask the
  agent to read the global `SKILL.md` and run it against the target directory.

Inspect discovery without running any checker, from the source repository:

```sh
bash scripts/list-tasks.sh /absolute/path/to/target-project
```

Discovery requires Bash and Python 3. A missing `.hygienist/` directory is an
error; an existing empty directory returns an empty task list.

## Initialize a project

Ask the agent to initialize Hygienist in the target project, for example:
`Use $hygienist to init this project`.

Initialization creates an empty `.hygienist/` directory only when it is absent.
If it already exists, the agent leaves its contents unchanged and suggests that
you may have meant to add a rule. Checks are Markdown files named `NN-name.md`.
After creating the directory, the agent briefly offers the three starter rules
below. Choose any subset, all three, or none. Only selected rules are installed;
initialization does not run checks.

## Add a rule

Ask the agent to add a rule, for example:
`Use $hygienist to add-rule: check that all environment variables are documented`.

The agent discusses missing details before writing: the goal, files in scope,
verification method, success/failure criteria, behavior when inputs are absent,
and whether repairs are allowed. It uses details already provided and asks only
about meaningful gaps. Custom rules are self-contained Markdown so a fresh
checker can execute them without the authoring conversation.

Once the details are clear, the agent creates the rule without overwriting
existing files, runs the renumbering helper, and reports its final path. Adding
a rule does not run it. Existing templates can also be added with this operation.

## Starter rule templates

Choose templates and copy them into the target's `.hygienist/` directory, using
available numeric prefixes of at least two digits. You can also ask the agent to install selected
templates. During initialization, the agent offers these choices and installs
only the rules you select.

| Template | Behavior |
| --- | --- |
| [Environment example](templates/10-env-example.md) | Create or repair `.env.example` with the same keys as `.env` and empty values. Leave `.env` unchanged; skip synchronization when it is absent. Independently audit an existing example for secrets and sanitize findings. |
| [OS artifacts](templates/20-os-artifacts.md) | Add missing macOS, Windows, and Linux artifact patterns to `.gitignore`. Suggest untracking indexed artifacts; return `FAIL` until those are removed from the index. Outside Git, skip with a warning and make no changes. |
| [Conflict markers](templates/30-conflict-markers.md) | Scan tracked and untracked non-ignored text files and check the Git index. Report conflicts without editing files. Outside Git, skip with a warning. |

When synchronizing from `.env`, the environment template deliberately clears
all values, including non-secret defaults, and does not copy source comments.
Without `.env`, it leaves synchronization alone and audits an existing example
for secrets, preserving unrelated safe content. If both files are absent, it
returns `OK` without creating anything. The OS template changes only the
root `.gitignore`; it does not delete or untrack files. Both repair templates
verify the resulting state before reporting success.

## Inspect rules

Ask the agent to inspect the project's Hygienist rules, for example:
`Use $hygienist to inspect this project`.

Inspection reads rules and relevant local supporting code without executing
rule commands, repairing files, or renumbering. Findings identify paths, line
numbers, severity, the risky behavior, and a proposed safer alternative. The
review covers secret transmission, credential harvesting, destructive actions,
harness overrides, scope escapes, hidden commands, and unclear permissions.
Examples and commands recommended for user review are distinguished from actions
the rule actually asks the agent to perform.

Inspection is a separate, optional action. Findings do not automatically block
execution, and `run`, `init`, and `add-rule` do not perform a security preflight.
Choose which rules to trust and run after reviewing their behavior. The host
agent's own permissions remain in effect.

## When to run

Hygienist is useful after completing a set of changes, before a commit or pull
request, and after updating a check in a project with `.hygienist/` rules. It can
also be invoked directly whenever the user wants repository hygiene verification.
The skill guides agents to choose meaningful checkpoints and rerun when later
changes could affect the checks.

## How a run works

1. The parent reads the checker contract and result schema, discovers tasks,
   and keeps that ordered list fixed for the run.
2. For each task, it starts exactly one fresh checker, sequentially, supplying
   the target root, task path, contract/schema, and verbatim rule contents.
   Other tasks and earlier results are not supplied.
3. It validates each response and returns one report entry per discovered task
   in discovery order.

The parent does not execute checker tasks. Tasks are not merged, skipped,
retried, or assigned to a reused checker. A failure does not stop the remaining
tasks. No automatic safety review is performed.

A checker startup failure, crash, or invalid response becomes a `FAIL` entry with
an `Orchestration failure:` message. Discovery failures or unavailable delegation
stop the workflow rather than falling back to execution in the parent.

## Writing tasks

Add a Markdown file to `.hygienist` named `NN-name.md`, where `NN` has at least two
digits. Files are sorted by numeric prefix, then filename.
Files without that naming pattern are excluded.

After changes to installed rules, the skill renumbers them to `10, 20, 30, ...`,
retaining their order, descriptive names, and contents. For example,
`20-a.md`, `25-b.md`, `30-c.md` become `10-a.md`, `20-b.md`, `30-c.md`.
You can also run this directly:

```sh
bash scripts/renumber-rules.sh /absolute/path/to/target-project
```

The helper returns JSON with the renames and final task list. Numbers may exceed
99; discovery sorts them numerically. Renumbering does not run any checks.

Each task defines what to do, what counts as success, and what to return in
`message`. For example, `.hygienist/50-example.md` could contain:

```markdown
Return OK with message set to exactly "example completed".
```

A task can involve files, commands, or other resources available to the checker.
The shared contract does not require file paths, line numbers, or a particular
message format. Checkers may inspect supporting resources, but may modify
repository files only when the assigned task explicitly requests modifications,
subject to the host agent's own instructions and permissions.

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

See [CHECKER.md](references/CHECKER.md) and the
[result schema](references/checker-result.schema.json) for the complete contract.
Native output-schema support is used when available. Schema validation verifies
the response format; it does not establish that the task was executed correctly.

The parent adds the task path to each result. A shortened report illustrating the
intentional failure fixture:

```json
{
  "status": "FAIL",
  "results": [
    {"task": ".hygienist/10-first.md", "status": "FAIL", "message": "hello"}
  ]
}
```

An actual run includes every discovered task. The overall status is `OK` only
when every task has exactly one valid checker response and all statuses are `OK`.
An empty task list returns `{"status":"OK","results":[]}` without running checks.

## MVP validation

The scenarios in `tests/fixtures/sample/` are test checks, not starter rules for a
project. The first intentionally returns `FAIL`; a run of all four fixtures
should report overall `FAIL` and still execute the remaining checks.

Manual runs of the original MVP established the following behavior. The table
records those original run trials; later Goose trials also exercised initialization,
custom rule authoring, and inspection:

| Scenario | Goose | Codex |
| --- | --- | --- |
| Explicit invocation and structured report | Passed | Passed |
| One checker per task, sequential execution | Passed | Passed |
| Intentional failure, remaining tasks continue | Passed | Passed |
| Canary probe reports no other token visible | Passed | Passed |
| Deliberately injected canary produces `FAIL` | Passed | Not tested |

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
Agent workflow validation consists of manual runs. Discovery and renumbering
helpers also have filesystem tests, run with:

```sh
python3 -B -m unittest discover -s tests -p 'test_*.py'
```

Read-only inspection specimens and expected classifications are in
[tests/fixtures/bad](tests/fixtures/bad/README.md). They are separate from the
four MVP fixtures in `tests/fixtures/sample/` and must not be executed as ordinary
checks. These fixtures test advisory inspection, not runtime enforcement.

Manual `inspect` trials confirmed the following behavior:

| Scenario | Observed result |
| --- | --- |
| Four original MVP rules | No high-risk findings in the executable rules. |
| Two hostile rules | `HIGH RISK`: secret transmission/concealment, forged authority, harness modification, and fabricated success identified with line numbers. |
| Documentation alongside rules | Reviewed as documentation, not counted as an executable rule. |
| Read-only inspection | Rule commands were not executed and project files were not modified. |

The hostile-rule trial also worked from a natural-language inspection request.
These trials validate the observed workflow and findings on the supplied fixtures;
they are not exhaustive detection tests or runtime protection.

Current Goose trials also confirmed initialization with template selection,
declining all templates, interactive custom rule creation, post-write
renumbering, and execution of the authored rule in a separate checker. The
working-hours example preserved the requested exact messages and statuses.
Global discovery was separately verified with `goose skills list` after linking
the skill into `~/.agents/skills/`.

A pre-release agent trial exercised all three starter templates in a disposable
Git project using synthetic environment values:

| Template | Initial trial | After user-style remediation |
| --- | --- | --- |
| Environment example | Repaired mismatched keys and removed values/comments; `.env` unchanged. | `OK`, no further changes. |
| OS artifacts | Created `.gitignore`; returned `FAIL` for tracked `.DS_Store` with an untracking suggestion, without changing the index. | `OK` after the file was untracked; no further changes. |
| Conflict markers | Returned `FAIL` with the conflict block's line numbers; no edits. | `OK` after the conflict was resolved. |

Both trials used one fresh checker per rule in sequential order. The second
combined report was `OK` and performed no repairs. The trial covers these scoped
cases, not every missing-input or parser variant.
