"""Companies: the Recherche d'entreprises API (DINUM, French government).

Documentation: https://recherche-entreprises.api.gouv.fr/docs/
Specification: https://recherche-entreprises.api.gouv.fr/openapi.json

Facts taken from the official documentation (checked on 2026-11-23):
- open access, no API key;
- at most 7 requests per second per IP address and 30 per second per ASN
  ("likely to be hit on public clouds"); HTTP 429 with Retry-After when exceeded;
- at most 25 results per page;
- companies that opted out of public disclosure ("non-diffusibles") are not returned;
- this is not full access to the Sirene database (use INSEE's Sirene API for that).

Responses are reduced to the useful fields to keep the model's context small.
Directors' birth dates and nationalities are not passed on (data minimisation).
"""

from __future__ import annotations

import re
from typing import Any

from .http import SourceError, request_json

SEARCH_URL = "https://recherche-entreprises.api.gouv.fr/search"
SOURCE = "Recherche d'entreprises API (DINUM) - Sirene (INSEE) and RNE (INPI) data"
MAX_PER_PAGE = 25

# INSEE workforce size bands. Official French labels:
# annuaire-entreprises-data-gouv-fr/search-api, app/labels/tranches-effectifs.json
WORKFORCE_BANDS = {
    "NN": "No employees (non-employer unit)",
    "00": "0 employees at year end",
    "01": "1 or 2 employees",
    "02": "3 to 5 employees",
    "03": "6 to 9 employees",
    "11": "10 to 19 employees",
    "12": "20 to 49 employees",
    "21": "50 to 99 employees",
    "22": "100 to 199 employees",
    "31": "200 to 249 employees",
    "32": "250 to 499 employees",
    "41": "500 to 999 employees",
    "42": "1,000 to 1,999 employees",
    "51": "2,000 to 4,999 employees",
    "52": "5,000 to 9,999 employees",
    "53": "10,000 employees or more",
}

_STATUS = {"A": "active", "C": "closed"}


def normalize_siren(value: str) -> str:
    """Accept a SIREN (9 digits) or a SIRET (14 digits), with or without spaces."""
    digits = re.sub(r"\D", "", value or "")
    if len(digits) == 14:
        digits = digits[:9]
    if len(digits) != 9:
        raise ValueError("A SIREN has 9 digits (a SIRET has 14).")
    return digits


def summarize(r: dict[str, Any]) -> dict[str, Any]:
    """Reduce a /search result to its main fields."""
    hq = r.get("siege") or {}
    band = r.get("tranche_effectif_salarie")
    return {
        "siren": r.get("siren"),
        "name": r.get("nom_complet"),
        "acronym": r.get("sigle"),
        "status": _STATUS.get(r.get("etat_administratif"), r.get("etat_administratif")),
        "created": r.get("date_creation"),
        "closed": r.get("date_fermeture"),
        "naf_activity_code": r.get("activite_principale"),
        "legal_form_code": r.get("nature_juridique"),
        "company_category": r.get("categorie_entreprise"),
        "workforce": WORKFORCE_BANDS.get(band, band) if band else None,
        "workforce_year": r.get("annee_tranche_effectif_salarie"),
        "open_establishments": r.get("nombre_etablissements_ouverts"),
        "head_office": {
            "siret": hq.get("siret"),
            "address": hq.get("adresse"),
            "postcode": hq.get("code_postal"),
            "municipality": hq.get("libelle_commune"),
            "municipality_code": hq.get("commune"),
        },
        # True = the company objects to the reuse of its data for commercial prospecting
        # (GDPR art. 21(2), French Commercial Code art. R.123-320). Source: RNE.
        "objects_to_commercial_prospecting": r.get("opposition_diffusion_commerciale"),
    }


def _director(d: dict[str, Any]) -> dict[str, Any]:
    if d.get("type_dirigeant") == "personne morale":
        return {"type": "legal entity", "name": d.get("denomination"), "siren": d.get("siren"),
                "role": d.get("qualite")}
    return {"type": "natural person", "last_name": d.get("nom"), "first_names": d.get("prenoms"),
            "role": d.get("qualite")}


def profile(r: dict[str, Any]) -> dict[str, Any]:
    """Fuller profile: summary + directors, published financials, labels."""
    out = summarize(r)
    extra = r.get("complements") or {}
    vat = r.get("tva")
    out.update({
        "directors": [_director(d) for d in (r.get("dirigeants") or [])],
        "financials": r.get("finances"),  # {year: {ca: revenue, resultat_net: net income}} when published
        "vat_number": (vat[0] if vat else None) if isinstance(vat, list) else vat,
        "collective_agreements_idcc": extra.get("liste_idcc"),
        "labels_and_statuses": sorted(k for k, v in extra.items() if k.startswith("est_") and v is True),
        "insee_updated": r.get("date_mise_a_jour_insee"),
        "rne_updated": r.get("date_mise_a_jour_rne"),
    })
    return out


def search(
    text: str,
    postcode: str | None = None,
    department: str | None = None,
    naf_code: str | None = None,
    include_closed: bool = False,
    limit: int = 5,
) -> dict[str, Any]:
    if not (text or "").strip() and not (postcode or department or naf_code):
        raise ValueError("Give at least a name, an address or a filter.")
    params = {
        "q": (text or "").strip(),
        "code_postal": postcode,
        "departement": department,
        "activite_principale": naf_code,
        "etat_administratif": None if include_closed else "A",
        "per_page": max(1, min(int(limit), MAX_PER_PAGE)),
        "page": 1,
    }
    d = request_json(SEARCH_URL, params, source_name="Recherche d'entreprises API")
    return {
        "source": SOURCE,
        "total_results": d.get("total_results"),
        "results": [summarize(r) for r in d.get("results") or []],
    }


def get_profile(siren: str) -> dict[str, Any]:
    s = normalize_siren(siren)
    d = request_json(SEARCH_URL, {"q": s, "per_page": 1}, source_name="Recherche d'entreprises API")
    for r in d.get("results") or []:
        if r.get("siren") == s:
            return {"source": SOURCE, "company": profile(r)}
    raise SourceError(f"SIREN {s} not found (wrong number, or the company is not publicly disclosed).")
