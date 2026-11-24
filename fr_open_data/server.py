"""The "french-open-data" MCP server.

Usage:
  python -m fr_open_data.server                       # stdio (client on the same machine)
  python -m fr_open_data.server --http --port 8765    # Streamable HTTP on 127.0.0.1

Over HTTP, if MCP_TOKEN is set, every request must carry
"Authorization: Bearer <MCP_TOKEN>" (the "Bearer" option in Open WebUI).
To expose it on the Internet, put it behind an HTTPS reverse proxy and declare
the domain name with --domain (DNS rebinding protection from the MCP SDK).
"""

from __future__ import annotations

import argparse
import hmac
import json
import os
from typing import Annotated, Any, Callable

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from mcp_types import ToolAnnotations
from pydantic import Field

from . import __version__, companies, dvf, legifrance, municipalities
from .http import SourceError

INSTRUCTIONS = (
    "Read-only tools over French public data: companies (Sirene/RNE), property prices (DVF) "
    "and, when configured, Légifrance. Answer from the tool results only, cite the 'source' "
    "field and report any warning. If a tool returns an error, say so instead of answering from memory."
)
READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=True)


def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def _run(fn: Callable[..., Any], *args: Any) -> str:
    """Turn expected failures into ToolError, whose message reaches the model."""
    try:
        return _json(fn(*args))
    except (ValueError, SourceError) as e:
        raise ToolError(str(e)) from e


def search_companies(
    text: Annotated[str, Field(description="Name, acronym, address, director name, SIREN or SIRET.")],
    postcode: Annotated[str | None, Field(description="5-digit postcode (optional). Filters on any establishment, not only the head office.")] = None,
    department: Annotated[str | None, Field(description="Department code, e.g. 21 or 2A (optional).")] = None,
    naf_code: Annotated[str | None, Field(description="NAF/APE activity code, e.g. 56.10A (optional).")] = None,
    include_closed: Annotated[bool, Field(description="Include closed companies.")] = False,
    limit: Annotated[int, Field(ge=1, le=25, description="Number of results (1 to 25).")] = 5,
) -> str:
    """Search French companies, associations or public bodies (Recherche d'entreprises API).

    Returns SIREN, name, status, NAF activity code, workforce band, head office and whether
    the company objects to commercial prospecting. For details, use company_profile.
    """
    return _run(companies.search, text, postcode, department, naf_code, include_closed, limit)


def company_profile(
    siren: Annotated[str, Field(description="SIREN (9 digits) or SIRET (14 digits).")],
) -> str:
    """Profile of a French company: identity, directors, published financials, labels, collective agreements."""
    return _run(companies.get_profile, siren)


def find_municipality(
    name: Annotated[str, Field(description="Municipality name, e.g. Beaune.")],
    postcode: Annotated[str | None, Field(description="Postcode to disambiguate (optional).")] = None,
) -> str:
    """Find the INSEE code of a French municipality (needed by property_prices)."""
    return _run(municipalities.find, name, postcode)


def property_prices(
    insee_code: Annotated[str, Field(description="5-character INSEE municipality code, e.g. 21054.")],
    period: Annotated[str | None, Field(
        description="Year (e.g. 2024) or half-year (e.g. 2026-S1). Default: latest full year."
    )] = None,
) -> str:
    """House and apartment sale prices in a French municipality (DVF): medians and quartiles per m².

    Aggregated statistics only (no individual transaction). No data for Alsace, Moselle
    and Mayotte. Paris, Lyon and Marseille: use an arrondissement code.
    """
    return _run(dvf.property_prices, insee_code, period)


def search_legifrance(
    text: Annotated[str, Field(description="Words to search for (in French), e.g. 'bail commercial résiliation'.")],
    collection: Annotated[str, Field(description="CODE_DATE (codes), LODA_DATE (laws and decrees), JURI, CETAT, "
                                                 "CONSTIT, JORF, KALI, CNIL, CIRC, ACCO or ALL.")] = "CODE_DATE",
    limit: Annotated[int, Field(ge=1, le=20, description="Number of results.")] = 5,
) -> str:
    """Search Légifrance (French codes, laws, case law...). Returns titles and article ids."""
    return _run(legifrance.search, text, collection, limit)


def read_legifrance_article(
    article_id: Annotated[str, Field(description="Légifrance article id, e.g. LEGIARTI000006419283.")],
) -> str:
    """Text of a Légifrance article, with its dates of validity."""
    return _run(legifrance.read_article, article_id)


def build_server(with_legifrance: bool | None = None) -> MCPServer:
    srv = MCPServer(name="french-open-data", version=__version__, instructions=INSTRUCTIONS)
    tools = [search_companies, company_profile, find_municipality, property_prices]
    if legifrance.is_configured() if with_legifrance is None else with_legifrance:
        tools += [search_legifrance, read_legifrance_article]
    for fn in tools:
        srv.add_tool(fn, annotations=READ_ONLY)
    return srv


class RequireToken:
    """ASGI middleware: reject HTTP requests without "Authorization: Bearer <token>"."""

    def __init__(self, app: Any, token: str) -> None:
        self.app, self.expected = app, f"Bearer {token}".encode()

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] == "http":
            received = dict(scope.get("headers") or []).get(b"authorization", b"")
            if not hmac.compare_digest(received, self.expected):
                await send({"type": "http.response.start", "status": 401,
                            "headers": [(b"content-type", b"application/json"), (b"www-authenticate", b"Bearer")]})
                await send({"type": "http.response.body", "body": b'{"error":"missing or invalid token"}'})
                return
        await self.app(scope, receive, send)


def http_app(srv: MCPServer, host: str, domains: list[str], token: str | None) -> Any:
    security = None
    if domains:
        security = TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=[*domains, "127.0.0.1:*", "localhost:*"],
            allowed_origins=[f"https://{d}" for d in domains],
        )
    app = srv.streamable_http_app(host=host, transport_security=security)
    return RequireToken(app, token) if token else app


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--http", action="store_true", help="Streamable HTTP (default: stdio)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--domain", action="append", default=[], help="accepted public domain name (repeatable)")
    args = ap.parse_args(argv)

    srv = build_server()
    if not args.http:
        srv.run("stdio")
        return
    token = os.environ.get("MCP_TOKEN")
    if args.host not in ("127.0.0.1", "localhost", "::1") and not token:
        ap.error("listening beyond localhost: set MCP_TOKEN")
    import uvicorn

    uvicorn.run(http_app(srv, args.host, args.domain, token), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
