# Repository instructions

Hygienist is a global skill. This repository contains its distributable source,
development tests and public documentation. Keep those separate from generated
workspaces and historical validation evidence.

## Project knowledge

Before planning or changing Hygienist, resolve AgentWiki from the user's global
instructions. If available, read its `AGENTS.md` first, then
`wiki/projects/hygienist.md` and the linked project TODO page for current
decisions, priorities, and validation limits. Read other linked evidence only
when relevant; do not load the entire wiki. If the wiki or a page is unavailable,
continue using repository instructions and report material gaps in context.

## Artifact placement

| Artifact | Destination |
| --- | --- |
| Skill entrypoint, operation references, checker contract/schema, orchestration scripts, bundled rule templates/helpers and agent metadata | `skills/hygienist/` |
| Public usage/development documentation and branding | Repository root (`README.md`, `AGENTS.md`, `logo.png`) |
| Beads issue database and agent integrations | `.beads/`, `.agents/skills/beads/`, `.codex/`, `.goosehints`, `AGENTS.md` |
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

<!-- BEGIN BEADS CODEX SETUP: generated by bd setup codex -->
## Beads Issue Tracker

Use Beads (`bd`) for durable task tracking in repositories that include it. Use the `beads` skill at `.agents/skills/beads/SKILL.md` (project install) or `~/.agents/skills/beads/SKILL.md` (global install) for Beads workflow guidance, then use the `bd` CLI for issue operations.

### Quick Reference

```bash
bd ready                # Find available work
bd show <id>            # View issue details
bd update <id> --claim  # Claim work
bd close <id>           # Complete work
bd prime                # Refresh Beads context
```

### Rules

- Use `bd` for all task tracking; do not create markdown TODO lists.
- Run `bd prime` when Beads context is missing or stale. Codex 0.129.0+ can load Beads context automatically through native hooks; use `/hooks` to inspect or toggle them.
- Keep persistent project memory in Beads via `bd remember`; do not create ad hoc memory files.

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/core-concepts/sync-concepts.md for details and anti-patterns.
<!-- END BEADS CODEX SETUP -->

## Hygienist Beads workflow

For this project, AgentWiki remains the source for durable knowledge and product
decisions. Beads tracks actionable work and its live status; the roadmap page
describes feature intent without duplicating status checklists.

Before starting work, run `bd prime`, `bd dolt pull`, and `bd ready`. Claim the
selected issue when appropriate and close it only after completion. Push Beads
changes with `bd dolt push` at handoff so collaborators see them. This allows
syncing the issue database; it does not authorize source-code commits or pushes.

After cloning, run `bd bootstrap`. Set the local role to `maintainer` for a
project collaborator with write access, or `contributor` for fork-based work:
`git config beads.role maintainer` or `git config beads.role contributor`.


<!-- BEGIN BEADS INTEGRATION v:1 profile:full hash:bacef91e -->
## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Dolt-powered version control with native sync
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

### Quick Start

**Check for ready work:**

```bash
bd ready --json
```

**Create new issues:**

```bash
bd create "Issue title" --description="Detailed context" -t bug|feature|task -p 0-4 --json
bd create "Issue title" --description="What this issue is about" -p 1 --deps discovered-from:bd-123 --json
```

**Claim and update:**

```bash
bd update <id> --claim --json
bd update bd-42 --priority 1 --json
```

**Complete work:**

```bash
bd close bd-42 --reason "Completed" --json
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues
2. **Claim your task atomically**: `bd update <id> --claim`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   - `bd create "Found bug" --description="Details about what was found" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`

### Quality
- Use `--acceptance` and `--design` fields when creating issues
- Use `--validate` to check description completeness

### Lifecycle
- `bd defer <id>` / `bd supersede <id>` for issue management
- `bd stale` / `bd orphans` / `bd lint` for hygiene
- `bd human <id>` to flag for human decisions
- `bd formula list` / `bd mol pour <name>` for structured workflows

### Sync

bd stores issue history in Dolt:

- Each write auto-commits to Dolt history
- Use `bd dolt push`/`bd dolt pull` for remote sync
- Do not treat `.beads/issues.jsonl` as the sync protocol

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/core-concepts/sync-concepts.md for details and anti-patterns.

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems

For more details, see README.md and https://github.com/gastownhall/beads/blob/main/docs/getting-started/quickstart.md.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   bd dolt push
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.

<!-- END BEADS INTEGRATION -->
