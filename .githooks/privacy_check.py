"""Refuse commits and pushes that would publish personal data.

Enable once in each clone:

    git config core.hooksPath .githooks

What is refused:
- an author or committer email that is not a GitHub noreply address
  (ID+USERNAME@users.noreply.github.com), so that a real name and email set as the default
  Git identity of the machine are not published;
- a file named runs.jsonl: raw benchmark runs keep the full tool results, which include
  personal data from public registers (names of company directors);
- an absolute path to a home folder (/Users/NAME/, /home/NAME/, C:\\Users\\NAME\\), which
  holds the name of the account;
- any word listed in the file .git/info/private-words (one per line, for example your real
  name). That file lives in .git, so it is never committed.

`git commit --no-verify` and `git push --no-verify` skip these checks.
Standard library only, Python 3.9 or later (the python3 of macOS).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import unicodedata

NOREPLY = re.compile(r"^(\d+\+)?[A-Za-z0-9-]+@users\.noreply\.github\.com$")
HOME_PATH = re.compile(r"(?:/(?:Users|home)/|[A-Za-z]:\\+Users\\+)([^/\\\s\"'`<>]+)")
PLACEHOLDERS = {"", "user", "username", "you", "me", "name", "runner", "example", "shared",
                "$user", "${user}", "%username%", "~"}
RAW_RUNS = "runs.jsonl"
ZERO = re.compile(r"^0+$")


def git(*args: str, cwd: str | None = None) -> str:
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {out.stderr.strip()}")
    return out.stdout


def fold(text: str) -> str:
    """Lower case without accents, so that 'Élodie' matches 'elodie'."""
    text = unicodedata.normalize("NFKD", text.casefold())
    return "".join(c for c in text if not unicodedata.combining(c))


def is_noreply(email: str) -> bool:
    return bool(NOREPLY.match(email.strip()))


def home_paths(text: str) -> list[str]:
    """Absolute paths to a real home folder; placeholders such as /Users/<name>/ are allowed."""
    found = []
    for m in HOME_PATH.finditer(text):
        name = m.group(1)
        if fold(name) in PLACEHOLDERS or name.startswith(("$", "%", "{", "<")):
            continue
        found.append(m.group(0))
    return found


def private_words(cwd: str | None = None) -> list[str]:
    path = git("rev-parse", "--git-path", "info/private-words", cwd=cwd).strip()
    if cwd and not os.path.isabs(path):
        path = os.path.join(cwd, path)
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return []
    return [w.strip() for w in lines if w.strip() and not w.strip().startswith("#")]


def words_in(text: str, words: list[str]) -> list[str]:
    folded = fold(text)
    return [w for w in words if fold(w) in folded]


def is_raw_run(path: str) -> bool:
    return path.replace("\\", "/").rsplit("/", 1)[-1] == RAW_RUNS


def added_lines(diff: str) -> list[tuple[str, str]]:
    """(file, line) for each line a unified diff adds."""
    lines, current = [], ""
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else line[4:]
        elif line.startswith("+") and not line.startswith("+++"):
            lines.append((current, line[1:]))
    return lines


def check_identity(label: str, name: str, email: str, words: list[str]) -> list[str]:
    problems = []
    if not is_noreply(email):
        problems.append(f"{label} email {email!r} is not a GitHub noreply address "
                        "(set one with: git config user.email ID+USERNAME@users.noreply.github.com)")
    for w in words_in(f"{name} {email}", words):
        problems.append(f"{label} identity contains a private word ({w!r})")
    return problems


def check_changes(files: list[str], diff: str, words: list[str], where: str) -> list[str]:
    problems = []
    for path in files:
        if is_raw_run(path):
            problems.append(f"{where}{path}: raw benchmark runs are never committed (personal data)")
    for path, line in added_lines(diff):
        for p in home_paths(line):
            problems.append(f"{where}{path}: absolute home path {p!r} (use a path relative to the repository)")
        for w in words_in(line, words):
            problems.append(f"{where}{path}: contains a private word ({w!r})")
    return problems


def ident(var: str, cwd: str | None = None) -> tuple[str, str]:
    """Name and email from `git var GIT_AUTHOR_IDENT` ('Name <email> time zone')."""
    m = re.match(r"^(.*?) <([^>]*)>", git("var", var, cwd=cwd).strip())
    return (m.group(1), m.group(2)) if m else ("", "")


def check_staged(cwd: str | None = None) -> list[str]:
    words = private_words(cwd)
    problems = []
    for label, var in (("author", "GIT_AUTHOR_IDENT"), ("committer", "GIT_COMMITTER_IDENT")):
        problems += check_identity(label, *ident(var, cwd), words)
    files = [f for f in git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z",
                            cwd=cwd).split("\0") if f]
    diff = git("diff", "--cached", "-U0", "--no-color", "--no-ext-diff", cwd=cwd)
    problems += check_changes(files, diff, words, "")
    return problems


def empty_tree(cwd: str | None = None) -> str:
    return subprocess.run(["git", "hash-object", "-t", "tree", "--stdin"], cwd=cwd, input="",
                          capture_output=True, text=True, check=True).stdout.strip()


def check_commit(sha: str, words: list[str], cwd: str | None = None) -> list[str]:
    fields = git("log", "-1", "--format=%an%x00%ae%x00%cn%x00%ce%x00%P%x00%B", sha, cwd=cwd)
    an, ae, cn, ce, parents, message = fields.split("\0", 5)
    where = f"commit {sha[:7]}: "
    problems = [where + p for p in check_identity("author", an, ae, words)
                + check_identity("committer", cn, ce, words)]
    for p in home_paths(message):
        problems.append(f"{where}message contains an absolute home path {p!r}")
    for w in words_in(message, words):
        problems.append(f"{where}message contains a private word ({w!r})")
    base = parents.split()[0] if parents.split() else empty_tree(cwd)
    files = [f for f in git("diff", "--name-only", "--diff-filter=ACMR", "-z", base, sha,
                            cwd=cwd).split("\0") if f]
    diff = git("diff", "-U0", "--no-color", "--no-ext-diff", base, sha, cwd=cwd)
    return problems + check_changes(files, diff, words, where)


def commits_to_push(lines: list[str], remote: str, cwd: str | None = None) -> list[str]:
    """Commits that the push would send and that the remote does not have yet."""
    shas: list[str] = []
    for line in lines:
        parts = line.split()
        if len(parts) != 4 or ZERO.match(parts[1]):
            continue  # malformed line, or a branch deletion
        exclude = [f"--remotes={remote}"] if remote else []
        if not ZERO.match(parts[3]):
            known = subprocess.run(["git", "cat-file", "-e", parts[3] + "^{commit}"], cwd=cwd,
                                   capture_output=True).returncode == 0
            if known:
                exclude.append(parts[3])
        for sha in git("rev-list", parts[1], "--not", *exclude, cwd=cwd).split():
            if sha not in shas:
                shas.append(sha)
    return shas


def check_push(lines: list[str], remote: str, cwd: str | None = None) -> list[str]:
    words = private_words(cwd)
    problems = []
    for sha in commits_to_push(lines, remote, cwd):
        problems += check_commit(sha, words, cwd)
    return problems


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else ""
    if mode == "pre-commit":
        problems = check_staged()
    elif mode == "pre-push":
        remote = argv[2] if len(argv) > 2 else ""
        problems = check_push(sys.stdin.read().splitlines(), remote)
    else:
        print("usage: privacy_check.py pre-commit | pre-push REMOTE [URL]", file=sys.stderr)
        return 2
    if not problems:
        return 0
    print(f"Refused by .githooks/privacy_check.py ({mode}):", file=sys.stderr)
    for p in problems[:50]:
        print(f"  - {p}", file=sys.stderr)
    if len(problems) > 50:
        print(f"  ... and {len(problems) - 50} more", file=sys.stderr)
    print("Fix the problem, or skip the check with --no-verify if it is a false alarm.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
