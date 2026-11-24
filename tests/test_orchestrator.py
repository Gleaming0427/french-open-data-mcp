"""Offline end-to-end tests: fake LLM (local HTTP) + in-memory MCP servers."""

import json
import os
import threading
import unittest

from mcp import Client
from mcp.server.mcpserver import MCPServer

from fr_open_data import llm
from fr_open_data.orchestrator import Orchestrator, client_from_config
from fr_open_data.server import build_server
from tools import fake_llm


def test_server(name: str = "test") -> MCPServer:
    srv = MCPServer(name=name)

    @srv.tool()
    def search_companies(text: str) -> str:
        """Fake search."""
        return json.dumps({"source": "Fake source", "results": [{"name": text.upper()}]}, ensure_ascii=False)

    @srv.tool()
    def company_profile(siren: str) -> str:
        """Fake profile."""
        if siren == "000000000":
            raise ValueError("unknown SIREN")
        return json.dumps({"source": "Fake source", "siren": siren})

    return srv


class FakeLlm(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = fake_llm.make_server(0, key="secret")
        cls.url = f"http://127.0.0.1:{cls.http.server_address[1]}/v1"
        threading.Thread(target=cls.http.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()


class TestLlmClient(FakeLlm):
    def test_tool_call_rebuilt(self):
        tools = [{"type": "function", "function": {"name": "company_profile", "parameters": {}}}]
        for stream in (True, False):
            r = llm.chat(self.url, {"model": "f", "messages": [{"role": "user", "content": "SIREN 123456789"}],
                                    "tools": tools}, "secret", stream=stream)
            self.assertIsNone(r.error)
            self.assertEqual(r.tool_calls[0]["name"], "company_profile")
            self.assertEqual(json.loads(r.tool_calls[0]["arguments"]), {"siren": "123456789"})
            self.assertTrue(r.reasoning)

    def test_wrong_key(self):
        r = llm.chat(self.url, {"model": "f", "messages": [{"role": "user", "content": "x"}]}, "wrong")
        self.assertTrue(r.error.startswith("HTTP 401"))

    def test_strip_reasoning(self):
        self.assertEqual(llm.strip_reasoning("<think>blah</think> Answer"), "Answer")
        self.assertEqual(llm.strip_reasoning("blah</think> Answer"), "Answer")


class TestOrchestrator(FakeLlm, unittest.IsolatedAsyncioTestCase):
    def cfg(self, stream=True):
        return {"base_url": self.url, "model": "fake", "api_key_env": "FAKE_LLM_KEY", "stream": stream}

    async def asyncSetUp(self):
        os.environ["FAKE_LLM_KEY"] = "secret"

    async def test_full_loop(self):
        for stream in (True, False):
            async with Orchestrator(self.cfg(stream), {"t": Client(test_server())}) as o:
                a = await o.answer("bakery in Beaune")
            self.assertIsNone(a.error)
            self.assertEqual(a.turns, 2)
            self.assertEqual(len(a.tool_calls), 1)
            self.assertEqual(a.tool_calls[0].tool, "search_companies")
            self.assertEqual(a.tool_calls[0].source, "Fake source")
            self.assertIn("BAKERY IN BEAUNE", a.text)

    async def test_tool_error_reaches_the_model(self):
        async with Orchestrator(self.cfg(), {"t": Client(test_server())}) as o:
            a = await o.answer("SIREN 000000000")
        self.assertTrue(a.tool_calls[0].error)
        self.assertIn("ERROR", a.text)

    async def test_invalid_arguments_do_not_break_the_loop(self):
        # The model writes arguments that are not JSON: the tool reports an error and the
        # next request must still be accepted by a server that checks past tool calls.
        async with Orchestrator(self.cfg(), {"t": Client(test_server())}) as o:
            a = await o.answer("invalid arguments")
        self.assertIsNone(a.error)
        self.assertEqual(a.turns, 2)
        self.assertTrue(a.tool_calls[0].error)
        self.assertIn("invalid JSON arguments", a.text)

    async def test_repeated_call_is_not_run_again(self):
        srv = test_server()
        runs = []

        @srv.tool()
        def property_prices(insee_code: str) -> str:
            """Fake prices."""
            runs.append(insee_code)
            return json.dumps({"source": "Fake source", "median": 1})

        async with Orchestrator(self.cfg(), {"t": Client(srv)}) as o:
            a = await o.answer("repeat price 21054")
        self.assertIsNone(a.error)
        self.assertEqual(runs, ["21054"])
        self.assertEqual([t.repeated for t in a.tool_calls], [False, True])
        self.assertEqual(a.tool_calls[1].source, "Fake source")
        self.assertIn("already called", a.text)

    async def test_name_collisions_are_prefixed(self):
        clients = {"a": Client(test_server("a")), "b": Client(test_server("b"))}
        async with Orchestrator(self.cfg(), clients, tool_filters={"b": ["company_profile"]}) as o:
            self.assertEqual(sorted(o.routes), ["a__company_profile", "b__company_profile", "search_companies"])
            text, trace = await o._execute("missing", "{}")
            self.assertTrue(trace.error)
            text, trace = await o._execute("search_companies", "{not json")
            self.assertIn("JSON", text)

    async def test_unreachable_server_is_skipped(self):
        down = client_from_config({"name": "down", "command": ["fr-open-data-no-such-command"]})
        clients = {"ok": Client(test_server()), "down": down}
        async with Orchestrator(self.cfg(), clients) as o:
            self.assertIn("down", o.unavailable)
            self.assertEqual(sorted(o.routes), ["company_profile", "search_companies"])

    async def test_real_server_lists_tools(self):
        async with Client(build_server(with_legifrance=False)) as c:
            names = sorted(t.name for t in (await c.list_tools()).tools)
        self.assertEqual(names, ["company_profile", "find_municipality", "property_prices", "search_companies"])
        async with Client(build_server(with_legifrance=True)) as c:
            self.assertEqual(len((await c.list_tools()).tools), 6)
            r = await c.call_tool("property_prices", {"insee_code": "75056"})
        self.assertTrue(r.is_error)
        self.assertIn("arrondissement", r.content[0].text)


if __name__ == "__main__":
    unittest.main()
