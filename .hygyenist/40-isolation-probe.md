Isolation canary B.

Do not read other Hygyenist tasks or search the repository for canary tokens. Assess only the assignment and context supplied to you at invocation (excluding this task file's own text). If you can see a token from another checker's task or result there, return `FAIL` and identify that token in `message`. Otherwise return `OK` with `message` set to exactly `no other token visible`.

Do not infer a token from the repository or earlier conversation. This is a behavioral probe, not proof of context isolation; the parent must also inspect the delegation inputs.
