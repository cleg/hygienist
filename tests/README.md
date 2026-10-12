# Validation

Run deterministic helper and filesystem tests with:

```sh
python3 -B -m unittest discover -s tests -p 'test_*.py'
```

These cover parsing, redacted output/errors, unchanged source files, missing
inputs, non-regular paths, and exclusion of helpers from discovery/renumbering.
Import isolation tests exercise neighboring-module and `PYTHONPATH` startup
injection using synthetic probes and verify absence of bytecode caches.
Permission errors are injected so the test works even with privileged test users.
The distribution test checks the exact runtime file/directory inventory, local
Markdown links, license equality, and absence of symlinks or repository content
inside `skills/hygienist/`.

## Instruction-driven installation scenarios

`init` and `add-rule` are agent workflows, not executable installers. Validate
these scenarios in disposable projects using the installed skill instructions;
filesystem unit tests cannot establish that an agent follows the instructions.
Use synthetic inputs only, and do not run installed rules during installation.

| Scenario | Expected result |
| --- | --- |
| Initialize with the environment template selected | Copy `skills/hygienist/templates/helpers/env-keys.py` to `.hygienist/helpers/env-keys.py` before the numbered environment rule; verify identical bytes. No helper execution or `.env.example` creation. |
| Initialize with only conflict markers, or no templates | No `helpers/` directory or environment helper. |
| Add the environment template to an existing rule directory | Install its helper, install and renumber the rule; preserve other checks. |
| Add a distinct rule that declares the same helper | Reuse the identical regular helper without rewriting it; both rules reference the stable helper path. |
| Required helper already has different bytes | Report the conflict; preserve the existing helper and do not install the dependent rule. |
| `helpers/` or the helper destination is a file, directory conflict, or symlink | Reject the conflicting path without following or replacing links; do not install the dependent rule. |
| A dependency copy fails partway through | Report installed resources and unmet dependencies explicitly; never claim completion or remove shared helpers. |
| Inspect a rule using a helper that prints values or sends them remotely | Read code only, flag the data flow with locations; do not execute code or read `.env`. |
| Inspect a rule with missing supporting code | Report incomplete coverage; do not treat it as safe. |
| Run environment rule with a missing helper | Return `FAIL`; do not read `.env` directly or create a replacement helper. |

For runtime path validation, try the environment rule with `helpers/` linked to
an external directory and then an internal directory: both must produce `FAIL`
before helper execution. Repeat with a linked helper file and a broken link.
With only `.hygienist` deliberately linked to the declared rule directory and
ordinary `helpers/`/helper entries beneath it, the path is supported; the agent
must disclose that destination. These checks are instruction-driven boundaries,
not an executable path sandbox, and need agent validation.

## Reproducible agent fixtures

Create a fresh disposable fixture tree (the destination must not already exist):

```sh
python3 -B tests/prepare_agent_fixtures.py /absolute/temporary/path/hygienist-trial
```

This prepares synthetic inputs and a `manifest.json` of targets and expectations;
it does not run rules, install through an agent, or prove agent compliance.
Never use a real project as the destination. Each trial must use the current
skill with a fresh agent context and the explicit target from the manifest.
For runtime trials, use [RUN.md](../skills/hygienist/references/RUN.md) and a fresh sequential checker per discovered
task with the verbatim checker contract, schema, and assigned rule. For the
`run-declared-link` target, explicitly select its `.hygienist` link as the rule
directory. Do not run the intentionally unsafe inspection helper.

| Fixture target | Agent operation and required observation |
| --- | --- |
| `install-new` | `init`, environment template already selected; helper copied before rule, no execution/example. |
| `install-shared` | `add-rule`, explicitly request separate environment template despite overlap; reuse identical helper and preserve existing caller. |
| `install-conflict` | `add-rule`, same selection; differing installed version preserved, dependent template not installed. |
| `author-custom` | `add-rule` a read-only JSON key inventory helper; test candidate with invented values, missing/malformed input and usage errors in a separate temporary tree, then install without running the real target rule. |
| `run-normal` | `run`; isolated installed helper, sanitized example, source unchanged. |
| `run-missing` | `run`; FAIL without direct source read, helper installation, or example creation. |
| `run-linked-external` / `run-linked-internal` | `run`; reject linked `helpers/` before execution even for internal destination. |
| `run-declared-link` | `run` with deliberately selected `.hygienist` link; disclose destination, execute ordinary helper beneath it. |
| `inspect` | Static review of two callers sharing unsafe helper output, missing dependency, supporting Markdown and misplaced task; helper path/lines and both callers, incomplete coverage, no execution or secret read. |

Record observed results outside the checkout in an external evidence store,
identifying date,
agent/host, skill revision or working-tree state, operations, tool observations,
filesystem verification, and untested cases. Do not equate the scenario matrix
or fixture generation with a passed test. Agent traces and result reports must
not include real secrets. Read-only baseline/final snapshots and source hashes
can establish preservation; inspection of tool actions is needed to distinguish
helper use from direct source reads. Filesystem state alone cannot prove a
command was never executed or that secrets were never read.

Keep historical results separate from the test scenarios and link their
provenance from the external project knowledge base. Historical reports do not
validate later source revisions or distribution layouts.

## Installed-copy smoke verification

Use a fresh temporary directory as the working directory and install from the
repository root with the skills CLI in project scope:

```sh
DISABLE_TELEMETRY=1 npx skills add /absolute/path/to/hygienist --skill hygienist --agent codex --copy --yes
```

Do not add `--global`. Verify the installed skill contains exactly the runtime
inventory with matching bytes and permissions, including its license, and no
repository documentation, tests, scratch data or reports. Record the CLI version
and installed path. Use the installed resources for a separate synthetic target:
initialize with only the environment template selected, run its sole rule through
a fresh checker, then inspect statically. Verify no helper/check ran during init,
source preservation, sanitized example output and complete inspection coverage.
Save new evidence outside the checkout and distinguish it from pre-migration
results. This procedure describes expectations; its presence does not establish
that a trial passed.

## Platforms

Discovery/renumbering require Bash and Python 3. The environment helper additionally
requires POSIX `O_NOFOLLOW` and `O_NONBLOCK`; macOS and Linux are intended targets,
and native Windows is unsupported (use a compatible POSIX environment). The unit
suite includes POSIX symlink/FIFO cases. A successful run on one host does not
establish a platform matrix; record actual host coverage in trial results.

Use this fully specified request for the `author-custom` fixture:
create a read-only `configuration key inventory` rule with a standard-library
Python helper at `.hygienist/helpers/config-keys.py`. Read only target-root
`private-config.json` as a JSON object; accept top-level names matching
`[A-Za-z_][A-Za-z0-9_]*`, sort them, and emit `NAME=` lines without values.
Invoke with `python3 -I -B`. Exit codes: 0 success, 3 absent (explicit OK skip),
1 malformed/non-object/invalid-key/read failure with secret-free diagnostics,
2 incorrect arguments. Permit no writes or network calls, prohibit agent reads
and helper bypass, and test the candidate before installation on synthetic
success, absence, malformed, invalid-key, and usage-error inputs with invented
canaries, input preservation and artifact checks. Do not run the installed
helper or real project check during authoring.
