"""Municipalities (communes): the Découpage administratif API (geo.api.gouv.fr).

Turns a municipality name into its INSEE code. The DVF and company tools also accept a
name and call `resolve` themselves: in a benchmark on 2026-11-24, a small model (Olala
mini) called find_municipality correctly, then often passed a different code to the next
tool (e.g. 21054 instead of Dijon's 21231).
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from .http import request_json

COMMUNES_URL = "https://geo.api.gouv.fr/communes"
SOURCE = "Découpage administratif API (geo.api.gouv.fr)"

# Paris, Marseille and Lyon: DVF data is published per arrondissement
# (checked on the Tabular API: 0 rows for 75056, 13055 and 69123).
ARRONDISSEMENTS = {
    "75056": ("Paris", [f"751{n:02d}" for n in range(1, 21)]),
    "13055": ("Marseille", [f"132{n:02d}" for n in range(1, 17)]),
    "69123": ("Lyon", [f"6938{n}" for n in range(1, 10)]),
}
_CITY_CODES = {city.lower(): codes for city, codes in ARRONDISSEMENTS.values()}
# "Paris 11e", "Paris 11e arrondissement", "11e arrondissement de Paris", "Lyon 3", "Marseille 1er"
_ARRONDISSEMENT = re.compile(
    r"^(?:(?P<city1>paris|lyon|marseille)\s*(?P<n1>\d{1,2})\s*(?:e|er|eme|ème)?(?:\s+arrondissement)?"
    r"|(?P<n2>\d{1,2})\s*(?:e|er|eme|ème)?\s+arrondissement\s+(?:de\s+)?(?P<city2>paris|lyon|marseille))$")


def normalize(name: str) -> str:
    """Lower case, no accents, hyphens and apostrophes as spaces: "Saint-Étienne" -> "saint etienne"."""
    text = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[-'’]", " ", text)).strip()


def arrondissement_code(name: str) -> str | None:
    """INSEE code of a Paris, Lyon or Marseille arrondissement written as a name, else None."""
    m = _ARRONDISSEMENT.match(normalize(name))
    if not m:
        return None
    city, n = (m["city1"], m["n1"]) if m["city1"] else (m["city2"], m["n2"])
    codes = _CITY_CODES[city]
    return codes[int(n) - 1] if 1 <= int(n) <= len(codes) else None


def _search(name: str, postcode: str | None, limit: int) -> list[dict[str, Any]]:
    d = request_json(
        COMMUNES_URL,
        {
            "nom": name.strip(),
            "codePostal": postcode,
            "fields": "nom,code,codeDepartement,population",
            # Rank by population: without it, "Paris" returns two "Parisot" before Paris
            # (checked on 2026-11-24). `boost` is documented in the API's definition.yml.
            "boost": "population",
            "limit": max(1, min(int(limit), 20)),
        },
        source_name="Découpage administratif API",
    )
    return [{"name": c.get("nom"), "insee_code": c.get("code"), "department": c.get("codeDepartement"),
             "population": c.get("population")} for c in d or []]


def find(name: str, postcode: str | None = None, limit: int = 5) -> dict[str, Any]:
    """Municipalities matching a name. When some names match exactly, only those are returned."""
    if not (name or "").strip():
        raise ValueError("Give a municipality name.")
    code = arrondissement_code(name)
    if code:
        return {"source": SOURCE, "results": [{"name": name.strip(), "insee_code": code}]}
    results = _search(name, postcode, limit)
    exact = [r for r in results if normalize(r["name"]) == normalize(name)]
    for r in exact or results:
        if r["insee_code"] in ARRONDISSEMENTS:
            r["note"] = "For DVF, use an arrondissement INSEE code: " + ", ".join(ARRONDISSEMENTS[r["insee_code"]][1])
    return {"source": SOURCE, "results": exact or results}


def resolve(name: str, insee_code: str | None = None) -> tuple[str, str, str | None]:
    """(INSEE code, name, note) for a municipality name. Several municipalities with the same
    name: the given insee_code if it is one of them, else the most populated one (with a note).
    Raises ValueError when no municipality has this name."""
    code = arrondissement_code(name)
    if code:
        return code, name.strip(), None
    if re.fullmatch(r"\d[\dAB]\d{3}", (name or "").strip().upper()):
        # Benchmark 2026-11-24: the model put the INSEE code (75115) in the name field.
        return name.strip().upper(), name.strip().upper(), None
    results = _search(name, None, 20)
    exact = [r for r in results if normalize(r["name"]) == normalize(name)]
    if not exact:
        close = ", ".join(f"{r['name']} ({r['insee_code']})" for r in results[:5]) or "none"
        raise ValueError(f"No municipality is named {name!r}. Closest names: {close}.")
    chosen = next((r for r in exact if r["insee_code"] == (insee_code or "").strip().upper()), exact[0])
    note = None
    others = [r for r in exact if r is not chosen]
    if others:
        note = (f"Other municipalities are named {chosen['name']}: "
                + ", ".join(f"{r['insee_code']} (department {r['department']})" for r in others)
                + ". Give insee_code to choose one.")
    return chosen["insee_code"], chosen["name"], note
