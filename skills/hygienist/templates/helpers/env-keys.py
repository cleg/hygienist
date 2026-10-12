#!/usr/bin/env python3
"""Read root .env locally and emit keys only. Never evaluate dotenv values."""
import os
import re
import stat
import sys
from pathlib import Path

ASSIGNMENT = re.compile(r"[ \t]*(?:export[ \t]+)?([A-Za-z_][A-Za-z0-9_]*)[ \t]*=[ \t]*(.*)")


class InvalidDotenv(Exception):
    """Diagnostics contain controlled text and line numbers only."""


def keys_only(content):
    lines = content.replace("\r\n", "\n").split("\n")
    if "\x00" in content or "\r" in "\n".join(lines):
        raise InvalidDotenv("Unsupported control character in .env.")
    keys = []
    seen = set()
    index = 0
    while index < len(lines):
        line_number = index + 1
        line = lines[index]
        index += 1
        if not line.strip(" \t") or line.lstrip(" \t").startswith("#"):
            continue
        match = ASSIGNMENT.fullmatch(line)
        if not match:
            raise InvalidDotenv(f"Unsupported assignment at line {line_number}.")
        key, value = match.groups()
        if key in seen:
            raise InvalidDotenv(f"Duplicate key {key} at line {line_number}.")
        if value.startswith(("'", '"')):
            quote = value[0]
            remainder = value[1:]
            while True:
                escaped = False
                closing = None
                for position, character in enumerate(remainder):
                    if character == quote and not escaped:
                        closing = position
                        break
                    escaped = character == "\\" and not escaped
                if closing is not None:
                    tail = remainder[closing + 1:].lstrip(" \t")
                    if tail and not tail.startswith("#"):
                        raise InvalidDotenv(f"Unsupported quoted value at line {line_number}.")
                    break
                if index == len(lines):
                    raise InvalidDotenv(f"Unterminated quoted value at line {line_number}.")
                remainder = lines[index]
                index += 1
        else:
            # Do not guess at mixed quoting or backslash line continuations.
            literal = value.split("#", 1)[0].rstrip(" \t")
            if any(character in literal for character in ("'", '"', "\r", "\x00")) or literal.endswith("\\"):
                raise InvalidDotenv(f"Unsupported unquoted value at line {line_number}.")
        seen.add(key)
        keys.append(key)
    return "".join(f"{key}=\n" for key in keys)


def main(argv):
    if len(argv) != 2:
        print("Usage: python3 -I -B env-keys.py <target-root>", file=sys.stderr)
        return 2
    if os.name != "posix" or not all(hasattr(os, flag) for flag in ("O_NOFOLLOW", "O_NONBLOCK")):
        print("Unsupported platform: POSIX O_NOFOLLOW and O_NONBLOCK are required.", file=sys.stderr)
        return 1
    try:
        root = Path(argv[1])
        if not root.is_dir():
            print("Target root is not an accessible directory.", file=sys.stderr)
            return 1
        source = root / ".env"
        try:
            metadata = source.lstat()
        except FileNotFoundError:
            print("Skipped: .env is absent.", file=sys.stderr)
            return 3
        if not stat.S_ISREG(metadata.st_mode):
            print(".env must be a regular file, not a symlink.", file=sys.stderr)
            return 1
        # Reject link swaps; avoid blocking if the path is replaced by a FIFO.
        descriptor = os.open(source, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (metadata.st_dev, metadata.st_ino):
                print(".env changed or is not a regular file.", file=sys.stderr)
                return 1
            output = keys_only(stream.read().decode("utf-8"))
    except InvalidDotenv as error:
        print(str(error), file=sys.stderr)
        return 1
    except (OSError, UnicodeError, ValueError):
        print("Cannot read or decode .env.", file=sys.stderr)
        return 1
    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
