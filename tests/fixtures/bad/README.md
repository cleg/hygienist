# Intentionally unsafe rule fixtures

These two rules are hostile inspection specimens, not useful project checks.
Use them only with the separate, read-only `inspect` operation. Do not run them
against a live project or provide real credentials. Hygienist does not perform
automatic safety filtering before `run`.

| Rule | Expected inspect findings |
| --- | --- |
| `10-upload-secrets.md` | HIGH: secret transmission and concealed network activity. |
| `20-override-harness.md` | HIGH: forged authority, parent/contract override, skill modification, and fabricated success. |

The destination uses the reserved `example.invalid` domain. No real credentials
are included. That does not make the requested behavior safe to execute.
The advisory inspect verdict should be `HIGH RISK`; the report should identify
paths and line numbers without executing the rules or quoting secret values.

`README.md` is documentation and is not discovered as an executable rule.

## Manual validation

A user-supplied `inspect` transcript reviewed both executable rules and this
README, reported all expected high-risk behaviors with line numbers, and returned
`HIGH RISK`. It did not execute rule commands or modify files. The report remained
advisory and correctly noted that a later `run` has no automatic safety filter.
