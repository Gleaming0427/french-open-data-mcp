"""The "french-open-data" MCP server, over stdio (the client starts it on the same machine).

Usage:
  python -m fr_open_data.server

The LEGIFRANCE_* variables can also be set in a .env file in the current
directory (see .env.example); a variable already set in the environment wins.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Annotated, Any, Callable

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import ToolAnnotations
from pydantic import Field

from . import __version__, companies, dvf, envfile, legifrance, municipalities
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


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--env-file", default=".env", help="file of KEY=VALUE lines read at startup (default: .env)")
    args = ap.parse_args(argv)
    try:
        envfile.load(args.env_file)
    except ValueError as e:
        sys.exit(f"{args.env_file}: {e}")

    build_server().run("stdio")


if __name__ == "__main__":
    main()
