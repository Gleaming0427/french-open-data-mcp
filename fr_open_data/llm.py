"""Minimal client for an OpenAI-compatible chat API (standard library only).

Works with local servers:
- the Olala MLX server, mlx-engine (http://127.0.0.1:8000/v1, streaming responses only);
- Ollama (http://localhost:11434/v1);
- the fake server used by the tests (tools/fake_llm.py).

When streaming, the client rebuilds the reasoning (`reasoning_content`), the
answer (`content`) and the tool calls (`tool_calls`, sent in pieces).
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

# End-of-stream error sent by the Olala MLX server (mlx-engine) when max_tokens is reached.
_TRUNCATION_MARKERS = ("ended without a stop condition",)


@dataclass
class Reply:
    content: str = ""
    reasoning: str = ""
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    finish_reason: str | None = None
    usage: dict[str, Any] | None = None
    error: str | None = None
    truncated: bool = False
    total_s: float = 0.0


def _merge_tool_call(acc: dict[int, dict[str, Any]], delta: dict[str, Any]) -> None:
    idx = delta.get("index", len(acc))
    call = acc.setdefault(idx, {"id": None, "name": "", "arguments": ""})
    if delta.get("id"):
        call["id"] = delta["id"]
    fn = delta.get("function") or {}
    if fn.get("name"):
        call["name"] += fn["name"]
    args = fn.get("arguments")
    if isinstance(args, dict):  # some servers send an already-decoded object
        call["arguments"] = json.dumps(args, ensure_ascii=False)
    elif isinstance(args, str):
        call["arguments"] += args


def _read_stream(resp: Any, out: Reply) -> None:
    calls: dict[int, dict[str, Any]] = {}
    event = None
    for raw in resp:
        line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
        if not line:
            event = None
            continue
        if line.startswith("event:"):
            event = line[6:].strip()
            continue
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            obj = json.loads(data)
        except json.JSONDecodeError:
            if event == "error":
                out.error = data
                break
            continue
        if event == "error" or (isinstance(obj, dict) and obj.get("error")):
            err = obj.get("error", obj) if isinstance(obj, dict) else obj
            out.error = err if isinstance(err, str) else json.dumps(err, ensure_ascii=False)
            break
        if obj.get("usage"):
            out.usage = obj["usage"]
        for choice in obj.get("choices") or []:
            delta = choice.get("delta") or {}
            out.reasoning += delta.get("reasoning_content") or delta.get("reasoning") or ""
            out.content += delta.get("content") or ""
            for tc in delta.get("tool_calls") or []:
                _merge_tool_call(calls, tc)
            if choice.get("finish_reason"):
                out.finish_reason = choice["finish_reason"]
    out.tool_calls = [calls[k] for k in sorted(calls)]


def _read_block(obj: dict[str, Any], out: Reply) -> None:
    if obj.get("error"):
        err = obj["error"]
        out.error = err if isinstance(err, str) else json.dumps(err, ensure_ascii=False)
        return
    out.usage = obj.get("usage")
    choice = (obj.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    out.content = msg.get("content") or ""
    out.reasoning = msg.get("reasoning_content") or msg.get("reasoning") or ""
    out.finish_reason = choice.get("finish_reason")
    for tc in msg.get("tool_calls") or []:
        acc: dict[int, dict[str, Any]] = {}
        _merge_tool_call(acc, {**tc, "index": 0})
        out.tool_calls.append(acc[0])


def chat(base_url: str, payload: dict[str, Any], api_key: str | None = None,
         timeout_s: float = 300.0, stream: bool = True) -> Reply:
    body = dict(payload)
    body["stream"] = stream
    headers = {"Content-Type": "application/json", "Accept": "text/event-stream" if stream else "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions",
                                 data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    out = Reply()
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            if stream:
                _read_stream(resp, out)
            else:
                _read_block(json.loads(resp.read().decode("utf-8")), out)
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", errors="replace")[:500]
        except Exception:  # pragma: no cover
            detail = ""
        out.error = f"HTTP {e.code}: {detail}"
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError, json.JSONDecodeError) as e:
        out.error = out.error or f"{type(e).__name__}: {e}"
    out.total_s = time.perf_counter() - t0
    if out.finish_reason == "length" or (out.error and any(m in out.error for m in _TRUNCATION_MARKERS)):
        out.truncated = True
    return out


_THINK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def strip_reasoning(text: str) -> str:
    """Remove reasoning left in the answer (<think> tags)."""
    text = _THINK.sub("", text or "")
    if "</think>" in text.lower():
        text = re.split(r"</think>", text, flags=re.IGNORECASE)[-1]
    return text.strip()
