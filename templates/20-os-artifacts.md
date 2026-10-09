# Keep operating-system artifacts out of Git

## Scope and permitted changes

Check the target Git repository's root `.gitignore` and tracked/indexed paths.
You may create or append to the root `.gitignore`, preserving existing content.
Do not delete files, change the Git index, stage changes, or commit. In particular,
do not execute the removal commands suggested in the result.

## Artifact catalog

Use these Git ignore patterns, applying them at any depth:

```gitignore
# macOS
.DS_Store
.AppleDouble/
.LSOverride
._*
.Spotlight-V100/
.Trashes/
# Windows
Thumbs.db
ehthumbs.db
ehthumbs_vista.db
[Dd]esktop.ini
$RECYCLE.BIN/
# Linux and shared filesystems
.Trash-*/
.nfs*
```

Match file basenames and ancestor directory names against the catalog. Directory
patterns cover their descendants; they do not match similarly named regular
files. These are OS metadata and temporary artifacts, not a general list of
editor settings or build outputs. Honor explicit project exceptions; report
unresolved intentional uses rather than silently overriding them.

## Check and repair

1. Check whether the target belongs to a Git working tree before inspecting or
   editing `.gitignore`. If it is not a Git repository, return `OK` with a warning
   in `message`: "Warning: skipped OS-artifact checks because this is not a Git
   repository. No files were changed." Stop without creating `.gitignore` or
   initializing Git. Git being unavailable or a Git access/configuration error
   is not evidence that the target is a non-Git directory: return `FAIL` with
   that limitation instead. For a Git working tree, verify that the target is
   its root; do not silently modify a parent repository for a nested target.
2. Read tracked and staged paths using `git ls-files --cached -z`, deduplicating
   paths. Use null-delimited output so spaces and newlines in names are handled.
   Identify artifact paths by the catalog, independently of ignore rules: Git
   ignore patterns do not stop tracking files already in the index.
3. Inspect the root `.gitignore`. Refuse to overwrite a directory or symlink at
   that path. Append missing patterns in a clearly marked OS-artifacts section,
   with a separating newline, without rewriting other rules or duplicating
   patterns already present. Do not rely on the user's global Git excludes.
4. Verify each catalog pattern with representative paths at both root and nested
   locations using `git check-ignore --no-index -v --stdin`. Include directory
   descendants. Verify that the winning rule is an ignore rule, not a negation.
   Account for nested `.gitignore` overrides, testing actual artifact paths too.
   If exceptions keep artifacts unignored and cannot be resolved within the
   permitted root-file edit, return `FAIL` and explain the paths/rules involved.
5. Recheck tracked artifact paths. For each one still in the index, propose a
   properly shell-quoted `git rm --cached -- <path>` command for the user to
   review. Explain that this stops tracking the file while keeping its local
   copy; do not run it. Warn that untracking is a versioned deletion for others
   when that removal is committed. Do not suggest deleting local copies unless
   the user separately asks.

## Result

For a non-Git target, return `OK` with the skip warning above; this does not mean
Git checks ran or passed. For an applicable Git target, return `OK` only when
catalog artifacts are ignored and none are tracked/staged.
A successful `.gitignore` repair may produce `OK` if no tracked artifacts remain.
Return `FAIL` while tracked artifacts or ignore conflicts remain. In `message`,
list affected paths, describe `.gitignore` changes, and provide suggested removal
commands. If no repair was needed, say so. Never claim `.gitignore` removed an
already tracked file.
