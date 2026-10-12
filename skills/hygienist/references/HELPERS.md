# Maintain installed helpers

Helper maintenance is a deliberate parent operation requested by the user,
separate from installation, `run`, and read-only `inspect`. It never runs checks
or repairs unless separately requested. Global skill updates do not update
project copies; there is no automatic migration or garbage collection.

## Update or migrate

1. Read the installed code, candidate code, and all rules in the declared
   `.hygienist` directory, including non-discovered Markdown tasks. Inventory
   every helper dependency, command reference, local import, and supporting
   script referencing the helper. Use the shared path/link restrictions before
   reading or writing. Treat dynamic references or unavailable files as unknown
   dependents; do not claim the dependency inventory is complete.
2. Compare inputs, outputs, exit codes, runtime requirements, side effects, and
   invocation for **every** dependent rule. Compare installed template copies
   against the selected current template; preserve project adaptations. A
   matching filename does not prove version compatibility. Explain the planned
   changes within the requested migration scope before applying them.
3. Replace an existing regular helper only when the user requested its update,
   the dependent inventory is complete, and every dependent is compatible.
   Verify the candidate with synthetic fixtures according to `ADD-RULE.md`.
   Preserve the previous bytes for recovery until the batch is verified. Do not
   overwrite a file that changed since review or follow linked destinations.
4. For an incompatible version, use a new unused stable name such as
   `env-keys-v2.py`. Install it before updating only the selected dependent
   rules. Keep the old helper for remaining dependents; never make unrelated
   rules silently use a changed contract. If compatibility is uncertain, use
   a new name or leave the migration incomplete rather than replacing code.
5. Verify installed bytes and all updated references/contracts. Renumber after
   rule edits using the global procedure, never renumber helpers. Report old/new
   paths, migrated and remaining dependents, verification, and any incomplete
   steps. If a batch fails, identify the actual installed state and a bounded
   recovery plan; do not delete shared resources or claim migration finished.

## Remove

Deleting a rule never automatically deletes its helpers. Renumber the remaining
rules after deletion as usual. Orphaned helpers may remain deliberately.

Remove a helper only when explicitly requested and after checking all remaining
rule and supporting-code references, including non-discovered rules. If any
dependent remains, preserve it and explain the dependency; migrate or remove
those dependents only within the user's requested scope. Unavailable code or
dynamic references prevent a verified unused determination. Do not recursively
delete `helpers/`, follow links, or remove unrelated documentation/resources.
Report exactly which unused files were removed and which were retained.
