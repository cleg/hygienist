# Keep .env.example aligned with .env without secrets

## Scope and permitted changes

Check only `.env` and `.env.example` at the target repository root. You may create
or update `.env.example`. Do not change `.env`, stage files, or commit changes.
Do not print secret values, raw file contents, or diffs containing old values.
Read and compare file contents in a local process whose output contains only
variable names and diagnostics. Do not source or execute either dotenv file,
expand variable references, or install dependencies.

## Check and repair

1. Inspect `.env`. If it is absent, skip synchronization without treating that
   as a failure. Do not create `.env` or `.env.example`. If `.env.example` also
   does not exist, return `OK` with "Skipped: neither .env nor .env.example exists."
   If the example exists, proceed directly to the independent secret audit in
   step 6. An existing but unreadable or non-regular `.env` is an access/path
   problem, not an absent source: report `FAIL` without modifying it.
2. When `.env` exists, parse dotenv assignments using the project's existing dotenv parser when
   available, or a local parser that supports the syntax actually present.
   Recognize comments, blank lines, optional `export`, quoted values, and
   multiline values. Never interpret a continuation line inside a quoted value
   as another variable. If parsing is ambiguous or unsupported, report `FAIL`
   with the affected line numbers, without values, and do not write a file.
   Treat duplicate variable definitions as ambiguous and report their names.
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
   verify that names match, all values are empty, and `.env` remains unchanged.

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
