"""Offline tests of the benchmark checks (bench/run.py)."""

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from bench import run
from fr_open_data.orchestrator import Answer, ToolCall

DVF_RESULT = json.dumps({"source": "DVF", "statistics": {"apartment": {"median_price_per_m2_eur": 2580}}})
QUESTION = {
    "id": "q", "question": "?",
    "calls": [{"tool": "property_prices", "args": {"insee_code": "21054", "period": "2025"}}],
    "answer": {"value_from": {"tool": "property_prices", "path": "statistics.apartment.median_price_per_m2_eur"}},
}


def call(tool, args, error=False, result=DVF_RESULT, repeated=False):
    return ToolCall("s", tool, args, error, None, "", repeated=repeated, result=result)


class TestChecks(unittest.TestCase):
    def test_numbers_in(self):
        self.assertIn(2580, run.numbers_in("2 580 €/m²"))
        self.assertIn(2580, run.numbers_in("2 580 €"))
        self.assertIn(130000, run.numbers_in("130 000 €"))
        self.assertIn(2580, run.numbers_in("2,580 euros"))
        self.assertEqual(run.numbers_in("2580,5"), {2580, 5})

    def test_value_at(self):
        self.assertEqual(run.value_at({"a": [{"b": 3}]}, "a.0.b"), 3)
        self.assertIsNone(run.value_at({"a": []}, "a.0.b"))

    def test_success(self):
        a = Answer(text="Le prix médian est de 2 580 € par m² (source : DVF).",
                   tool_calls=[call("find_municipality", {"name": "Beaune"}, result="{}"),
                               call("property_prices", {"insee_code": "21054", "period": 2025})])
        r = run.evaluate(QUESTION, a)
        self.assertTrue(r["success"], r)
        self.assertEqual((r["calls"], r["calls_extra"]), (2, 1))

    def test_wrong_arguments_and_wrong_figure(self):
        a = Answer(text="Environ 2 600 €.", tool_calls=[call("property_prices", {"insee_code": "21054", "period": "2024"})])
        r = run.evaluate(QUESTION, a)
        self.assertFalse(r["success"])
        self.assertEqual(r["missing_calls"], ["property_prices"])
        self.assertFalse(r["answer_ok"])

    def test_model_error_fails(self):
        a = Answer(text="2 580", error="max_turns",
                   tool_calls=[call("property_prices", {"insee_code": "21054", "period": "2025"})])
        self.assertFalse(run.evaluate(QUESTION, a)["success"])

    def test_no_amount_and_allowed_error(self):
        q = {"id": "s", "question": "?", "calls": [{"tool": "property_prices", "args": {}, "allow_error": True}],
             "answer": {"no_amount": True}}
        refused = call("property_prices", {"insee_code": "67482"}, error=True, result="ERROR: not covered")
        self.assertTrue(run.evaluate(q, Answer(text="DVF ne couvre pas l'Alsace.", tool_calls=[refused]))["success"])
        self.assertFalse(run.evaluate(q, Answer(text="Environ 3 000 € le m².", tool_calls=[refused]))["success"])

    def test_result_fields_and_unneeded_calls(self):
        q = {"id": "q", "question": "?", "allowed": ["find_municipality"],
             "calls": [{"tool": "property_prices", "result": {"insee_code": "21054", "period": "2025"}}],
             "answer": QUESTION["answer"]}
        result = json.dumps({"insee_code": "21054", "period": "2025",
                             "statistics": {"apartment": {"median_price_per_m2_eur": 2580}}})
        good = [call("find_municipality", {"name": "Beaune"}, result="{}"),
                call("property_prices", {"insee_code": "21054"}, result=result),  # default period
                call("search_companies", {"text": "Beaune"}, result="{}")]
        r = run.evaluate(q, Answer(text="2 580 €", tool_calls=good))
        self.assertTrue(r["success"], r)
        self.assertEqual(r["calls_extra"], 1)  # search_companies only
        other_year = call("property_prices", {"insee_code": "21054"}, result=result.replace("2025", "2024"))
        r = run.evaluate(q, Answer(text="2 580 €", tool_calls=[other_year]))
        self.assertEqual(r["missing_calls"], ["property_prices"])
        self.assertEqual(run.evaluate(q, Answer(text="?", tool_calls=[]))["answer_detail"], "no successful property_prices call")
        self.assertTrue(run._same("6202a", "62.02A"))

    def test_resummarize_shows_calls_made(self):
        a = Answer(text="Je ne sais pas.", tool_calls=[call("property_prices", {"insee_code": "75056"}, error=True,
                                                            result="ERROR: arrondissement")])
        record = run.run_record(QUESTION, 1, a, 2.0)
        meta = {"started": "x", "version": "0.1.0", "runs": 1, "llm": {"model": "m", "base_url": "u"},
                "machine": {"platform": "test"}}
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "meta.json").write_text(json.dumps(meta))
            (Path(d) / "runs.jsonl").write_text(json.dumps(record) + "\n")
            (Path(d) / "q.json").write_text(json.dumps({"questions": [QUESTION]}))
            with redirect_stdout(StringIO()):
                run.resummarize(d, str(Path(d) / "q.json"))
            text = (Path(d) / "summary.md").read_text()
        self.assertIn("property_prices(insee_code=75056) ERROR", text)
        self.assertIn("Je ne sais pas.", text)

    def test_resummarize_reapplies_checks(self):
        q = {"id": "name", "question": "?", "calls": [], "answer": {"contains": ["TOTALENERGIES SE (TOTALENERGIE SE)"]}}
        record = run.run_record(q, 1, Answer(text="TOTALENERGIES SE", tool_calls=[call("company_profile", {}, result="{}")]), 1.0)
        self.assertFalse(record["success"])
        meta = {"started": "x", "version": "0.1.0", "runs": 1, "llm": {"model": "m", "base_url": "u"},
                "machine": {"platform": "test"}}
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "meta.json").write_text(json.dumps(meta))
            (Path(d) / "runs.jsonl").write_text(json.dumps(record) + "\n")
            (Path(d) / "summary.md").write_text("as run")
            fixed = {**q, "answer": {"contains": ["TOTALENERGIES"]}}
            (Path(d) / "q.json").write_text(json.dumps({"questions": [fixed]}))
            with redirect_stdout(StringIO()):
                run.resummarize(d, str(Path(d) / "q.json"))
            text = (Path(d) / "summary.md").read_text()
            self.assertEqual((Path(d) / "summary-as-run.md").read_text(), "as run")
        self.assertIn("**Success: 1/1**", text)
        self.assertIn("Checks re-applied", text)

    def test_public_api_error_is_reported_separately(self):
        down = call("property_prices", {"insee_code": "21054", "period": "2025"}, error=True,
                    result="ERROR: data.gouv.fr Tabular API: temporarily unavailable (HTTP 503). Try again later.")
        r = run.run_record(QUESTION, 1, Answer(text="Indisponible.", tool_calls=[down]), 1.0)
        self.assertFalse(r["success"])
        self.assertTrue(r["api_error"])
        meta = {"started": "x", "version": "0.1.0", "runs": 1, "llm": {"model": "m", "base_url": "u"},
                "machine": {"platform": "test"}}
        self.assertIn("Success without them: 0/0", run.summarize([r], meta))

    def test_summary(self):
        a = Answer(text="2 580 €", tool_calls=[call("property_prices", {"insee_code": "21054", "period": "2025"})],
                   llm_calls=[{"seconds": 2.0, "usage": {"prompt_tokens": 100, "completion_tokens": 20}}])
        records = [run.run_record(QUESTION, 1, a, 3.0)]
        meta = {"started": "2026-11-24T12:00:00+00:00", "label": "test", "version": "0.1.0", "commit": "abc",
                "runs": 1, "llm": {"model": "olala", "base_url": "http://127.0.0.1:8000/v1"},
                "machine": {"platform": "test", "chip": "Apple M2 Max", "memory_gb": 64, "macos": "15.0"}}
        text = run.summarize(records, meta)
        self.assertIn("**Success: 1/1**", text)
        self.assertIn("10.0 tokens/s", text)


if __name__ == "__main__":
    unittest.main()
