"""Read a .env file into the environment (standard library only).

Supported syntax: one KEY=VALUE per line, blank lines, lines starting with #,
an optional "export " prefix, values in single or double quotes, and a comment
after an unquoted value when preceded by a space (KEY=value # comment).
No variable expansion and no multi-line values.

A variable already set in the environment is never overridden, and an empty
value is ignored, so that `export KEY=...` in the terminal always wins.
"""

from __future__ import annotations

import os
import re

_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def parse(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        key, sep, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if not sep or not _KEY.fullmatch(key):
            # The line itself is not quoted: it may contain a secret.
            raise ValueError(f"line {n}: expected KEY=VALUE")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        values[key] = value
    return values


def load(path: str = ".env") -> list[str]:
    """Set the variables of `path` that are not already set; return their names.

    A missing file is not an error. A malformed line raises ValueError.
    """
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return []
    loaded = []
    for key, value in parse(text).items():
        if value and key not in os.environ:
            os.environ[key] = value
            loaded.append(key)
    return loaded
