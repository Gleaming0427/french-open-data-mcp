"""Property prices: "Demandes de valeurs foncières géolocalisées" (DVF), via the data.gouv.fr Tabular API.

Dataset: https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees/
(derived from the DGFiP DVF file, Licence Ouverte 2.0, updated twice a year).

Why the Tabular API and not the per-municipality files:
the October 2026 release replaced the per-municipality tree
(files.data.gouv.fr/geo-dvf/latest/csv/...) with yearly files. The old tree is
now listed as "[ARCHIVE] ... livraison avril - suppression au 31/11/2026". The
yearly files are queryable through the Tabular API since 2026-11-18 (dataset
history). The Tabular API specification documents the `code_commune__exact`
filter used here.

Legal constraints stated by the DGFiP on the source dataset:
- article R112 A-3 of the Livre des procédures fiscales: use must not allow the
  re-identification, even indirect, of the people concerned;
- reuse must not allow indexing by external search engines.
For this reason the tool only returns aggregated statistics per municipality,
never an address or an individual transaction.

Coverage: no data for Alsace, Moselle and Mayotte (departments 57, 67, 68, 976).

Method (documented approximation, not an official index):
1. rows of the municipality are grouped by `id_mutation`;
2. keep transactions of nature "Vente" (sale) with a property value > 0;
3. keep those with exactly one dwelling (house or apartment), possibly with
   outbuildings ("Dépendance"), and no commercial or industrial premises;
4. price per m² = property value / built floor area of the dwelling.
The property value includes land and outbuildings, so the price per m² of houses
is overestimated when the plot is large.
"""

from __future__ import annotations

import re
import statistics
import time
from collections import defaultdict
from typing import Any

from .http import SourceError, request_json
from .municipalities import ARRONDISSEMENTS

DATASET_URL = "https://www.data.gouv.fr/api/1/datasets/demandes-de-valeurs-foncieres-geolocalisees/"
TABULAR_URL = "https://tabular-api.data.gouv.fr/api/resources/{rid}/data/"
SOURCE = "DVF géolocalisées (DGFiP, processed by data.gouv.fr), via the data.gouv.fr Tabular API"
COLUMNS = [
    "id_mutation", "date_mutation", "nature_mutation", "valeur_fonciere", "id_parcelle",
    "lot1_numero", "code_type_local", "type_local", "surface_reelle_bati",
    "nombre_pieces_principales", "nom_commune",
]
PAGE_SIZE = 200
MAX_PAGES = 60  # 12,000 rows: beyond that the result is flagged as partial
UNCOVERED_DEPARTMENTS = {"57", "67", "68", "976"}
DWELLING_TYPES = {1: "house", 2: "apartment"}  # DVF code_type_local 1 = Maison, 2 = Appartement
COMMERCIAL_PREMISES = 4  # "Local industriel. commercial ou assimilé"
SMALL_SAMPLE = 10

_resource_cache: tuple[float, dict[str, tuple[str, str]]] | None = None


def department_of(insee_code: str) -> str:
    return insee_code[:3] if insee_code.startswith("97") else insee_code[:2]


def resources_by_period(force: bool = False) -> dict[str, tuple[str, str]]:
    """{"2025" or "2026-S1": (resource id, title)}, read from data.gouv.fr (cached 1 h)."""
    global _resource_cache
    if not force and _resource_cache and time.time() - _resource_cache[0] < 3600:
        return _resource_cache[1]
    d = request_json(DATASET_URL, source_name="data.gouv.fr catalogue")
    out: dict[str, tuple[str, str]] = {}
    for r in d.get("resources") or []:
        title = (r.get("title") or "").strip()
        m = re.fullmatch(r"DVF (\d{4})", title)
        if m:
            out[m[1]] = (r["id"], title)
            continue
        m = re.fullmatch(r"DVF (\d{4}) \((1er|2nd) semestre\)", title)
        if m:
            out[f"{m[1]}-S{1 if m[2] == '1er' else 2}"] = (r["id"], title)
    if not out:
        raise SourceError("No yearly DVF resource found on data.gouv.fr (has the dataset layout changed?).")
    _resource_cache = (time.time(), out)
    return out


def latest_full_year(periods: dict[str, Any]) -> str:
    years = sorted(p for p in periods if p.isdigit())
    if not years:
        raise SourceError("No full year available.")
    return years[-1]


def read_rows(rid: str, insee_code: str) -> tuple[list[dict[str, Any]], bool]:
    """All rows for one municipality (paginated). Returns (rows, complete)."""
    url = TABULAR_URL.format(rid=rid)
    params = {"code_commune__exact": insee_code, "page_size": PAGE_SIZE, "columns": ",".join(COLUMNS)}
    rows: list[dict[str, Any]] = []
    for page in range(1, MAX_PAGES + 1):
        d = request_json(url, {**params, "page": page}, source_name="data.gouv.fr Tabular API", timeout_s=60)
        rows.extend(d.get("data") or [])
        if not (d.get("links") or {}).get("next"):
            return rows, True
    return rows, False


def _num(v: Any) -> float | None:
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def dwelling_sales(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Apply the method described above. Returns (kept sales, number of sales of any kind)."""
    by_transaction: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_transaction[str(row.get("id_mutation"))].append(row)

    kept, n_sales = [], 0
    for group in by_transaction.values():
        if group[0].get("nature_mutation") != "Vente":
            continue
        n_sales += 1
        value = _num(group[0].get("valeur_fonciere"))
        if not value or value <= 0:
            continue
        if COMMERCIAL_PREMISES in {_num(r.get("code_type_local")) for r in group}:
            continue
        dwellings = {
            (r.get("id_parcelle"), int(_num(r.get("code_type_local")) or 0), _num(r.get("surface_reelle_bati")),
             r.get("nombre_pieces_principales"), r.get("lot1_numero"))
            for r in group
            if _num(r.get("code_type_local")) in DWELLING_TYPES
        }
        if len(dwellings) != 1:
            continue
        _, code, area, rooms, _ = next(iter(dwellings))
        if not area or area <= 0:
            continue
        kept.append({"type": DWELLING_TYPES[code], "value": value, "area": area,
                     "price_m2": value / area, "rooms": rooms, "date": group[0].get("date_mutation")})
    return kept, n_sales


def _round(x: float | None, step: int) -> int | None:
    return None if x is None else int(round(x / step) * step)


def statistics_by_type(sales: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for kind in ("house", "apartment"):
        vs = [v for v in sales if v["type"] == kind]
        if not vs:
            out[kind] = {"sales_kept": 0}
            continue
        m2 = sorted(v["price_m2"] for v in vs)
        q = statistics.quantiles(m2, n=4, method="inclusive") if len(m2) >= 2 else [m2[0]] * 3
        s = {
            "sales_kept": len(vs),
            "median_price_eur": _round(statistics.median(v["value"] for v in vs), 1000),
            "median_price_per_m2_eur": _round(q[1], 10),
            "price_per_m2_q1_eur": _round(q[0], 10),
            "price_per_m2_q3_eur": _round(q[2], 10),
            "median_area_m2": round(statistics.median(v["area"] for v in vs)),
        }
        if len(vs) < SMALL_SAMPLE:
            s["warning"] = f"Fewer than {SMALL_SAMPLE} sales: figures are unreliable."
        out[kind] = s
    return out


def property_prices(insee_code: str, period: str | None = None) -> dict[str, Any]:
    code = re.sub(r"\s", "", insee_code or "").upper()
    if not re.fullmatch(r"\d[\dAB]\d{3}", code):
        raise ValueError("Expected a 5-character INSEE municipality code (e.g. 21054). Use find_municipality.")
    if code in ARRONDISSEMENTS:
        city, codes = ARRONDISSEMENTS[code]
        raise ValueError(f"DVF publishes {city} per arrondissement: use one of these codes: {', '.join(codes)}.")
    if department_of(code) in UNCOVERED_DEPARTMENTS:
        raise ValueError("DVF does not cover Alsace, Moselle or Mayotte (departments 57, 67, 68, 976).")

    periods = resources_by_period()
    p = (period or "").strip().upper() or latest_full_year(periods)
    if p not in periods:
        raise ValueError(f"Period not available. Published periods: {', '.join(sorted(periods))}.")
    rid, title = periods[p]
    rows, complete = read_rows(rid, code)
    if not rows:
        raise SourceError(f"No transactions for municipality {code} in period {p}.")
    sales, n_sales = dwelling_sales(rows)
    return {
        "source": SOURCE,
        "resource": title,
        "municipality": rows[0].get("nom_commune"),
        "insee_code": code,
        "period": p,
        "sales_all_property_types": n_sales,
        "statistics": statistics_by_type(sales),
        "complete_data": complete,
        "method": (
            "Sales of a single dwelling (house or apartment, outbuildings allowed, no commercial "
            "premises); price per m2 = property value / built floor area. House prices include "
            "the land. Indicative statistic, not an official index."
        ),
    }
