"""Benchmark: ask fixed questions to the configured model, several times, and check the answers.

  python -m bench.run --config config.json --runs 3 --label "Olala q5e6, MacBook Pro M2 Max"

For each run of each question (bench/questions_dev.json or bench/questions_test.json), it
records the tools called, their arguments, results and duration, the model requests
(duration and token counts when the server reports them), and checks:
- that the expected tool calls succeeded with the expected arguments, or returned the
  expected data (e.g. the DVF result is for the right municipality and year);
- that the answer contains the figure returned by the tool in this run (or the expected
  text, or no euro amount when the data does not exist);
- that the model did not fail (error, or no answer within max_turns).

Results go to bench/results/<date>-<time>/: meta.json (machine, model, configuration),
runs.jsonl (one line per run, with the full answer and tool results; never committed: it
includes personal data from public registers) and summary.md (tables to publish).
meta.json is written when the run starts and again when it ends: the meta.json of an
interrupted run has no "finished" time.
The memory used by the model server is not measured: read it in Activity Monitor.

  python -m bench.run --summarize latest     # rebuild summary.md of the latest results

  python -m bench.run --validate --questions bench/questions_test.json
                                              # check the questions against the tools, no model

--validate calls the tools directly with the arguments given in each question's 'validate'
entries and checks that the data needed by the question exists (right municipality and
period, a figure at the expected place, the expected error for areas DVF does not cover).
It needs no model and no config, only Internet access to the public APIs.

--summarize re-applies the checks of the current questions file to the stored answers and
tool results (the model is not run again). The summary written during the run is kept as
summary-as-run.md, and the new summary says when and with what the checks were re-applied.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import re
import statistics
import unicodedata
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

import anyio

from fr_open_data import __version__, envfile
from fr_open_data.orchestrator import (Answer, ToolCall, api_key, check_config, from_config, load_config,
                                       remote_llm_host, tool_arguments, warn_if_remote)

HERE = Path(__file__).resolve().parent
_SEPARATOR = re.compile(r"(?<=\d)[\s   .,'](?=\d{3}(?!\d))")  # thousands separators
_EURO_AMOUNT = re.compile(r"\d[\d\s   .,]*\s*(€|euros?\b|EUR\b)", re.IGNORECASE)
# Messages of fr_open_data/http.py when a public API fails: not the model's fault.
API_ERROR_MARKERS = ("unreachable", "temporarily unavailable", "too many requests", "failed after retry")
# Words showing that an answer names the source of the data (case and accents ignored, whole words),
# by source of the tool result. Not part of the success criterion.
SOURCE_WORDS = {
    "dvf": ("dvf", "valeurs foncieres"),
    "recherche d'entreprises": ("recherche d'entreprises", "recherche d entreprises", "sirene", "rne", "inpi"),
    "decoupage administratif": ("decoupage administratif", "geo api gouv fr", "api geo"),
    "legifrance": ("legifrance",),
}


# ---------------------------------------------------------------- checks

def numbers_in(text: str) -> set[int]:
    """Integers written in a text, accepting thousands separators ("2 580", "130 000", "2,580")."""
    return {int(n) for n in re.findall(r"(?<!\d)\d+(?!\d)", _SEPARATOR.sub("", text or ""))}


def value_at(data: Any, path: str) -> Any:
    for part in path.split("."):
        if isinstance(data, list) and part.isdigit() and int(part) < len(data):
            data = data[int(part)]
        elif isinstance(data, dict):
            data = data.get(part)
        else:
            return None
    return data


def _code(value: Any) -> str:
    return re.sub(r"[\s.]+", "", str(value)).upper()


def _same(actual: Any, expected: Any) -> bool:
    """Compare codes and years, ignoring case, spaces and dots ("62.02A" = "6202a")."""
    return _code(actual) == _code(expected)


_KEY_SEP = re.compile(r"\s*,?\s*")
_COLON = re.compile(r"\s*:\s*")


def leading_fields(text: str) -> dict[str, Any]:
    """Complete top-level fields of a JSON object cut short (the orchestrator truncates tool
    results to max_result_chars, which can cut a long company list): every field before the
    cut is kept, the field being cut and those after it are lost."""
    decoder, out = json.JSONDecoder(), {}
    i = (text or "").find("{")
    if i < 0:
        return out
    i += 1
    while True:
        i = _KEY_SEP.match(text, i).end()
        try:
            key, i = decoder.raw_decode(text, i)
        except json.JSONDecodeError:
            return out
        colon = _COLON.match(text, i)
        if not isinstance(key, str) or not colon:
            return out
        try:
            value, i = decoder.raw_decode(text, colon.end())
        except json.JSONDecodeError:
            return out
        out[key] = value


def _parse_result(text: Any) -> dict[str, Any]:
    """The JSON object of a tool result, or its complete leading fields when it was cut short."""
    try:
        d = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        # Found in the first Ollama run: a search with limit=25 exceeded max_result_chars; the
        # model read total_results at the top of the cut text, the check could not parse it.
        return leading_fields(text) if isinstance(text, str) else {}
    return d if isinstance(d, dict) else {}


def _result(call: ToolCall) -> dict[str, Any]:
    return _parse_result(call.result)


def tools_of(spec: dict[str, Any]) -> list[str]:
    """'tool' is one tool name or a list of tools that are equally valid."""
    return [spec["tool"]] if isinstance(spec["tool"], str) else list(spec["tool"])


def call_matches(call: ToolCall, expected: dict[str, Any]) -> bool:
    """'args': required arguments; 'result': required fields of the tool result (dotted paths)."""
    if call.tool not in tools_of(expected) or (call.error and not expected.get("allow_error")):
        return False
    args = call.arguments if isinstance(call.arguments, dict) else (tool_arguments(call.arguments) or {})
    if not all(k in args and _same(args[k], v) for k, v in (expected.get("args") or {}).items()):
        return False
    spec = expected.get("result") or {}
    if isinstance(spec.get(call.tool), dict):  # fields that depend on the tool: {"tool": {"path": value}}
        spec = spec[call.tool]
    result = _result(call) if spec else {}
    return all(value_at(result, k) is not None and _same(value_at(result, k), v) for k, v in spec.items())


def _plain(text: str) -> str:
    """Lower case, no accents, punctuation as spaces, apostrophes kept: for word matching."""
    t = unicodedata.normalize("NFKD", (text or "").replace("’", "'")).encode("ascii", "ignore").decode().lower()
    return " " + re.sub(r"[^a-z0-9']+", " ", t) + " "


def cites_source(answer: str, results: list[str]) -> bool | None:
    """Whether the answer names the source of at least one tool result that returned data.
    None when no successful result has a source this check knows."""
    words = []
    for text in results:
        source = _parse_result(text).get("source")
        for key, kws in SOURCE_WORDS.items():
            if source and key in _plain(source):
                words += kws
    if not words:
        return None
    plain = _plain(answer)
    return any(f" {_plain(w).strip()} " in plain for w in words)


def unneeded_calls(q: dict[str, Any], tools: list[str]) -> int:
    """Calls to tools the question does not need ('calls' and 'allowed' tools are needed)."""
    needed = {t for e in q.get("calls") or [] for t in tools_of(e)} | set(q.get("allowed") or [])
    return sum(t not in needed for t in tools)


def evaluate(q: dict[str, Any], a: Answer) -> dict[str, Any]:
    """Checks for one run. 'success' is true when every check passes."""
    missing = ["/".join(tools_of(e)) for e in q.get("calls") or [] if not any(call_matches(c, e) for c in a.tool_calls)]
    expect = q.get("answer") or {}
    answer_ok, detail = True, None
    if "value_from" in expect:
        spec = expect["value_from"]
        results = [c for c in a.tool_calls if c.tool in tools_of(spec) and not c.error]
        value = None
        if results:
            path = spec["path"] if isinstance(spec["path"], str) else spec["path"].get(results[-1].tool, "")
            value = value_at(_result(results[-1]), path)
        if not results:
            answer_ok, detail = False, f"no successful {'/'.join(tools_of(spec))} call"
        elif value is None:
            answer_ok, detail = False, f"no value at {spec['path']} in the {spec['tool']} result"
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            answer_ok = int(round(value)) in numbers_in(a.text)
            detail = f"expected {value}"
        else:
            answer_ok = str(value).lower() in (a.text or "").lower()
            detail = f"expected {value!r}"
    if expect.get("contains"):
        found = [s for s in expect["contains"] if _plain(s).strip() in _plain(a.text)]
        answer_ok = answer_ok and len(found) == len(expect["contains"])
        detail = f"expected {expect['contains']}"
    if expect.get("no_amount"):
        amount = _EURO_AMOUNT.search(a.text or "")
        answer_ok = answer_ok and amount is None
        detail = f"euro amount found: {amount.group(0)!r}" if amount else "no euro amount"
    model_ok = a.error is None
    return {
        "success": model_ok and not missing and answer_ok,
        "api_error": any(c.error and any(m in c.result for m in API_ERROR_MARKERS) for c in a.tool_calls),
        "cites_source": cites_source(a.text, [c.result for c in a.tool_calls if not c.error]),
        "model_ok": model_ok,
        "missing_calls": missing,
        "answer_ok": answer_ok,
        "answer_detail": detail,
        "calls": len(a.tool_calls),
        "calls_failed": sum(c.error for c in a.tool_calls),
        "calls_repeated": sum(c.repeated for c in a.tool_calls),
        "calls_extra": unneeded_calls(q, [c.tool for c in a.tool_calls]),
    }


def run_record(q: dict[str, Any], n: int, a: Answer, seconds: float) -> dict[str, Any]:
    usage = [c.get("usage") or {} for c in a.llm_calls]
    return {
        "id": q["id"], "category": q.get("category"), "run": n, "question": q["question"],
        **evaluate(q, a),
        "seconds": round(seconds, 2),
        "llm_seconds": round(sum(c.get("seconds") or 0 for c in a.llm_calls), 2),
        "tool_seconds": round(sum(c.seconds for c in a.tool_calls), 2),
        "llm_requests": len(a.llm_calls),
        "prompt_tokens": sum(u.get("prompt_tokens") or 0 for u in usage) if any(usage) else None,
        "completion_tokens": sum(u.get("completion_tokens") or 0 for u in usage) if any(usage) else None,
        "error": a.error,
        "tool_calls": [{"tool": c.tool, "arguments": c.arguments, "error": c.error, "repeated": c.repeated,
                        "seconds": round(c.seconds, 2), "result": c.result} for c in a.tool_calls],
        "answer": a.text,
    }


# ---------------------------------------------------------------- summary

def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval of a proportion k/n (runs of the same question are not
    independent, so the real uncertainty is larger)."""
    if n == 0:
        return 0.0, 0.0
    p, d = k / n, 1 + z * z / n
    centre, half = (p + z * z / (2 * n)) / d, z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return max(0.0, centre - half), min(1.0, centre + half)


def _rate(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({k / n:.0%}, 95% interval {lo:.0%}-{hi:.0%})" if n else "0/0"


def _median(values: list[float]) -> float | None:
    values = [v for v in values if v is not None]
    return round(statistics.median(values), 1) if values else None


def summarize(records: list[dict[str, Any]], meta: dict[str, Any]) -> str:
    by_id: dict[str, list[dict[str, Any]]] = {}
    for r in records:
        by_id.setdefault(r["id"], []).append(r)
    ok = sum(r["success"] for r in records)
    completion = [r["completion_tokens"] for r in records if r["completion_tokens"] is not None]
    llm_s = sum(r["llm_seconds"] for r in records if r["completion_tokens"] is not None)
    params = json.dumps(meta["llm"].get("params") or {}, ensure_ascii=False)
    qfiles = ", ".join(f"`{Path(f).name}`" for f in _question_files(meta.get("questions_file"))) or "file not recorded"
    lines = [
        f"# Benchmark {meta['started']}",
        "",
        f"- Label: {meta.get('label') or '(none)'}",
        f"- Model: `{meta['llm']['model']}` at `{meta['llm']['base_url']}`, params `{params}`",
        f"- Machine: {machine_text(meta['machine'])}",
        *([f"- Model server: {meta['server_version']}"] if meta.get("server_version") else []),
        f"- Code: french-open-data-mcp {meta['version']}, commit `{meta.get('commit') or '?'}`",
        f"- Questions: {qfiles}, {len({r['id'] for r in records})} questions",
        f"- Runs: {meta['runs']} per question, {len(records)} in total",
        *([f"- Checks re-applied on {meta['rescored']['date']} with `{meta['rescored']['questions_file']}` "
           f"(commit `{meta['rescored']['commit'] or '?'}`) to {meta['rescored']['runs']} stored runs; "
           "the summary written during the run is kept in summary-as-run.md"] if meta.get("rescored") else []),
        "",
        f"**Success: {_rate(ok, len(records))}** (expected tool calls succeeded and the answer contains the "
        "tool's figure; runs of the same question are not independent, so the real uncertainty is larger).",
        "",
    ]
    categories: dict[str, list[dict[str, Any]]] = {}
    for r in records:
        if r.get("category"):
            categories.setdefault(r["category"], []).append(r)
    if categories:
        lines += ["| Category | Success | Names the source |", "|---|---|---|"]
        for cat, rs in categories.items():
            cites = [r["cites_source"] for r in rs if r.get("cites_source") is not None]
            lines.append(f"| {cat} | {_rate(sum(r['success'] for r in rs), len(rs))} "
                         f"| {f'{sum(cites)}/{len(cites)}' if cites else '-'} |")
        lines.append("")
    api = [r for r in records if r["api_error"]]
    if api:
        clean = [r for r in records if not r["api_error"]]
        lines += [f"{len(api)} run(s) hit a public API error (network, HTTP 429 or 5xx), which is not the "
                  f"model's fault. Success without them: {sum(r['success'] for r in clean)}/{len(clean)}.", ""]
    cited = [r["cites_source"] for r in records if r.get("cites_source") is not None]
    if cited:
        lines += [f"Answers naming the source of the data returned: {sum(cited)}/{len(cited)} (runs where a "
                  "tool returned data; keyword check, not part of the success criterion).", ""]
    if completion and llm_s:
        lines += [f"Model output: {sum(completion)} tokens in {llm_s:.0f} s of model requests, "
                  f"{sum(completion) / llm_s:.1f} tokens/s end to end (includes prompt processing).", ""]
    lines += [
        "| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls | Names the source |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for qid, rs in by_id.items():
        cites = [r["cites_source"] for r in rs if r.get("cites_source") is not None]
        lines.append(
            f"| {qid} | {sum(r['success'] for r in rs)}/{len(rs)} | {_median([r['seconds'] for r in rs])} "
            f"| {_median([r['calls'] for r in rs])} | {sum(r['calls_extra'] for r in rs)} "
            f"| {sum(r['calls_failed'] for r in rs)} | {sum(r['calls_repeated'] for r in rs)} "
            f"| {f'{sum(cites)}/{len(cites)}' if cites else '-'} |")
    lines += ["", "Unneeded calls: calls to tools the question does not need (looking up a municipality "
              "code is needed when the question names a town). Failed calls include tool errors the "
              "model caused (e.g. a wrong code) and expected errors (Strasbourg is not covered by DVF)."]
    failures = [r for r in records if not r["success"]]
    if failures:
        lines += ["", "## Failures", "", "| Question | Run | Reason | Calls made | Answer (start) |",
                  "|---|---|---|---|---|"]
        for r in failures:
            reasons = []
            if not r["model_ok"]:
                reasons.append(f"model: {r['error']}")
            if r["missing_calls"]:
                reasons.append("missing or wrong call: " + ", ".join(r["missing_calls"]))
            if not r["answer_ok"]:
                reasons.append(f"answer ({r['answer_detail']})")
            if r["api_error"]:
                reasons.append("public API error during the run")
            q = r["question"]
            lines.append(f"| {r['id']} | {r['run']} | {mask_sirens('; '.join(reasons), q)} "
                         f"| {_calls_text(r['tool_calls'], q)} | {_cell(mask_sirens(r['answer'], q), 160)} |")
    lines += ["", "Memory used by the model server: not measured by this script (read it in Activity Monitor).", ""]
    return "\n".join(lines)


def repo_relative(path: str) -> str:
    """Path relative to the repository (an absolute path would publish the user's home folder)."""
    p = Path(path).resolve()
    try:
        return str(p.relative_to(HERE.parent))
    except ValueError:
        return p.name


def _cell(text: Any, limit: int) -> str:
    t = re.sub(r"\s+", " ", str(text or "")).strip().replace("|", "/")
    return t if len(t) <= limit else t[:limit] + "…"


_SIREN_OR_SIRET = re.compile(r"(?<!\d)\d{9}(?:\d{5})?(?!\d)")


def mask_sirens(text: str, question: str) -> str:
    """Hide the SIREN and SIRET numbers that the question does not contain. A company returned
    by a tool may be a sole proprietor, whose SIREN identifies a natural person."""
    asked = set(re.findall(r"(?<!\d)\d{9}(?!\d)", question or ""))
    return _SIREN_OR_SIRET.sub(lambda m: m[0] if m[0][:9] in asked else "[SIREN]", text or "")


def _calls_text(calls: list[dict[str, Any]], question: str = "") -> str:
    parts = []
    for c in calls:
        args = c["arguments"] if isinstance(c["arguments"], dict) else {}
        shown = ", ".join(f"{k}={v}" for k, v in args.items())
        parts.append(f"{c['tool']}({shown})" + (" ERROR" if c["error"] else "") + (" repeated" if c["repeated"] else ""))
    return _cell(mask_sirens(" > ".join(parts) or "none", question), 300)


def rescore(record: dict[str, Any], q: dict[str, Any]) -> None:
    """Re-apply the checks of q to a stored run."""
    a = Answer(text=record["answer"], error=record.get("error"), tool_calls=[
        ToolCall("", c["tool"], c["arguments"], c["error"], None, "", repeated=c["repeated"],
                 seconds=c.get("seconds") or 0.0, result=c["result"]) for c in record["tool_calls"]])
    record.update(evaluate(q, a))


def load_questions(paths: list[str]) -> list[dict[str, Any]]:
    """Questions of one or more files; ids must be unique across the files."""
    questions: list[dict[str, Any]] = []
    for path in paths:
        questions += json.loads(Path(path).read_text(encoding="utf-8"))["questions"]
    ids = [q["id"] for q in questions]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise ValueError(f"question ids used twice: {', '.join(duplicates)}")
    return questions


def _question_files(value: Any) -> list[str]:
    return [value] if isinstance(value, str) else list(value or [])


def _locate(path: str) -> str:
    """A questions file as given, relative to the repository (as in meta.json), or by name in bench/."""
    for candidate in (Path(path), HERE.parent / path, HERE / Path(path).name):
        if candidate.exists():
            return str(candidate)
    return path


def resummarize(path: str, questions_file: str | list[str] | None) -> None:
    """Rebuild summary.md from runs.jsonl and meta.json, re-applying the checks of the questions file."""
    root = Path(path)
    if path == "latest":
        dirs = sorted(d for d in (HERE / "results").glob("*-*") if (d / "runs.jsonl").exists())
        if not dirs:
            sys.exit("No results found in bench/results.")
        root = dirs[-1]
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    records = [json.loads(line) for line in (root / "runs.jsonl").read_text(encoding="utf-8").splitlines() if line]
    qfiles = [_locate(f) for f in _question_files(questions_file or meta.get("questions_file"))]
    if not qfiles:
        sys.exit(f"{root / 'meta.json'} records no questions file: give it with --questions.")
    qfile = ", ".join(Path(f).name for f in qfiles)
    questions = {q["id"]: q for q in load_questions(qfiles)}
    rescored = 0
    for r in records:
        if r["id"] in questions:
            rescore(r, questions[r["id"]])
            rescored += 1
    if rescored:
        meta = {**meta, "rescored": {"date": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                                     "questions_file": Path(qfile).name, "runs": rescored,
                                     "commit": _command("git", "-C", str(HERE.parent), "rev-parse", "--short", "HEAD")}}
        if (root / "summary.md").exists() and not (root / "summary-as-run.md").exists():
            (root / "summary-as-run.md").write_text((root / "summary.md").read_text(encoding="utf-8"), encoding="utf-8")
    summary = summarize(records, meta)
    (root / "summary.md").write_text(summary, encoding="utf-8")
    print(summary)
    print(f"Rewritten: {root / 'summary.md'}")


def check_validation(q: dict[str, Any], v: dict[str, Any], is_error: bool, text: str) -> tuple[list[str], Any]:
    """Problems found when a question's 'validate' entry was run, and the value the answer will need."""
    if v.get("expect_error"):
        ok = is_error and str(v["expect_error"]).lower() in text.lower()
        return ([] if ok else [f"expected an error containing {v['expect_error']!r}, got: {text[:150]}"]), None
    if is_error:
        return [f"tool error: {text[:200]}"], None
    problems, value = [], None
    call = ToolCall("", v["tool"], v.get("args") or {}, False, None, "", result=text)
    for e in q.get("calls") or []:
        if v["tool"] in tools_of(e) and not call_matches(call, {k: x for k, x in e.items() if k != "args"}):
            problems.append(f"result does not match {e.get('result')}")
    expect = q.get("answer") or {}
    spec = expect.get("value_from")
    if spec and v["tool"] in tools_of(spec):
        path = spec["path"] if isinstance(spec["path"], str) else spec["path"].get(v["tool"], "")
        value = value_at(_result(call), path)
        if value is None:
            problems.append(f"no value at {spec['path']}")
    for s in expect.get("contains") or []:
        if s.lower() not in text.lower():
            problems.append(f"{s!r} not in the result")
    return problems, value


async def validate(questions: list[dict[str, Any]]) -> bool:
    """Run each question's 'validate' entries on the tools (in-process MCP server, no model)."""
    from mcp import Client

    from fr_open_data.server import build_server

    all_ok = True
    async with Client(build_server(with_legifrance=False)) as c:
        for q in questions:
            entries = q.get("validate") or []
            if not entries:
                print(f"SKIP {q['id']}: no 'validate' entry")
                continue
            for v in entries:
                for attempt in range(3):  # public APIs can fail briefly
                    r = await c.call_tool(v["tool"], v.get("args") or {})
                    text = "\n".join(getattr(x, "text", "") for x in r.content or [])
                    if not (r.is_error and any(m in text for m in API_ERROR_MARKERS)):
                        break
                    await anyio.sleep(3)
                problems, value = check_validation(q, v, bool(r.is_error), text)
                all_ok &= not problems
                shown = f" -> {value}" if value is not None else (" -> error as expected" if v.get("expect_error") else "")
                print(f"{'OK  ' if not problems else 'FAIL'} {q['id']}: {v['tool']}({json.dumps(v.get('args') or {}, ensure_ascii=False)})"
                      f"{shown}{'; ' + '; '.join(problems) if problems else ''}", flush=True)
    return all_ok


# ---------------------------------------------------------------- environment

def _command(*args: str, timeout: float = 10) -> str | None:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=True).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def profiler_field(text: str | None, key: str) -> str | None:
    """First "Key: value" of a system_profiler text output."""
    m = re.search(rf"^\s*{re.escape(key)}:\s*(.+?)\s*$", text or "", re.MULTILINE)
    return m.group(1) if m else None


def machine_info() -> dict[str, Any]:
    info: dict[str, Any] = {"platform": platform.platform(), "python": platform.python_version()}
    if sys.platform == "darwin":
        info["chip"] = _command("sysctl", "-n", "machdep.cpu.brand_string")
        mem = _command("sysctl", "-n", "hw.memsize")
        info["memory_gb"] = round(int(mem) / 2**30) if mem and mem.isdigit() else None
        info["macos"] = _command("sw_vers", "-productVersion")
        # system_profiler: "Total Number of Cores" is the CPU in SPHardwareDataType, the GPU in SPDisplaysDataType.
        hw = _command("system_profiler", "SPHardwareDataType", timeout=60)
        gpu = _command("system_profiler", "SPDisplaysDataType", timeout=60)
        info["model"] = profiler_field(hw, "Model Name")
        info["model_id"] = profiler_field(hw, "Model Identifier")
        info["cpu_cores"] = profiler_field(hw, "Total Number of Cores")
        info["gpu_cores"] = profiler_field(gpu, "Total Number of Cores")
    return info


def machine_text(m: dict[str, Any]) -> str:
    parts = [" ".join(p for p in (m.get("model"), f"({m['model_id']})" if m.get("model_id") else None) if p),
             m.get("chip") or m.get("platform"),
             f"CPU {m['cpu_cores']} cores" if m.get("cpu_cores") else None,
             f"GPU {m['gpu_cores']} cores" if m.get("gpu_cores") else None,
             f"{m.get('memory_gb') or '?'} GB memory",
             f"macOS {m['macos']}" if m.get("macos") else None]
    return ", ".join(p for p in parts if p)


def server_health(llm_cfg: dict[str, Any]) -> Any:
    """GET /health on the model server (mlx-engine reports its context length there)."""
    url = re.sub(r"/v1/?$", "", llm_cfg["base_url"].rstrip("/")) + "/health"
    key = api_key(llm_cfg)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"} if key else {})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:  # optional information
        return f"unavailable ({type(e).__name__})"


# ---------------------------------------------------------------- main

def write_meta(out_dir: Path, meta: dict[str, Any]) -> None:
    (out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


async def _run(args: argparse.Namespace, cfg: dict[str, Any], questions: list[dict[str, Any]],
               out_dir: Path, meta: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    async with from_config(cfg) as orch:
        if orch.unavailable:
            sys.exit(f"MCP server unavailable: {orch.unavailable}")
        meta["tools"] = sorted(orch.routes)
        # Written now and again at the end, so that an interrupted run keeps its label and
        # settings (its meta.json then has no "finished" time).
        write_meta(out_dir, meta)
        with open(out_dir / "runs.jsonl", "w", encoding="utf-8") as f:
            for q in questions:
                for n in range(1, args.runs + 1):
                    t0 = time.perf_counter()
                    a = await orch.answer(q["question"])
                    r = run_record(q, n, a, time.perf_counter() - t0)
                    records.append(r)
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                    f.flush()
                    calls = " > ".join(c["tool"] + ("(x)" if c["error"] else "") for c in r["tool_calls"]) or "-"
                    print(f"{'OK  ' if r['success'] else 'FAIL'} {q['id']} #{n} {r['seconds']:.1f}s [{calls}]", flush=True)
    return records


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--questions", nargs="+", default=[str(HERE / "questions_dev.json")],
                    help="one or more question files (ids must be unique across them)")
    ap.add_argument("--model", help="replace llm.model of the config (e.g. an Ollama model name)")
    ap.add_argument("--runs", type=int, default=3, help="runs per question (default 3)")
    ap.add_argument("--only", help="comma-separated question ids")
    ap.add_argument("--label", help="free text stored with the results, e.g. model file and machine")
    ap.add_argument("--out", default=str(HERE / "results"))
    ap.add_argument("--env-file", default=".env")
    ap.add_argument("--server-version", help='model server and version, e.g. "mlx-engine (OVHcloud fork) 58083ca"')
    ap.add_argument("--summarize", metavar="DIR", help="only rebuild summary.md of a results folder ('latest' for the last one)")
    ap.add_argument("--validate", action="store_true", help="only check the questions against the tools (no model)")
    args = ap.parse_args(argv)
    if args.summarize:
        resummarize(args.summarize, args.questions if "--questions" in (argv or sys.argv) else None)
        return
    if args.validate:
        sys.exit(0 if anyio.run(validate, load_questions(args.questions)) else 1)
    try:
        envfile.load(args.env_file)
        cfg = load_config(args.config)
        check_config(cfg)
        if args.model:
            cfg["llm"]["model"] = args.model
        warn_if_remote(cfg["llm"])
    except (OSError, ValueError) as e:
        sys.exit(f"{args.config}: {e}")
    try:
        questions = load_questions(args.questions)
    except (OSError, ValueError) as e:
        sys.exit(f"questions: {e}")
    if args.only:
        wanted = set(args.only.split(","))
        questions = [q for q in questions if q["id"] in wanted]
    if not questions or args.runs < 1:
        sys.exit("Nothing to run.")

    started = dt.datetime.now(dt.timezone.utc)
    out_dir = Path(args.out) / started.strftime("%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "started": started.isoformat(timespec="seconds"),
        "label": args.label,
        "server_version": args.server_version,
        "llm_remote_host": remote_llm_host(cfg["llm"]),  # None: the model runs on this machine
        "version": __version__,
        "commit": _command("git", "-C", str(HERE.parent), "rev-parse", "--short", "HEAD"),
        "machine": machine_info(),
        "llm": {k: v for k, v in cfg["llm"].items() if k != "api_key_env"},
        "server_health": server_health(cfg["llm"]),
        "max_turns": cfg.get("max_turns", 6),
        "runs": args.runs,
        "questions_file": (repo_relative(args.questions[0]) if len(args.questions) == 1
                           else [repo_relative(q) for q in args.questions]),
    }
    records = anyio.run(_run, args, cfg, questions, out_dir, meta)
    meta["finished"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    write_meta(out_dir, meta)
    summary = summarize(records, meta)
    (out_dir / "summary.md").write_text(summary, encoding="utf-8")
    print("\n" + summary)
    print(f"Results: {out_dir}")


if __name__ == "__main__":
    main()
