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

    def test_cites_source(self):
        dvf_result = json.dumps({"source": "DVF géolocalisées (DGFiP, processed by data.gouv.fr)"})
        company = json.dumps({"source": "Recherche d'entreprises API (DINUM) - Sirene (INSEE) and RNE (INPI) data"})
        geo = json.dumps({"source": "Découpage administratif API (geo.api.gouv.fr)"})
        self.assertTrue(run.cites_source("2 580 € (source : DVF)", [dvf_result]))
        self.assertTrue(run.cites_source("Selon les demandes de valeurs foncières…", [dvf_result]))
        self.assertFalse(run.cites_source("2 580 €.", [dvf_result]))
        self.assertTrue(run.cites_source("Source : API Recherche d’entreprises.", [company]))
        self.assertFalse(run.cites_source("Une entreprise interne concernée.", [company]))  # no "rne" inside words
        self.assertTrue(run.cites_source("Code 21054 (source : geo.api.gouv.fr)", [geo]))
        self.assertTrue(run.cites_source("Code 21054 (API Géo)", [geo]))
        self.assertIsNone(run.cites_source("Pas de données.", ["ERROR: not covered"]))
        self.assertIsNone(run.cites_source("x", []))

    def test_truncated_result_keeps_leading_fields(self):
        full = json.dumps({"source": "S", "filters": {"code_commune": "33063", "activite_principale": "56.10A"},
                           "total_results": 1490, "results": [{"name": "X" * 50}] * 200})
        cut = full[:8000] + " [...truncated]"
        fields = run.leading_fields(cut)
        self.assertEqual(fields["total_results"], 1490)
        self.assertEqual(fields["filters"]["code_commune"], "33063")
        self.assertNotIn("results", fields)
        q = {"id": "c", "question": "?",
             "calls": [{"tool": "search_companies", "result": {"filters.code_commune": "33063",
                                                                "filters.activite_principale": "56.10A"}}],
             "answer": {"value_from": {"tool": "search_companies", "path": "total_results"}}}
        r = run.evaluate(q, Answer(text="1490 entreprises actives.", tool_calls=[call("search_companies", {}, result=cut)]))
        self.assertTrue(r["success"], r)

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

    def test_profiler_fields_and_machine_text(self):
        hw = "Hardware:\n\n    Hardware Overview:\n\n      Model Name: MacBook Pro\n      Model Identifier: Mac14,6\n" \
             "      Chip: Apple M2 Max\n      Total Number of Cores: 12 (8 performance and 4 efficiency)\n      Memory: 32 GB\n"
        gpu = "Graphics/Displays:\n\n    Apple M2 Max:\n\n      Chipset Model: Apple M2 Max\n      Type: GPU\n" \
              "      Total Number of Cores: 38\n      Metal Support: Metal 3\n"
        self.assertEqual(run.profiler_field(hw, "Total Number of Cores"), "12 (8 performance and 4 efficiency)")
        self.assertEqual(run.profiler_field(gpu, "Total Number of Cores"), "38")
        self.assertIsNone(run.profiler_field(None, "Model Name"))
        m = {"model": "MacBook Pro", "model_id": "Mac14,6", "chip": "Apple M2 Max", "cpu_cores": "12", "gpu_cores": "38",
             "memory_gb": 32, "macos": "15.0", "platform": "x"}
        self.assertEqual(run.machine_text(m), "MacBook Pro (Mac14,6), Apple M2 Max, CPU 12 cores, GPU 38 cores, "
                                              "32 GB memory, macOS 15.0")
        self.assertEqual(run.machine_text({"platform": "Linux"}), "Linux, ? GB memory")

    def test_validation_checks(self):
        q = {"id": "q", "question": "?",
             "calls": [{"tool": "property_prices", "result": {"insee_code": "21054", "period": "2025"}}],
             "answer": QUESTION["answer"]}
        v = {"tool": "property_prices", "args": {"municipality": "Beaune", "period": "2025"}}
        good = json.dumps({"insee_code": "21054", "period": "2025",
                           "statistics": {"apartment": {"median_price_per_m2_eur": 2580}}})
        self.assertEqual(run.check_validation(q, v, False, good), ([], 2580))
        problems, _ = run.check_validation(q, v, False, good.replace("21054", "21231"))
        self.assertTrue(problems)
        problems, _ = run.check_validation(q, v, True, "ERROR: down")
        self.assertIn("tool error", problems[0])
        refused = {**v, "expect_error": "does not cover"}
        self.assertEqual(run.check_validation(q, refused, True, "DVF does not cover Alsace")[0], [])
        self.assertTrue(run.check_validation(q, refused, False, good)[0])

    def test_load_questions_and_ollama_config(self):
        from fr_open_data.orchestrator import check_config, remote_llm_host
        both = run.load_questions([str(run.HERE / "questions_holdout.json"), str(run.HERE / "questions_holdout2.json")])
        self.assertEqual(len(both), 24)
        with self.assertRaisesRegex(ValueError, "used twice"):
            run.load_questions([str(run.HERE / "questions.json")] * 2)
        cfg = json.loads((run.HERE / "config.ollama.json").read_text(encoding="utf-8"))
        check_config(cfg)
        self.assertIsNone(remote_llm_host(cfg["llm"]))
        self.assertIsNone(cfg["llm"]["tool_choice"])
        meta = {"started": "x", "version": "0.1.0", "runs": 1, "llm": {"model": "m", "base_url": "u"},
                "machine": {"platform": "test"},
                "questions_file": ["bench/questions_holdout.json", "bench/questions_holdout2.json"]}
        text = run.summarize([], meta)
        self.assertIn("`questions_holdout.json`, `questions_holdout2.json`", text)

    def test_holdout2_file(self):
        data = json.loads((Path(run.HERE) / "questions_holdout2.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["questions"]), 16)
        self.assertEqual(len({q["id"] for q in data["questions"]}), 16)
        for q in data["questions"]:
            self.assertTrue(q.get("validate"), q["id"])
            self.assertTrue(q.get("answer"), q["id"])

    def test_validate_runs_the_tools(self):
        from unittest import mock

        import anyio
        from mcp.server.mcpserver import MCPServer
        from mcp.server.mcpserver.exceptions import ToolError

        srv = MCPServer(name="fake")

        @srv.tool()
        def property_prices(municipality: str = "", period: str = "") -> str:
            """Fake DVF."""
            if municipality == "Colmar":
                raise ToolError("DVF does not cover Alsace")  # like fr_open_data.server._run
            return json.dumps({"insee_code": "21054", "period": period,
                               "statistics": {"apartment": {"median_price_per_m2_eur": 2580}}})

        ok_q = {"id": "ok", "question": "?", "answer": QUESTION["answer"],
                "calls": [{"tool": "property_prices", "result": {"insee_code": "21054", "period": "2025"}}],
                "validate": [{"tool": "property_prices", "args": {"municipality": "Beaune", "period": "2025"}}]}
        refused = {"id": "colmar", "question": "?", "calls": [], "answer": {"no_amount": True},
                   "validate": [{"tool": "property_prices", "args": {"municipality": "Colmar"}, "expect_error": "does not cover"}]}
        wrong = {**ok_q, "id": "wrong", "calls": [{"tool": "property_prices", "result": {"insee_code": "99999"}}]}
        with mock.patch("fr_open_data.server.build_server", return_value=srv), redirect_stdout(StringIO()) as out:
            self.assertTrue(anyio.run(run.validate, [ok_q, refused]))
            self.assertFalse(anyio.run(run.validate, [wrong]))
        self.assertIn("OK   ok: property_prices", out.getvalue())
        self.assertIn("-> 2580", out.getvalue())
        self.assertIn("FAIL wrong", out.getvalue())

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
