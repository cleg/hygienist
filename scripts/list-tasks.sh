#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: bash list-tasks.sh <target-root>" >&2
  exit 2
fi

python3 - "$1" <<'PY'
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
task_dir = root / ".hygienist"
if not task_dir.is_dir():
    print(f"Hygienist task directory not found: {task_dir}", file=sys.stderr)
    sys.exit(1)

tasks = [
    f".hygienist/{path.name}"
    for path in sorted(
        (path for path in task_dir.iterdir()
         if path.is_file() and re.fullmatch(r"[0-9]{2,}-.+\.md", path.name)),
        key=lambda path: (int(path.name.split("-", 1)[0]), path.name),
    )
]
print(json.dumps({"tasks": tasks}, ensure_ascii=False, indent=2))
PY
