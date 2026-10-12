# Hygienist issue tracking

This project uses [Beads](https://github.com/gastownhall/beads) to track
implementation work. The local Dolt database is authoritative; `issues.jsonl`
is not the sync source.

## First use

Install `bd` and run `bd bootstrap` after cloning the source repository. The
project config points to the canonical GitHub HTTPS URL for `origin`. With
write access to the shared repository, set the local role using
`git config beads.role maintainer`; fork contributors should use
`git config beads.role contributor`.

## Daily use

```sh
bd prime
bd dolt pull
bd ready
bd update <issue-id> --claim
```

After changing issue state, share it with:

```sh
bd dolt push
```

## Agent integrations

Codex uses the project Beads skill and native hooks. OpenCode gets its Beads
workflow from the managed section in the root `AGENTS.md`; Goose gets the same
project guidance through `.goosehints`. These files are committed so each tool
uses the same issue database and workflow.

Beads data sync is separate from Git source changes. See the root `AGENTS.md`
for the project workflow and the AgentWiki project page for product direction.
