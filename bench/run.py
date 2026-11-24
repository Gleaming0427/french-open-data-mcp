"""Benchmark: ask fixed questions to the configured model, several times, and check the answers.

  python -m bench.run --config config.json --runs 3 --label "Olala q5e6, MacBook Pro M2 Max"

For each run of each question (bench/questions.json), it records the tools called, their
arguments, results and duration, the model requests (duration and token counts when the
server reports them), and checks:
- that the expected tool calls succeeded with the expected arguments, or returned the
  expected data (e.g. the DVF result is for the right municipality and year);
- that the answer contains the figure returned by the tool in this run (or the expected
  text, or no euro amount when the data does not exist);
- that the model did not fail (error, or no answer within max_turns).

Results go to bench/results/<date>-<time>/: meta.json (machine, model, configuration),
runs.jsonl (one line per run, with the full answer) and summary.md (tables to publish).
The memory used by the model server is not measured: read it in Activity Monitor.

  python -m bench.run --summarize latest     # rebuild summary.md of the latest results
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import re
import statistics
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

import anyio

from fr_open_data import __version__, envfile
from fr_open_data.orchestrator import Answer, ToolCall, check_config, from_config, load_config, tool_arguments

HERE = Path(__file__).resolve().parent
_SEPARATOR = re.compile(r"(?<=\d)[\s   .,'](?=\d{3}(?!\d))")  # thousands separators
_EURO_AMOUNT = re.compile(r"\d[\d\s   .,]*\s*(€|euros?\b|EUR\b)", re.IGNORECASE)
# Messages of fr_open_data/http.py when a public API fails: not the model's fault.
API_ERROR_MARKERS = ("unreachable", "temporarily unavailable", "too many requests", "failed after retry")


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


def _same(actual: Any, expected: Any) -> bool:
    """Compare codes and years, ignoring case, spaces and dots ("62.02A" = "6202a")."""
    norm = lambda v: re.sub(r"[\s.]+", "", str(v)).upper()  # noqa: E731
    return norm(actual) == norm(expected)


def _result(call: ToolCall) -> dict[str, Any]:
    try:
        d = json.loads(call.result)
    except (json.JSONDecodeError, TypeError):
        return {}
    return d if isinstance(d, dict) else {}


def call_matches(call: ToolCall, expected: dict[str, Any]) -> bool:
    """'args': required arguments; 'result': required fields of the tool result (dotted paths)."""
    if call.tool != expected["tool"] or (call.error and not expected.get("allow_error")):
        return False
    args = call.arguments if isinstance(call.arguments, dict) else (tool_arguments(call.arguments) or {})
    if not all(k in args and _same(args[k], v) for k, v in (expected.get("args") or {}).items()):
        return False
    result = _result(call) if expected.get("result") else {}
    return all(value_at(result, k) is not None and _same(value_at(result, k), v)
               for k, v in (expected.get("result") or {}).items())


def unneeded_calls(q: dict[str, Any], tools: list[str]) -> int:
    """Calls to tools the question does not need ('calls' and 'allowed' tools are needed)."""
    needed = {e["tool"] for e in q.get("calls") or []} | set(q.get("allowed") or [])
    return sum(t not in needed for t in tools)


def evaluate(q: dict[str, Any], a: Answer) -> dict[str, Any]:
    """Checks for one run. 'success' is true when every check passes."""
    missing = [e["tool"] for e in q.get("calls") or [] if not any(call_matches(c, e) for c in a.tool_calls)]
    expect = q.get("answer") or {}
    answer_ok, detail = True, None
    if "value_from" in expect:
        spec = expect["value_from"]
        results = [c for c in a.tool_calls if c.tool == spec["tool"] and not c.error]
        value = None
        if results:
            try:
                value = value_at(json.loads(results[-1].result), spec["path"])
            except (json.JSONDecodeError, TypeError):
                value = None
        if not results:
            answer_ok, detail = False, f"no successful {spec['tool']} call"
        elif value is None:
            answer_ok, detail = False, f"no value at {spec['path']} in the {spec['tool']} result"
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            answer_ok = int(round(value)) in numbers_in(a.text)
            detail = f"expected {value}"
        else:
            answer_ok = str(value).lower() in (a.text or "").lower()
            detail = f"expected {value!r}"
    if expect.get("contains"):
        found = [s for s in expect["contains"] if s.lower() in (a.text or "").lower()]
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
        "id": q["id"], "run": n, "question": q["question"],
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
    lines = [
        f"# Benchmark {meta['started']}",
        "",
        f"- Label: {meta.get('label') or '(none)'}",
        f"- Model: `{meta['llm']['model']}` at `{meta['llm']['base_url']}`, params `{json.dumps(meta['llm'].get('params') or {}, ensure_ascii=False)}`",
        f"- Machine: {meta['machine'].get('chip') or meta['machine']['platform']}, "
        f"{meta['machine'].get('memory_gb') or '?'} GB memory"
        + (f", macOS {meta['machine']['macos']}" if meta['machine'].get('macos') else ""),
        f"- Code: french-open-data-mcp {meta['version']}, commit `{meta.get('commit') or '?'}`",
        f"- Runs: {meta['runs']} per question, {len(records)} in total",
        "",
        f"**Success: {ok}/{len(records)}** (expected tool calls succeeded and the answer contains the tool's figure).",
        "",
    ]
    api = [r for r in records if r["api_error"]]
    if api:
        clean = [r for r in records if not r["api_error"]]
        lines += [f"{len(api)} run(s) hit a public API error (network, HTTP 429 or 5xx), which is not the "
                  f"model's fault. Success without them: {sum(r['success'] for r in clean)}/{len(clean)}.", ""]
    if completion and llm_s:
        lines += [f"Model output: {sum(completion)} tokens in {llm_s:.0f} s of model requests, "
                  f"{sum(completion) / llm_s:.1f} tokens/s end to end (includes prompt processing).", ""]
    lines += [
        "| Question | Success | Median time (s) | Median tool calls | Unneeded calls | Failed calls | Repeated calls |",
        "|---|---|---|---|---|---|---|",
    ]
    for qid, rs in by_id.items():
        lines.append(
            f"| {qid} | {sum(r['success'] for r in rs)}/{len(rs)} | {_median([r['seconds'] for r in rs])} "
            f"| {_median([r['calls'] for r in rs])} | {sum(r['calls_extra'] for r in rs)} "
            f"| {sum(r['calls_failed'] for r in rs)} | {sum(r['calls_repeated'] for r in rs)} |")
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
            lines.append(f"| {r['id']} | {r['run']} | {'; '.join(reasons)} | {_calls_text(r['tool_calls'])} "
                         f"| {_cell(r['answer'], 160)} |")
    lines += ["", "Memory used by the model server: not measured by this script (read it in Activity Monitor).", ""]
    return "\n".join(lines)


def _cell(text: Any, limit: int) -> str:
    t = re.sub(r"\s+", " ", str(text or "")).strip().replace("|", "/")
    return t if len(t) <= limit else t[:limit] + "…"


def _calls_text(calls: list[dict[str, Any]]) -> str:
    parts = []
    for c in calls:
        args = c["arguments"] if isinstance(c["arguments"], dict) else {}
        shown = ", ".join(f"{k}={v}" for k, v in args.items())
        parts.append(f"{c['tool']}({shown})" + (" ERROR" if c["error"] else "") + (" repeated" if c["repeated"] else ""))
    return _cell(" > ".join(parts) or "none", 300)


def resummarize(path: str, questions_file: str | None) -> None:
    """Rebuild summary.md from runs.jsonl and meta.json (unneeded calls are recomputed)."""
    root = Path(path)
    if path == "latest":
        dirs = sorted(d for d in (HERE / "results").glob("*-*") if (d / "runs.jsonl").exists())
        if not dirs:
            sys.exit("No results found in bench/results.")
        root = dirs[-1]
    meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
    records = [json.loads(line) for line in (root / "runs.jsonl").read_text(encoding="utf-8").splitlines() if line]
    qfile = questions_file or meta.get("questions_file") or str(HERE / "questions.json")
    questions = {q["id"]: q for q in json.loads(Path(qfile).read_text(encoding="utf-8"))["questions"]}
    for r in records:
        if r["id"] in questions:
            r["calls_extra"] = unneeded_calls(questions[r["id"]], [c["tool"] for c in r["tool_calls"]])
    summary = summarize(records, meta)
    (root / "summary.md").write_text(summary, encoding="utf-8")
    print(summary)
    print(f"Rewritten: {root / 'summary.md'}")


# ---------------------------------------------------------------- environment

def _command(*args: str) -> str | None:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=10, check=True).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def machine_info() -> dict[str, Any]:
    info: dict[str, Any] = {"platform": platform.platform(), "python": platform.python_version()}
    if sys.platform == "darwin":
        info["chip"] = _command("sysctl", "-n", "machdep.cpu.brand_string")
        mem = _command("sysctl", "-n", "hw.memsize")
        info["memory_gb"] = round(int(mem) / 2**30) if mem and mem.isdigit() else None
        info["macos"] = _command("sw_vers", "-productVersion")
    return info


def server_health(llm_cfg: dict[str, Any]) -> Any:
    """GET /health on the model server (mlx-engine reports its context length there)."""
    url = re.sub(r"/v1/?$", "", llm_cfg["base_url"].rstrip("/")) + "/health"
    key = os.environ.get(llm_cfg["api_key_env"]) if llm_cfg.get("api_key_env") else None
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"} if key else {})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:  # optional information
        return f"unavailable ({type(e).__name__})"


# ---------------------------------------------------------------- main

async def _run(args: argparse.Namespace, cfg: dict[str, Any], questions: list[dict[str, Any]],
               out_dir: Path, meta: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    async with from_config(cfg) as orch:
        if orch.unavailable:
            sys.exit(f"MCP server unavailable: {orch.unavailable}")
        meta["tools"] = sorted(orch.routes)
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
    ap.add_argument("--questions", default=str(HERE / "questions.json"))
    ap.add_argument("--runs", type=int, default=3, help="runs per question (default 3)")
    ap.add_argument("--only", help="comma-separated question ids")
    ap.add_argument("--label", help="free text stored with the results, e.g. model file and machine")
    ap.add_argument("--out", default=str(HERE / "results"))
    ap.add_argument("--env-file", default=".env")
    ap.add_argument("--summarize", metavar="DIR", help="only rebuild summary.md of a results folder ('latest' for the last one)")
    args = ap.parse_args(argv)
    if args.summarize:
        resummarize(args.summarize, args.questions if "--questions" in (argv or sys.argv) else None)
        return
    try:
        envfile.load(args.env_file)
        cfg = load_config(args.config)
        check_config(cfg)
    except (OSError, ValueError) as e:
        sys.exit(f"{args.config}: {e}")
    questions = json.loads(Path(args.questions).read_text(encoding="utf-8"))["questions"]
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
        "version": __version__,
        "commit": _command("git", "-C", str(HERE.parent), "rev-parse", "--short", "HEAD"),
        "machine": machine_info(),
        "llm": {k: v for k, v in cfg["llm"].items() if k != "api_key_env"},
        "server_health": server_health(cfg["llm"]),
        "max_turns": cfg.get("max_turns", 6),
        "runs": args.runs,
        "questions_file": args.questions,
    }
    records = anyio.run(_run, args, cfg, questions, out_dir, meta)
    meta["finished"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    (out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = summarize(records, meta)
    (out_dir / "summary.md").write_text(summary, encoding="utf-8")
    print("\n" + summary)
    print(f"Results: {out_dir}")


if __name__ == "__main__":
    main()
