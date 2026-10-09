#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: bash renumber-rules.sh <target-root>" >&2
  exit 2
fi

python3 - "$1" <<'PY'
import json
import os
import re
import sys
import tempfile
from pathlib import Path

root = Path(sys.argv[1]).resolve()
task_dir = root / ".hygienist"
if not task_dir.is_dir():
    print(f"Hygienist task directory not found: {task_dir}", file=sys.stderr)
    sys.exit(1)

pattern = re.compile(r"([0-9]{2,})-(.+)\.md")
rules = sorted(
    (path for path in task_dir.iterdir() if path.is_file() and pattern.fullmatch(path.name)),
    key=lambda path: (int(pattern.fullmatch(path.name)[1]), path.name),
)
plan = [
    (source, task_dir / f"{index * 10:02d}-{pattern.fullmatch(source.name)[2]}.md")
    for index, source in enumerate(rules, 1)
]
sources = {source for source, _ in plan}
for _, destination in plan:
    if os.path.lexists(destination) and destination not in sources:
        print(f"Cannot renumber: destination already exists: {destination}", file=sys.stderr)
        sys.exit(1)

changes = [(source, destination) for source, destination in plan if source != destination]
if changes:
    staging = Path(tempfile.mkdtemp(prefix=".renumber-", dir=task_dir))
    staged = []
    completed = []
    try:
        # Move all changing names aside before assigning any final name.
        for source, destination in changes:
            temporary = staging / source.name
            source.rename(temporary)
            staged.append((source, temporary, destination))
        for source, temporary, destination in staged:
            temporary.rename(destination)
            completed.append((source, temporary, destination))
    except OSError as error:
        recovery_errors = []
        for source, temporary, destination in reversed(completed):
            try:
                destination.rename(temporary)
            except OSError as recovery_error:
                recovery_errors.append(str(recovery_error))
        for source, temporary, _ in staged:
            if os.path.lexists(temporary):
                try:
                    temporary.rename(source)
                except OSError as recovery_error:
                    recovery_errors.append(str(recovery_error))
        if recovery_errors:
            print(f"Renumber failed: {error}. Recovery incomplete; inspect {staging}.", file=sys.stderr)
            for recovery_error in recovery_errors:
                print(recovery_error, file=sys.stderr)
        else:
            staging.rmdir()
            print(f"Renumber failed; original names restored: {error}", file=sys.stderr)
        sys.exit(1)
    staging.rmdir()

print(json.dumps({
    "renamed": [
        {"from": f".hygienist/{source.name}", "to": f".hygienist/{destination.name}"}
        for source, destination in changes
    ],
    "tasks": [f".hygienist/{destination.name}" for _, destination in plan],
}, ensure_ascii=False, indent=2))
PY
