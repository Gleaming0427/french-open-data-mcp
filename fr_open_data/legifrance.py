"""Légifrance (DILA, French official legal database) via the PISTE platform. Optional module.

Status: NOT TESTED against the live API (no PISTE credentials were available
during development). Only request building and defensive response parsing are
covered by unit tests.

Access: a PISTE account, acceptance of the Légifrance API terms, an application
subscribed to the API, then OAuth "client_credentials" credentials.

Endpoints (environment variables, defaults below):
- LEGIFRANCE_TOKEN_URL: https://oauth.piste.gouv.fr/api/oauth/token
- LEGIFRANCE_API_URL:   https://api.piste.gouv.fr/dila/legifrance/lf-engine-app
These production URLs come from consistent unofficial sources (the pylegifrance
library and third-party projects). The official sources consulted (data.gouv.fr
record and the specification published by api.gouv.fr) only list the sandbox:
https://sandbox-oauth.piste.gouv.fr/api/oauth/token and https://sandbox-api.piste.gouv.fr.
Check them in your PISTE console.

Request format: "DILA - Légifrance" specification published at
github.com/betagouv/api_gouv_swaggers (SearchRequestDTO: fond + recherche
{champs, operateur, pageNumber, pageSize (max 100), sort, typePagination}).
"""

from __future__ import annotations

import html
import os
import re
import threading
import time
from typing import Any

from .http import SourceError, request_json

SOURCE = "Légifrance (DILA), API via PISTE"
COLLECTIONS = ["CODE_DATE", "LODA_DATE", "JURI", "CETAT", "CONSTIT", "JORF", "KALI", "CNIL", "CIRC", "ACCO", "ALL"]
_ARTICLE_ID = re.compile(r"(LEGI|JORF|KALI)ARTI\d{12}")


def token_url() -> str:
    return os.environ.get("LEGIFRANCE_TOKEN_URL") or "https://oauth.piste.gouv.fr/api/oauth/token"


def api_url() -> str:
    return (os.environ.get("LEGIFRANCE_API_URL") or "https://api.piste.gouv.fr/dila/legifrance/lf-engine-app").rstrip("/")


def is_configured() -> bool:
    return bool(os.environ.get("LEGIFRANCE_CLIENT_ID") and os.environ.get("LEGIFRANCE_CLIENT_SECRET"))


class _Token:
    def __init__(self) -> None:
        self._value: str | None = None
        self._expires = 0.0
        self._lock = threading.Lock()

    def get(self) -> str:
        with self._lock:
            if self._value and time.time() < self._expires - 60:
                return self._value
            d = request_json(
                token_url(), method="POST", source_name="PISTE (OAuth token)",
                form={
                    "grant_type": "client_credentials",
                    "client_id": os.environ.get("LEGIFRANCE_CLIENT_ID", ""),
                    "client_secret": os.environ.get("LEGIFRANCE_CLIENT_SECRET", ""),
                    "scope": "openid",
                },
            )
            if not isinstance(d, dict) or not d.get("access_token"):
                raise SourceError("PISTE: no token in the response.")
            self._value = d["access_token"]
            self._expires = time.time() + float(d.get("expires_in") or 3600)
            return self._value


_token = _Token()


def _call(route: str, body: dict[str, Any]) -> Any:
    if not is_configured():
        raise SourceError("Légifrance is not configured: set LEGIFRANCE_CLIENT_ID and LEGIFRANCE_CLIENT_SECRET.")
    return request_json(f"{api_url()}{route}", method="POST", json_body=body, source_name="Légifrance API",
                        headers={"Authorization": f"Bearer {_token.get()}"})


def plain_text(value: Any) -> str:
    """Strip HTML tags (e.g. <mark>) and normalise whitespace."""
    if value is None:
        return ""
    if isinstance(value, list):
        value = " … ".join(str(v) for v in value)
    t = html.unescape(re.sub(r"<[^>]+>", " ", str(value)))
    return re.sub(r"\s+", " ", t).strip()


def _date(v: Any) -> str | None:
    """Légifrance dates are often milliseconds since 1970."""
    if isinstance(v, (int, float)) and v > 0:
        return time.strftime("%Y-%m-%d", time.gmtime(v / 1000))
    return v if isinstance(v, str) else None


def search_body(text: str, collection: str, limit: int) -> dict[str, Any]:
    if collection not in COLLECTIONS:
        raise ValueError(f"Unknown collection. Allowed values: {', '.join(COLLECTIONS)}.")
    if not (text or "").strip():
        raise ValueError("Give words to search for.")
    return {
        "fond": collection,
        "recherche": {
            "champs": [{
                "typeChamp": "ALL",
                "operateur": "ET",
                "criteres": [{"typeRecherche": "TOUS_LES_MOTS_DANS_UN_CHAMP", "valeur": text.strip(), "operateur": "ET"}],
            }],
            "operateur": "ET",
            "pageNumber": 1,
            "pageSize": max(1, min(int(limit), 20)),
            "sort": "PERTINENCE",
            "typePagination": "DEFAUT",
        },
    }


def summarize_results(d: Any) -> list[dict[str, Any]]:
    """Defensive reading of the /search response (structure not guaranteed)."""
    out = []
    for r in (d or {}).get("results") or []:
        titles = r.get("titles") or []
        item: dict[str, Any] = {
            "title": plain_text(titles[0].get("title")) if titles else plain_text(r.get("title")),
            "text_id": (titles[0].get("cid") or titles[0].get("id")) if titles else r.get("id"),
            "nature": r.get("nature"),
            "status": r.get("etat") or (titles[0].get("legalStatus") if titles else None),
        }
        extracts = []
        for s in r.get("sections") or []:
            for e in s.get("extracts") or []:
                extracts.append({"article_id": e.get("id"), "number": e.get("num"),
                                 "extract": plain_text(e.get("values"))[:400]})
        if extracts:
            item["articles"] = extracts[:3]
        out.append(item)
    return out


def search(text: str, collection: str = "CODE_DATE", limit: int = 5) -> dict[str, Any]:
    d = _call("/search", search_body(text, collection, limit))
    return {"source": SOURCE, "collection": collection, "total": (d or {}).get("totalResultNumber"),
            "results": summarize_results(d)}


def read_article(article_id: str) -> dict[str, Any]:
    ident = (article_id or "").strip().upper()
    if not _ARTICLE_ID.fullmatch(ident):
        raise ValueError("Expected a Légifrance article id, e.g. LEGIARTI000006419283.")
    d = _call("/consult/getArticle", {"id": ident})
    a = (d or {}).get("article") or {}
    if not a:
        raise SourceError(f"Article {ident} not found.")
    parents = a.get("textTitles") or []
    return {
        "source": SOURCE,
        "id": a.get("id") or ident,
        "number": a.get("num"),
        "status": a.get("etat"),
        "in_force_from": _date(a.get("dateDebut")),
        "in_force_until": _date(a.get("dateFin")),
        "parent_text": plain_text(parents[0].get("titre") or parents[0].get("title")) if parents else None,
        "content": plain_text(a.get("texte") or a.get("texteHtml"))[:6000],
    }
