"""Orchestrator: connects a local OpenAI-compatible LLM to MCP servers started on this machine.

  python -m fr_open_data.orchestrator --config config.json --check
  python -m fr_open_data.orchestrator --config config.json --question "Apartment prices in Beaune in 2025?"
  python -m fr_open_data.orchestrator --config config.json        # interactive mode

Keys (MLX_ENGINE_API_KEY, LEGIFRANCE_*) come from environment variables, or from a
.env file in the current directory (see .env.example); a variable already set in the
terminal wins.

Loop: the model receives the question and the list of MCP tools; when it asks for
a tool, the orchestrator runs it on the matching MCP server and sends the result
back; this repeats until an answer without tool calls (or `max_turns`).
Each question is handled independently (short requests, as recommended by the
Olala model card).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
from contextlib import AsyncExitStack
from dataclasses import dataclass, field, replace
from typing import Any

import anyio
from mcp import Client, StdioServerParameters
from mcp.client.stdio import get_default_environment

from . import envfile, llm

DEFAULT_SYSTEM_PROMPT = (
    "You answer questions using official French public data. Use the tools to get the facts; "
    "never invent a figure, a name or a legal article. If the tools do not provide the "
    "information, say so. Call only the tools the question needs, and answer as soon as a "
    "tool result contains the answer. End by citing the source given by the tool. Answer "
    "briefly, in the language of the question."
)
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
# Sent instead of running a tool once the question has used max_tool_calls.
TOOL_LIMIT_NOTE = ("ERROR: limit of {n} tool calls reached for this question; this call was not run. "
                   "Answer now with the results you already have.")
# Prefix of a tool result sent again when the model repeats an identical call.
REPEATED_CALL_NOTE = "You already called this tool with these arguments; same result as before. Answer from it.\n"
# Variables passed to MCP servers started as subprocesses (stdio), on top of the
# safe ones kept by the SDK (PATH, HOME...). Proxy and CA variables are needed
# when outbound traffic goes through a proxy.
FORWARDED_ENV = [
    "LEGIFRANCE_CLIENT_ID", "LEGIFRANCE_CLIENT_SECRET", "LEGIFRANCE_TOKEN_URL", "LEGIFRANCE_API_URL",
    "FR_OPEN_DATA_USER_AGENT", "PYTHONPATH",
    "HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "NO_PROXY", "no_proxy",
    "SSL_CERT_FILE", "SSL_CERT_DIR",
]
CONNECT_TIMEOUT_S = 60.0


@dataclass
class ToolCall:
    server: str
    tool: str
    arguments: Any
    error: bool
    source: str | None
    excerpt: str
    repeated: bool = False  # identical to an earlier successful call: not run again
    seconds: float = 0.0  # time spent running the tool
    result: str = ""  # text sent to the model


@dataclass
class Answer:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    turns: int = 0
    error: str | None = None
    llm_calls: list[dict[str, Any]] = field(default_factory=list)  # per model request: seconds, usage


def client_from_config(s: dict[str, Any]) -> Client:
    """Build an MCP client for a server started as a subprocess: {"command": [...]} (stdio)."""
    if not s.get("command"):
        raise ValueError(f"MCP server {s.get('name')!r}: give 'command' (the server is started locally over stdio).")
    cmd = list(s["command"])
    env = {**get_default_environment(), **{k: os.environ[k] for k in FORWARDED_ENV if k in os.environ}}
    return Client(StdioServerParameters(command=cmd[0], args=cmd[1:], env=env, cwd=s.get("cwd")),
                  read_timeout_seconds=CONNECT_TIMEOUT_S * 5)


def openai_tool(name: str, tool: Any) -> dict[str, Any]:
    return {"type": "function", "function": {
        "name": name,
        "description": (tool.description or "").strip()[:1024],
        "parameters": tool.input_schema or {"type": "object", "properties": {}},
    }}


def result_text(res: Any) -> str:
    parts = [getattr(c, "text", "") for c in res.content or []]
    return "\n".join(p for p in parts if p)


def tool_arguments(raw: str | None) -> dict[str, Any] | None:
    """Decode the arguments of a tool call: a dict, or None if they are not a JSON object."""
    if not (raw or "").strip():
        return {}
    try:
        args = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return args if isinstance(args, dict) else None


def source_of(text: str) -> str | None:
    try:
        d = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None
    return d.get("source") if isinstance(d, dict) else None


class Orchestrator:
    def __init__(self, llm_config: dict[str, Any], clients: dict[str, Client], *,
                 tool_filters: dict[str, list[str]] | None = None, system_prompt: str = DEFAULT_SYSTEM_PROMPT,
                 max_turns: int = 6, max_result_chars: int = 8000, max_tool_calls: int = 10) -> None:
        self.cfg = llm_config
        self.clients = clients
        self.filters = tool_filters or {}
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        self.max_result_chars = max_result_chars
        self.max_tool_calls = max_tool_calls  # tools actually run per question (max_turns limits model requests)
        self.tools: list[dict[str, Any]] = []
        self.routes: dict[str, tuple[str, str]] = {}  # exposed name -> (server, original name)
        self.unavailable: dict[str, str] = {}  # server -> reason
        self._stack: AsyncExitStack | None = None

    async def __aenter__(self) -> "Orchestrator":
        self._stack = AsyncExitStack()
        found: list[tuple[str, Any]] = []
        for name, client in self.clients.items():
            try:
                await self._stack.enter_async_context(client)
                listed = (await client.list_tools()).tools
            except Exception as e:  # one unreachable server must not block the others
                self.unavailable[name] = f"{type(e).__name__}: {e}"
                print(f"warning: MCP server {name!r} unavailable ({self.unavailable[name]})", file=sys.stderr)
                continue
            keep = set(self.filters.get(name) or [])
            found += [(name, t) for t in listed if not keep or t.name in keep]
        names = [t.name for _, t in found]
        for server, t in found:
            exposed = t.name if names.count(t.name) == 1 else f"{server}__{t.name}"
            self.routes[exposed] = (server, t.name)
            self.tools.append(openai_tool(exposed, t))
        return self

    async def __aexit__(self, *exc: Any) -> None:
        if self._stack:
            await self._stack.aclose()

    def _request(self, messages: list[dict[str, Any]]) -> llm.Reply:
        payload: dict[str, Any] = {"model": self.cfg["model"], "messages": messages,
                                   "max_tokens": self.cfg.get("max_tokens", 4096)}
        payload.update(self.cfg.get("params") or {})
        if self.tools:
            payload["tools"] = self.tools
            # "auto" by default (mlx-engine accepts auto or none). llm.tool_choice = null omits it:
            # Ollama's OpenAI-compatible endpoint lists tool_choice as unsupported.
            tool_choice = self.cfg.get("tool_choice", "auto")
            if tool_choice:
                payload["tool_choice"] = tool_choice
        key = os.environ.get(self.cfg["api_key_env"]) if self.cfg.get("api_key_env") else None
        return llm.chat(self.cfg["base_url"], payload, key, self.cfg.get("timeout_s", 300), self.cfg.get("stream", True))

    async def _execute(self, name: str, arguments: str) -> tuple[str, ToolCall]:
        if name not in self.routes:
            text = f"ERROR: unknown tool {name!r}. Available tools: {', '.join(self.routes)}."
            return text, ToolCall("?", name, arguments, True, None, text[:200])
        server, original = self.routes[name]
        args = tool_arguments(arguments)
        if args is None:
            text = "ERROR: invalid JSON arguments. Call the tool again with a valid JSON object."
            return text, ToolCall(server, original, arguments, True, None, text)
        t0 = time.perf_counter()
        try:
            res = await self.clients[server].call_tool(original, args)
        except Exception as e:  # transport failure: report it to the model instead of crashing
            text = f"ERROR: MCP server {server!r} failed: {type(e).__name__}: {e}"
            return text, ToolCall(server, original, args, True, None, text[:200],
                                  seconds=time.perf_counter() - t0, result=text)
        text = result_text(res)
        source = source_of(text)
        if res.is_error:
            text = "ERROR: " + text
        if len(text) > self.max_result_chars:
            text = text[: self.max_result_chars] + " [...truncated]"
        return text, ToolCall(server, original, args, bool(res.is_error), source, text[:200],
                              seconds=time.perf_counter() - t0, result=text)

    async def answer(self, question: str) -> Answer:
        messages: list[dict[str, Any]] = [{"role": "system", "content": self.system_prompt},
                                          {"role": "user", "content": question}]
        out = Answer(text="")
        done: dict[tuple[str, str], tuple[str, ToolCall]] = {}  # successful calls of this question
        executed = 0
        for turn in range(1, self.max_turns + 1):
            out.turns = turn
            reply = await anyio.to_thread.run_sync(self._request, messages)
            out.llm_calls.append({"seconds": reply.total_s, "usage": reply.usage, "finish_reason": reply.finish_reason})
            if reply.error and not reply.truncated:
                out.error = reply.error
                out.text = f"Model error: {reply.error}"
                return out
            if not reply.tool_calls:
                out.text = llm.strip_reasoning(reply.content)
                if reply.truncated:
                    out.text += "\n[answer truncated: token limit reached]"
                return out
            calls = []
            for i, c in enumerate(reply.tool_calls):
                c["id"] = c.get("id") or f"call_{turn}_{i}"
                # Arguments sent back must be a JSON object: the Olala MLX server (mlx-engine)
                # rejects the whole request otherwise (HTTP 400). The tool result reports the error.
                args = tool_arguments(c["arguments"])
                calls.append({"id": c["id"], "type": "function", "function": {
                    "name": c["name"], "arguments": json.dumps({} if args is None else args, ensure_ascii=False)}})
            messages.append({"role": "assistant", "content": llm.strip_reasoning(reply.content), "tool_calls": calls})
            for c in reply.tool_calls:
                args = tool_arguments(c["arguments"])
                key = (c["name"], json.dumps(args, sort_keys=True)) if args is not None else None
                if key in done:
                    # Small models sometimes repeat a call (a DVF query takes several seconds):
                    # send back the earlier result instead of querying the API again.
                    text, trace = done[key]
                    text, trace = REPEATED_CALL_NOTE + text, replace(trace, repeated=True, seconds=0.0)
                elif executed >= self.max_tool_calls:
                    text = TOOL_LIMIT_NOTE.format(n=self.max_tool_calls)
                    server, original = self.routes.get(c["name"], ("?", c["name"]))
                    trace = ToolCall(server, original, args if args is not None else c["arguments"], True, None,
                                     text[:200], result=text)
                else:
                    executed += 1
                    text, trace = await self._execute(c["name"], c["arguments"])
                    if key and not trace.error:
                        done[key] = (text, trace)
                out.tool_calls.append(trace)
                messages.append({"role": "tool", "tool_call_id": c["id"], "content": text})
        out.text = "Maximum number of tool calls reached without a final answer."
        out.error = "max_turns"
        return out


def load_config(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_config(cfg: dict[str, Any]) -> None:
    """Raise ValueError if the configuration cannot be used (e.g. an old config with remote servers)."""
    if not isinstance(cfg.get("llm"), dict) or not cfg["llm"].get("base_url"):
        raise ValueError("'llm.base_url' is missing.")
    for s in cfg.get("mcp_servers") or []:
        if not s.get("command"):
            raise ValueError(f"MCP server {s.get('name')!r} has no 'command'. Only servers started on "
                             "this machine over stdio are supported (copy config.example.json again).")


def remote_llm_host(llm_cfg: dict[str, Any]) -> str | None:
    """The host of llm.base_url when it is not this machine, else None."""
    host = urllib.parse.urlparse(llm_cfg.get("base_url") or "").hostname
    return None if host in LOCAL_HOSTS else (host or "?")


def warn_if_remote(llm_cfg: dict[str, Any]) -> None:
    host = remote_llm_host(llm_cfg)
    if host:
        print(f"warning: llm.base_url points to {host}, not to this machine: questions and tool results "
              "will be sent there. This project is meant for a local model.", file=sys.stderr)


def from_config(cfg: dict[str, Any]) -> Orchestrator:
    servers = cfg.get("mcp_servers") or []
    return Orchestrator(
        cfg["llm"],
        {s["name"]: client_from_config(s) for s in servers},
        tool_filters={s["name"]: s["tools"] for s in servers if s.get("tools")},
        system_prompt=cfg.get("system_prompt", DEFAULT_SYSTEM_PROMPT),
        max_turns=cfg.get("max_turns", 6),
        max_result_chars=cfg.get("max_result_chars", 8000),
        max_tool_calls=cfg.get("max_tool_calls", 10),
    )


def show(a: Answer) -> None:
    print(a.text)
    if a.tool_calls:
        print("\n--- tools called ---")
        for t in a.tool_calls:
            state = "ERROR" if t.error else "repeated, not run again" if t.repeated else "ok"
            print(f"- {t.server}/{t.tool} {json.dumps(t.arguments, ensure_ascii=False)}: {state}"
                  + (f" - source: {t.source}" if t.source else ""))


async def _main(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    warn_if_remote(cfg["llm"])
    key_env = cfg["llm"].get("api_key_env")
    if key_env and not os.environ.get(key_env):
        print(f"warning: {key_env} is not set (environment or {args.env_file}): requests are sent without a key",
              file=sys.stderr)
    async with from_config(cfg) as orch:
        if args.check:
            print("MCP tools:", ", ".join(orch.routes) or "(none)")
            for name, reason in orch.unavailable.items():
                print(f"Unavailable MCP server {name}: {reason}")
            c = cfg["llm"]
            reply = await anyio.to_thread.run_sync(lambda: llm.chat(
                c["base_url"],
                {"model": c["model"], "max_tokens": 512, **(c.get("params") or {}),
                 "messages": [{"role": "user", "content": "Reply only: OK"}]},
                os.environ.get(c.get("api_key_env") or "", None), 120, c.get("stream", True)))
            print("Model:", f"FAILED {reply.error}" if reply.error else repr(llm.strip_reasoning(reply.content)))
            return
        if args.question:
            show(await orch.answer(args.question))
            return
        print("Question (empty line to quit):")
        while True:
            try:
                q = (await anyio.to_thread.run_sync(input, "> ")).strip()
            except EOFError:
                break
            if not q:
                break
            show(await orch.answer(q))
            print()


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--question")
    ap.add_argument("--check", action="store_true", help="test the connection to the model and the MCP servers")
    ap.add_argument("--env-file", default=".env", help="file of KEY=VALUE lines read at startup (default: .env)")
    args = ap.parse_args(argv)
    try:
        envfile.load(args.env_file)
    except ValueError as e:
        sys.exit(f"{args.env_file}: {e}")
    if not os.path.exists(args.config):
        sys.exit(f"Config not found: {args.config} (copy config.example.json)")
    cfg = load_config(args.config)
    try:
        check_config(cfg)
    except ValueError as e:
        sys.exit(f"{args.config}: {e}")
    anyio.run(_main, args, cfg)


if __name__ == "__main__":
    main()
