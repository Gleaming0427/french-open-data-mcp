"""Fake OpenAI-compatible server, to test the orchestrator WITHOUT a model.

Deterministic behaviour:
- until a tool result has been received, it asks for a tool:
  * question with 5 digits and the word "price"  -> property_prices(insee_code)
  * question with 9 or 14 digits                 -> company_profile(siren)
  * otherwise                                    -> search_companies(text=question)
  (if the chosen tool is not offered, it takes the first tool in the list;
  if the question contains "invalid arguments", the call carries arguments that are not JSON;
  if it contains "repeat", the same call is made a second time after the first result);
- then it answers by quoting the start of the last tool result.

The stream sends reasoning first, then the tool call in two pieces. Like the Olala MLX
server (mlx-engine), it answers HTTP 400 when a past tool call in the conversation has
arguments that are not valid JSON.

  python tools/fake_llm.py --port 8099
  # config: "base_url": "http://127.0.0.1:8099/v1", "model": "fake"
"""

from __future__ import annotations

import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


def choose_call(question: str, tools: list[str]) -> tuple[str, dict[str, Any]]:
    five = re.search(r"(?<!\d)(\d{5})(?!\d)", question)
    siren = re.search(r"(?<!\d)(\d{14}|\d{9})(?!\d)", question.replace(" ", ""))
    if five and "price" in question.lower():
        name, args = "property_prices", {"insee_code": five[1]}
    elif siren:
        name, args = "company_profile", {"siren": siren[1]}
    else:
        name, args = "search_companies", {"text": question}
    if name not in tools and tools:
        name = tools[0]
    return name, args


def chunk(delta: dict[str, Any] | None = None, finish: str | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {"object": "chat.completion.chunk",
                           "choices": [{"index": 0, "delta": delta or {}, "finish_reason": finish}]}
    if finish:  # like mlx-engine, token counts come with the last chunk
        out["usage"] = {"prompt_tokens": 100, "completion_tokens": 10, "total_tokens": 110}
    return out


class Handler(BaseHTTPRequestHandler):
    key: str | None = None

    def log_message(self, *a: Any) -> None:  # quiet
        pass

    def _json(self, code: int, obj: Any) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if self.key and self.headers.get("Authorization") != f"Bearer {self.key}":
            return self._json(401, {"error": "unauthorized"})
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        msgs = req.get("messages") or []
        for m in msgs:
            for tc in m.get("tool_calls") or []:
                try:
                    json.loads(tc["function"]["arguments"])
                except (TypeError, ValueError):
                    return self._json(400, {"error": {"message": "Tool call arguments must be a JSON object."}})
        question = next((m["content"] for m in msgs if m["role"] == "user"), "")
        results = [m["content"] for m in msgs if m["role"] == "tool"]
        tools = [t["function"]["name"] for t in req.get("tools") or []]

        if "repeat" in question.lower() and len(results) == 1 and tools:
            name, args = choose_call(question, tools)
            call = (name, json.dumps(args, ensure_ascii=False))
        elif results or not tools:
            call = None
            text = f"According to the tool: {results[-1][:120]}" if results else "OK"
        else:
            name, args = choose_call(question, tools)
            call = (name, '{"text": ' if "invalid arguments" in question.lower() else json.dumps(args, ensure_ascii=False))

        if not req.get("stream"):
            msg: dict[str, Any] = {"role": "assistant", "content": None if call else text,
                                   "reasoning_content": "Thinking."}
            if call:
                msg["tool_calls"] = [{"id": "call_0", "type": "function",
                                      "function": {"name": call[0], "arguments": call[1]}}]
            return self._json(200, {"choices": [{"index": 0, "message": msg,
                                                 "finish_reason": "tool_calls" if call else "stop"}]})

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()

        def send(obj: Any) -> None:
            self.wfile.write(f"data: {json.dumps(obj, ensure_ascii=False)}\n\n".encode())
            self.wfile.flush()

        send(chunk({"reasoning_content": "Thinking. "}))
        if call:
            half = len(call[1]) // 2
            send(chunk({"tool_calls": [{"index": 0, "id": "call_0", "type": "function",
                                        "function": {"name": call[0], "arguments": call[1][:half]}}]}))
            send(chunk({"tool_calls": [{"index": 0, "function": {"arguments": call[1][half:]}}]}))
            send(chunk(finish="tool_calls"))
        else:
            send(chunk({"content": text}))
            send(chunk(finish="stop"))
        self.wfile.write(b"data: [DONE]\n\n")


def make_server(port: int = 0, key: str | None = None) -> ThreadingHTTPServer:
    """Create the server (port 0 = free port chosen by the OS) without starting it."""
    Handler.key = key
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8099)
    ap.add_argument("--key", default=None, help="expected key (Bearer), optional")
    args = ap.parse_args()
    srv = make_server(args.port, args.key)
    print(f"Fake LLM on http://127.0.0.1:{args.port}/v1")
    srv.serve_forever()


if __name__ == "__main__":
    main()
