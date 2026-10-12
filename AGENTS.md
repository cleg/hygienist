# Repository instructions

Hygienist is a global skill. This repository contains its distributable source,
development tests and public documentation. Keep those separate from generated
workspaces and historical validation evidence.

## Artifact placement

| Artifact | Destination |
| --- | --- |
| Skill entrypoint, operation references, checker contract/schema, orchestration scripts, bundled rule templates/helpers and agent metadata | `skills/hygienist/` |
| Public usage/development documentation and branding | Repository root (`README.md`, `AGENTS.md`, `logo.png`) |
| License | Root `LICENSE` and an identical ordinary copy in `skills/hygienist/LICENSE` |
| Automated tests, reusable fixture sources/generators, expected outcomes and validation procedures | `tests/` |
| Existing local manual-test workspace and reset script | Ignored `_work/`; retain as local resources |
| New disposable fixtures, installed-copy test projects, caches and temporary output | A fresh temporary directory outside the checkout |
| Durable historical trial reports, raw checker results, tool observations, source fingerprints and preservation evidence | External evidence storage; use AgentWiki `raw/hygienist/YYYY-MM-DD-topic/` when available |
| Current decisions, reusable lessons and a concise validation summary with evidence links | AgentWiki `wiki/projects/hygienist.md` when available |

Do not add historical reports to `tests/agent-results/`, fixture READMEs or the
skill package. Test documentation describes how to reproduce scenarios and
their expected outcomes; observed results belong in external evidence storage.
Do not retain routine task logs or transient output as durable knowledge.

Resolve AgentWiki from the user's global instructions and read its `AGENTS.md`
before accessing it. Prefer updating the existing project page. If it is
unavailable, use another explicit external evidence location outside the checkout
and report that location; do not create a repository-local replacement wiki.
Keep public test documentation independent of personal wiki paths.

## Distribution boundary

`skills/hygienist/` is the sole source skill and must remain self-contained.
Do not duplicate `SKILL.md` at the repository root. Keep documentation, tests,
scratch data, reports and symlinks out of the package. `.gitignore` controls Git
tracking; it does not filter skill installation contents.

Resolve skill-owned resources from the directory containing its `SKILL.md`.
Resolve installed project rules, helpers and their inputs/outputs from the
selected target project's root. Target projects own `.hygienist/NN-name.md`
and `.hygienist/helpers/`; do not copy global contracts or orchestration into them.

The expected package inventory is maintained in
[tests/test_distribution.py](tests/test_distribution.py). When intentionally
adding or removing runtime resources, update that inventory and affected links
and tests together. Preserve file permissions and license equality.

## Evidence and local data

Record the date, host/platform, source revision or working-tree fingerprints,
installed skill/CLI version when relevant, operations, actual results, deviations
and untested cases. Distinguish agent-reported actions from independent filesystem
verification. A scenario table, fixture generation or a matching status alone
does not establish agent compliance or complete coverage.

Preserve historical evidence as captured. Do not rewrite old fingerprints,
paths or results to imply they validate a newer revision or layout. Archive
copies must be verified by SHA-256 and active references updated before removing
originals; conflicting destinations must not be overwritten.

Preserve preexisting uncommitted changes and local workspace contents. Do not
run `_work/reset.sh`, clear scratch data or execute hostile fixtures as incidental
cleanup. Hostile specimens are for static inspection only. Agent trials use
synthetic inputs and must not read real secrets or repair real projects.

## Validation

Run the applicable checks described in [tests/README.md](tests/README.md).
The automated suite command, from the repository root, is:

```sh
python3 -B -m unittest discover -s tests -p 'test_*.py'
```

For distribution/resource-path changes, also verify an actual project-scope
installation in a disposable directory and exercise the installed-copy smoke
procedure. Use the installed resources for that trial; store new evidence
externally and report its actual platform and coverage limits. Do not use a
global installation or alter unrelated development symlinks as part of a smoke
test.
