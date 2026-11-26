"""Tests of .githooks/privacy_check.py (the checks run before a commit and before a push)."""

import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / ".githooks" / "privacy_check.py"
spec = importlib.util.spec_from_file_location("privacy_check", HOOK)
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)

NOREPLY = "123+someone@users.noreply.github.com"
# Built in pieces so that this file does not trip the check itself.
MAC_HOME = "/" + "Users/account1/project/bench/questions.json"
LINUX_HOME = "/" + "home/account2/work/meta.json"
WIN_HOME = "C:" + "\\" + "Users\\account3\\data"


class PureFunctions(unittest.TestCase):
    def test_noreply(self):
        self.assertTrue(pc.is_noreply(NOREPLY))
        self.assertTrue(pc.is_noreply("someone@users.noreply.github.com"))
        self.assertFalse(pc.is_noreply("someone@example.com"))
        self.assertFalse(pc.is_noreply("noreply@example.com"))

    def test_home_paths(self):
        self.assertEqual(len(pc.home_paths(f'"questions_file": "{MAC_HOME}"')), 1)
        self.assertEqual(len(pc.home_paths(LINUX_HOME)), 1)
        self.assertEqual(len(pc.home_paths(WIN_HOME)), 1)
        for placeholder in ("/" + "Users/<name>/x", "/" + "home/$USER/x", "/" + "Users/NAME/x",
                            "/" + "home/user/x", "~/Documents/x", "bench/questions.json"):
            self.assertEqual(pc.home_paths(placeholder), [], placeholder)

    def test_private_words_ignore_case_and_accents(self):
        self.assertEqual(pc.words_in("Signed: ÉPÉE", ["epee"]), ["epee"])
        self.assertEqual(pc.words_in("nothing here", ["secretword"]), [])

    def test_raw_runs(self):
        self.assertTrue(pc.is_raw_run("bench/results/20261125-100314/runs.jsonl"))
        self.assertTrue(pc.is_raw_run("runs.jsonl"))
        self.assertFalse(pc.is_raw_run("bench/results/20261125-100314/summary.md"))

    def test_added_lines(self):
        diff = ("diff --git a/x b/x\n--- a/x\n+++ b/x\n@@ -1 +1 @@\n-old\n+new line\n"
                "diff --git a/y b/y\n--- /dev/null\n+++ b/y\n@@ -0,0 +1 @@\n+other\n")
        self.assertEqual(pc.added_lines(diff), [("x", "new line"), ("y", "other")])


class InRepository(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.env = dict(os.environ, GIT_AUTHOR_NAME="Someone", GIT_AUTHOR_EMAIL=NOREPLY,
                        GIT_COMMITTER_NAME="Someone", GIT_COMMITTER_EMAIL=NOREPLY,
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        self._saved = {k: os.environ.get(k) for k in self.env}
        os.environ.update(self.env)
        self.git("init", "-q", "-b", "main")
        Path(self.dir, ".git", "info").mkdir(exist_ok=True)
        Path(self.dir, ".git", "info", "private-words").write_text("# private\nSecretword\n")

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.dir, check=True, capture_output=True,
                              text=True).stdout

    def write(self, name, text):
        path = Path(self.dir, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        self.git("add", "-f", name)

    def test_clean_commit_passes(self):
        self.write("bench/results/r/summary.md", "Success: 10/10\n")
        self.assertEqual(pc.check_staged(self.dir), [])

    def test_raw_runs_home_path_and_private_word_refused(self):
        self.write("bench/results/r/runs.jsonl", "{}\n")
        self.write("bench/results/r/meta.json", f'{{"questions_file": "{MAC_HOME}"}}\n')
        self.write("notes.md", "Written by Secretword\n")
        problems = "\n".join(pc.check_staged(self.dir))
        self.assertIn("runs.jsonl", problems)
        self.assertIn("absolute home path", problems)
        self.assertIn("private word", problems)

    def test_identity_refused(self):
        os.environ["GIT_AUTHOR_EMAIL"] = "someone@example.com"
        os.environ["GIT_COMMITTER_NAME"] = "Test Secretword"
        self.write("a.txt", "a\n")
        problems = "\n".join(pc.check_staged(self.dir))
        self.assertIn("author email", problems)
        self.assertIn("committer identity contains a private word", problems)

    def test_push_checks_every_new_commit(self):
        self.write("a.txt", "a\n")
        self.git("commit", "-q", "-m", "clean")
        clean = self.git("rev-parse", "HEAD").strip()
        self.assertEqual(pc.check_push([f"refs/heads/main {clean} refs/heads/main {'0' * 40}"],
                                       "origin", self.dir), [])
        self.write("bench/results/r/runs.jsonl", "{}\n")
        self.git("commit", "-q", "-m", "add raw runs")
        os.environ["GIT_AUTHOR_EMAIL"] = "someone@example.com"
        self.write("b.txt", "b\n")
        self.git("commit", "-q", "-m", "by Secretword")
        head = self.git("rev-parse", "HEAD").strip()
        problems = "\n".join(pc.check_push([f"refs/heads/main {head} refs/heads/main {clean}"],
                                           "origin", self.dir))
        self.assertIn("runs.jsonl", problems)
        self.assertIn("author email", problems)
        self.assertIn("message contains a private word", problems)
        self.assertNotIn(f"commit {clean[:7]}", problems)
        # Deleting a remote branch sends nothing.
        self.assertEqual(pc.check_push([f"(delete) {'0' * 40} refs/heads/x {clean}"], "origin",
                                       self.dir), [])


if __name__ == "__main__":
    unittest.main()
