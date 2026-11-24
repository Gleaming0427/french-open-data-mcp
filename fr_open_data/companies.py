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

from . import municipalities
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
_INSEE_CODE = re.compile(r"\d[\dAB]\d{3}")
_NAF_CODE = re.compile(r"\d{2}\.?\d{2}[A-Z]")
_SECTIONS = set("ABCDEFGHIJKLMNOPQRSTU")


def _code_list(value: str | None, check: Any, message: str) -> str | None:
    """Normalise a comma-separated list of codes; raise ValueError if one is invalid."""
    if not (value or "").strip():
        return None
    codes = [c.strip().upper() for c in value.split(",") if c.strip()]
    if not all(check(c) for c in codes):
        raise ValueError(message)
    return ",".join(codes)


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
    text: str = "",
    postcode: str | None = None,
    department: str | None = None,
    naf_code: str | None = None,
    include_closed: bool = False,
    limit: int = 5,
    municipality_code: str | None = None,
    activity_section: str | None = None,
    municipality: str | None = None,
) -> dict[str, Any]:
    """Search companies. postcode, municipality (name), municipality_code and department filter on
    any establishment; naf_code and activity_section apply to the main activity of the company."""
    notes = []
    if _NAF_CODE.fullmatch((text or "").strip().upper()) and not naf_code:
        # Seen in a benchmark: a small model put the NAF code in the text, which then matched nothing.
        naf_code, text = text.strip(), ""
        notes.append(f"The text {naf_code!r} is a NAF code: it was used as naf_code.")
    if (municipality or "").strip():
        code, name, note = municipalities.resolve(municipality, municipality_code)
        if municipality_code and municipality_code.strip().upper() != code:
            notes.append(f"municipality_code {municipality_code} was not used: {name} has the INSEE code {code}.")
        municipality_code = code
        if note:
            notes.append(note)
    municipality_code = _code_list(municipality_code, _INSEE_CODE.fullmatch,
                                   "municipality_code: 5-character INSEE codes, e.g. 31555 (use find_municipality).")
    activity_section = _code_list(activity_section, _SECTIONS.__contains__,
                                  "activity_section: letters A to U, e.g. J (information and communication).")
    naf_code = _code_list(naf_code, _NAF_CODE.fullmatch, "naf_code: NAF/APE codes such as 62.02A, comma-separated.")
    if not (text or "").strip() and not (postcode or department or naf_code or municipality_code or activity_section):
        raise ValueError("Give at least a name, an address or a filter.")
    params = {
        "q": (text or "").strip(),
        "code_postal": postcode,
        "code_commune": municipality_code,
        "departement": department,
        "activite_principale": naf_code,
        "section_activite_principale": activity_section,
        "etat_administratif": None if include_closed else "A",
        "per_page": max(1, min(int(limit), MAX_PER_PAGE)),
        "page": 1,
    }
    d = request_json(SEARCH_URL, params, source_name="Recherche d'entreprises API")
    results = [summarize(r) for r in d.get("results") or []]
    total = d.get("total_results")
    out = {
        "source": SOURCE,
        "filters": {k: v for k, v in params.items() if v not in (None, "") and k not in ("per_page", "page")},
        "total_results": total,
        # Benchmark 2026-11-24: asked "how many", the model twice answered with the number of
        # companies listed (5) instead of total_results.
        "count": (f"{total} companies match these filters in total; only the first {len(results)} are listed "
                  "below. To answer 'how many', use total_results." if total is not None else None),
        "results": results,
    }
    if notes:
        out["notes"] = notes
    return out


def get_profile(siren: str) -> dict[str, Any]:
    s = normalize_siren(siren)
    d = request_json(SEARCH_URL, {"q": s, "per_page": 1}, source_name="Recherche d'entreprises API")
    for r in d.get("results") or []:
        if r.get("siren") == s:
            return {"source": SOURCE, "company": profile(r)}
    raise SourceError(f"SIREN {s} not found (wrong number, or the company is not publicly disclosed).")
