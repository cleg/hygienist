#!/usr/bin/env bash
set -euo pipefail

task_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

python3 - "$task_dir" <<'PY'
import json
import re
import sys
from pathlib import Path

task_dir = Path(sys.argv[1])
tasks = [
    f".hygyenist/{path.name}"
    for path in sorted(task_dir.iterdir(), key=lambda path: path.name)
    if path.is_file() and re.fullmatch(r"[0-9]{2}-.+\.md", path.name)
]
print(json.dumps({"tasks": tasks}, ensure_ascii=False, indent=2))
PY
