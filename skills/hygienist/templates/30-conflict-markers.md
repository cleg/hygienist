# Detect unresolved merge conflicts

## Scope and permitted changes

Check tracked and untracked non-ignored text files in the target Git repository.
Include tracked files even when an ignore rule matches them. Do not scan ignored
untracked files, `.git` internals, binary content, or submodule contents. Report
unmerged submodule entries in the Git index. This rule is read-only: do not resolve
conflicts or edit files automatically.

## Check

1. Check whether the target belongs to a Git working tree. If it does not,
   return `OK` with a warning in `message`: "Warning: skipped conflict checks
   because this is not a Git repository. No files were changed." Stop without
   scanning files or initializing Git. An unavailable Git executable or a Git
   access/configuration error is not evidence of a non-Git directory: report
   `FAIL` with the limitation instead. For an applicable Git working tree,
   verify that the target is its root; do not silently scan a parent repository
   when the target is a nested directory.
2. Check `git ls-files --unmerged -z`. Any entries mean unresolved conflicts,
   even if the working-tree text no longer contains markers.
3. Search tracked and untracked non-ignored text files for marker-shaped lines.
   For example, from the target root:

   ```sh
   git grep -n -I -E '^(<{7,}([[:blank:]].*)?|\|{7,}([[:blank:]].*)?|={7,}|>{7,}([[:blank:]].*)?)[[:space:]]*$' -- .
   git grep --untracked --exclude-standard -n -I -E '^(<{7,}([[:blank:]].*)?|\|{7,}([[:blank:]].*)?|={7,}|>{7,}([[:blank:]].*)?)[[:space:]]*$' -- .
   ```

   Run both searches and deduplicate path/line results: the tracked-only search
   retains tracked files that match ignore rules; the other includes non-ignored
   untracked files. Git grep returns 0 for matches, 1 for no matches, and a
   different status for errors. Treat errors as `FAIL`, not as a clean scan. This expression covers
   standard markers and longer configured markers. If `.gitattributes` uses a
   smaller `conflict-marker-size`, adapt the search for the affected paths.
   The trailing whitespace match also handles CRLF line endings.
4. Inspect candidates in file context. The marker types are an opening run of
   `<`, an optional diff3 base run of `|`, a separator run of `=`, and a closing
   run of `>`, all at the start of a line. Report complete unresolved blocks and
   leftover fragments. An isolated equals-only divider is not sufficient evidence
   of a conflict. Recognize clearly intentional marker examples in documentation
   or conflict-parser tests; explain any excluded candidates briefly.
5. Report affected file paths and one-based line numbers. Do not include entire
   file contents or secret values in the report. If required files cannot be
   read or a candidate cannot be distinguished from an intentional example,
   report the limitation rather than claiming the repository is clean.

## Result

For a non-Git target, return `OK` with the skip warning above; do not imply that
conflict checks ran or passed. For an applicable Git target, return `OK` only
when the index has no unmerged entries and the scoped scan finds no unresolved
markers or uncertain candidates. Return `FAIL` otherwise,
listing paths and line numbers, or the reason the scan could not complete.
This result covers the stated working-tree scope, not ignored files or history.
