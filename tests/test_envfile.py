"""Tests of the .env reader."""

import os
import tempfile
import unittest
from unittest import mock

from fr_open_data import envfile


class TestParse(unittest.TestCase):
    def test_syntax(self):
        text = (
            "# comment\n"
            "\n"
            "A=1\n"
            "export B = two words \n"
            "C=\"quoted # not a comment\"\n"
            "D='single'\n"
            "E=value # comment\n"
            "F=\n"
            "G=a=b\n"
        )
        self.assertEqual(envfile.parse(text), {
            "A": "1", "B": "two words", "C": "quoted # not a comment", "D": "single",
            "E": "value", "F": "", "G": "a=b",
        })

    def test_malformed_line_does_not_show_its_content(self):
        with self.assertRaises(ValueError) as ctx:
            envfile.parse("A=1\nsk-secret-value\n")
        self.assertIn("line 2", str(ctx.exception))
        self.assertNotIn("secret", str(ctx.exception))


class TestLoad(unittest.TestCase):
    def write(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".env", delete=False, encoding="utf-8")
        f.write(text)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def test_environment_wins_and_empty_values_are_ignored(self):
        path = self.write("FROM_FILE=file\nALREADY_SET=file\nEMPTY=\n")
        with mock.patch.dict(os.environ, {"ALREADY_SET": "terminal"}, clear=False):
            os.environ.pop("FROM_FILE", None)
            os.environ.pop("EMPTY", None)
            self.assertEqual(envfile.load(path), ["FROM_FILE"])
            self.assertEqual(os.environ["FROM_FILE"], "file")
            self.assertEqual(os.environ["ALREADY_SET"], "terminal")
            self.assertNotIn("EMPTY", os.environ)

    def test_missing_file(self):
        self.assertEqual(envfile.load(os.path.join(tempfile.gettempdir(), "does-not-exist.env")), [])


if __name__ == "__main__":
    unittest.main()
