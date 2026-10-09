# Initialize Hygienist

Use the target directory specified by the user, or the current working directory.
The target must already exist and be a directory. Resolve `.hygienist` within
that target, not within this global skill's source directory.

1. Inspect the target's `.hygienist` path, including symlinks.
2. If it is already a directory (including a symlink to a directory), leave it
   and its contents unchanged. Tell the user in their language:
   "You already have Hygienist here. Did you mean to add a rule?"
   For Ukrainian, use: "Та в тебе ж уже є `.hygienist`, може ти хотів просто додати правило?"
   Stop this initialization attempt without installing rules.
3. If the path is absent, create the `.hygienist` directory and verify it exists.
   Explain that it stores project checks as Markdown files named `NN-name.md`,
   where `NN` is at least two digits. Then offer the starter rules below.
4. If the path is a file, a broken symlink, or another non-directory entry,
   report the conflict without replacing it. Report creation or access failures
   without claiming initialization succeeded.

## Offer starter rules

After creating the directory, briefly describe all three options in the user's
language, including their repair behavior:

1. [Environment example](../templates/10-env-example.md): keep `.env.example`
   aligned with `.env` without copying values, and audit the example for secrets.
   May create or sanitize the example; never changes `.env`. Missing `.env`
   skips synchronization.
2. [OS artifacts](../templates/20-os-artifacts.md): keep macOS, Windows, and Linux
   system files out of Git. May update `.gitignore`; suggests untracking already
   indexed files without doing it automatically. Skips non-Git projects with
   a warning.
3. [Conflict markers](../templates/30-conflict-markers.md): detect unresolved
   merge markers and unmerged Git index entries. Reports findings without
   modifying files. Skips non-Git projects with a warning.

Ask which rules to add, allowing any subset, all three, or none. If the user's
initial request already specifies the selection, use it without asking again.
Otherwise wait for their choice; do not treat silence as selection. Declining
all rules leaves an initialized empty directory.

After selection, continue this initialization rather than restarting the
already-existing-directory branch. Read each selected template and copy its
contents into `.hygienist/`, retaining its basename if available or choosing an
unused numeric prefix of at least two digits. Check for existing files and never overwrite rules.
Verify the installed contents, then run the skill's
`scripts/renumber-rules.sh` with the target root after all selected copies are
complete. Follow the shared rule-change instructions in `SKILL.md` and report
the final paths returned by that helper. Report any
copy/access failure without claiming all selected rules were installed.

Do not copy scripts, schemas, or global skill instructions into the project.
Do not execute the rules or perform their repairs as part of initialization;
installing a rule only creates its Markdown file. If the user only asks how
initialization works, explain the behavior without creating files.
