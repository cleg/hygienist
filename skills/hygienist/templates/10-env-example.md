# Keep .env.example aligned with .env without secrets

## Helper dependencies

Installation metadata for `init`/`add-rule` only; this section is not an
installation instruction for a checker, even when copied into an installed rule.

- Bundled source (relative to the skill root): `templates/helpers/env-keys.py`.
- Installed destination (relative to the target root): `.hygienist/helpers/env-keys.py`.
- Runtime: Python 3 on POSIX (macOS/Linux), with `os.O_NOFOLLOW` and `os.O_NONBLOCK`, standard library only; invocation must include `-I -B`.

This is the only helper required by the template. During a check it must already
be installed; the checker must not install it or substitute the bundled source.

## Scope and permitted changes

Check only `.env` and `.env.example` at the target repository root. You may create
or update `.env.example`. Do not change `.env`, stage files, or commit changes.
Do not print secret values, raw file contents, or diffs containing old values.
Never read `.env` directly into agent context. Obtain its keys only from the
installed helper's output. Do not bypass it with another parser, inline script,
file reader, shell command, or tool. You may read `.env.example` for its audit,
but do not expose its sensitive contents in tool output or reports. Do not source
or execute either dotenv file, expand variable references, or install dependencies.

## Check and repair

1. Resolve `.hygienist/helpers/env-keys.py` from the target root. Before
   executing it, inspect the path without following links below the declared
   `.hygienist` directory. Require `helpers/` to be an actual directory and
   `env-keys.py` to be a readable regular file; reject symlinks at either path,
   including broken links or links pointing inside the directory. Check parents
   first, one component at a time. Stop at the first invalid component without
   inspecting its children, even with `lstat` (which follows intermediate links). An explicitly
   selected `.hygienist` directory symlink is allowed: disclose its destination
   and check `helpers/` and the helper within that declared destination.
   If any component is missing, conflicting, or cannot be verified, return
   `FAIL` without executing the helper or reading `.env`.
   From the target root, run `python3 -I -B .hygienist/helpers/env-keys.py "<target-root>"`,
   replacing `<target-root>` with the actual target path. Do not create, modify,
   or replace the helper during a check. If Python or the helper is unavailable,
   return `FAIL`; never fall back to reading `.env` yourself or dropping the
   isolation flags.
2. Use only stdout from a successful helper invocation as the source keys.
   Exit `0` means stdout contains only ordered `NAME=` assignments (possibly
   empty). Exit `3` means `.env` is absent: skip synchronization, create neither
   dotenv file, and proceed to step 6 if `.env.example` exists. If both files are
   absent, return `OK` with "Skipped: neither .env nor .env.example exists."
   Any other exit code means `FAIL`, without writing the example. The helper
   rejects duplicate keys, unsupported syntax, unreadable/non-regular files,
   and symlinks; its diagnostics contain no values. Do not inspect the original
   file to diagnose a failure. Validate successful stdout consists only of
   unique lines matching `[A-Za-z_][A-Za-z0-9_]*=`; invalid output means `FAIL`.
3. The desired example contains exactly the variable names from `.env`, in their
   first-occurrence order, with each assignment written as `NAME=`. All values
   must be empty, including non-secret defaults: this avoids guessing which
   values are confidential. Do not copy source comments, which can also contain
   secrets. A header explaining that users must supply their own values is fine.
4. If `.env.example` is absent, create it. If it exists, check that it parses,
   contains exactly those variable names once each, and has only empty values.
   Check comments and other text too: use the canonical content from step 3
   when repairing, so old secrets cannot remain in comments or multiline text.
   Refuse to overwrite a directory or symlink at `.env.example`.
5. If the existing example already has canonical content, leave it unchanged.
   Otherwise replace its contents with the canonical example. Re-read it and
   verify that names match the successful helper output and all values are empty.
   Do not read `.env` to verify this; the helper is read-only and repairs must
   address only `.env.example`.

6. Audit the final `.env.example` independently for accidentally included secrets,
   after synchronization or even when `.env` was absent. Require a readable
   regular file; refuse to modify symlinks or non-regular paths. Examine all
   assignments, comments, and multiline content, not only variable names.
   Use an existing local secret scanner when available, with output redacted;
   otherwise inspect locally for tokens/API keys, passwords, private-key blocks,
   connection strings or URLs containing credentials, and other concrete secret
   indicators. Variable names such as `API_KEY` alone and obvious empty/example
   placeholders are not secrets. Never submit file contents to external services.
7. Remove detected secrets from the example: clear affected assignment values
   to `NAME=`, and remove secret-bearing comments or standalone text. Without
   `.env`, preserve unrelated keys, safe example values, and comments; do not
   perform key synchronization or clear every value merely because the source
   is absent. Re-read the file and repeat the audit after any repair. If syntax
   prevents a reliable repair, access fails, or a suspected secret cannot be
   resolved confidently, return `FAIL` with names/line numbers and the limitation,
   without exposing values. Do not claim a heuristic audit proves that no
   possible secret exists; state the method and scope actually checked.

## Result

Return `OK` when applicable synchronization and the independent secret audit
complete successfully, including after repair, or when both files are absent.
A missing `.env` alone is never a failure. In `message`, state whether alignment
was skipped, already correct, created, or updated, and summarize the secret audit
and any sanitization without revealing secrets. Include
only variable names/counts and paths, never source values or removed contents.
Return `FAIL` if parsing, access, writing, or verification fails. This check
ensures a sanitized current example; it does not remove secrets from Git history.
