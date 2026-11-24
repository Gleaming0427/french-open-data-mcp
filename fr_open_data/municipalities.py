"""Municipalities (communes): the Découpage administratif API (geo.api.gouv.fr).

Used to turn a municipality name into its INSEE code, which the DVF tool needs.
"""

from __future__ import annotations

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


def find(name: str, postcode: str | None = None, limit: int = 5) -> dict[str, Any]:
    if not (name or "").strip():
        raise ValueError("Give a municipality name.")
    d = request_json(
        COMMUNES_URL,
        {
            "nom": name.strip(),
            "codePostal": postcode,
            "fields": "nom,code,codesPostaux,codeDepartement,population",
            "limit": max(1, min(int(limit), 20)),
        },
        source_name="Découpage administratif API",
    )
    results = []
    for c in d or []:
        item = {
            "name": c.get("nom"),
            "insee_code": c.get("code"),
            "department": c.get("codeDepartement"),
            "postcodes": c.get("codesPostaux"),
            "population": c.get("population"),
        }
        if c.get("code") in ARRONDISSEMENTS:
            item["note"] = "For DVF, use an arrondissement INSEE code: " + ", ".join(ARRONDISSEMENTS[c["code"]][1])
        results.append(item)
    return {"source": SOURCE, "results": results}
