"""HTTP calls to the public APIs (standard library only).

- An explicit User-Agent header is sent, as recommended by the
  Recherche d'entreprises API documentation.
- On HTTP 429, the Retry-After header is honoured once (capped wait), then the
  error is raised.
- On a network failure, the request is retried once after 1 s.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from . import __version__

USER_AGENT = os.environ.get("FR_OPEN_DATA_USER_AGENT", f"french-open-data-mcp/{__version__} (open-source MCP server)")
MAX_WAIT_S = 5.0


class SourceError(RuntimeError):
    """Error returned by a public API (the message is meant for the model and the user)."""


def _retry_after(value: str | None) -> float:
    try:
        return min(max(float(value or 1), 0.0), MAX_WAIT_S)
    except ValueError:
        return 1.0


def request_json(
    url: str,
    params: dict[str, Any] | None = None,
    *,
    method: str = "GET",
    json_body: Any = None,
    form: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    timeout_s: float = 30.0,
    source_name: str = "API",
) -> Any:
    """Send a request and return the decoded JSON. Raises SourceError on failure."""
    if params:
        clean = {k: v for k, v in params.items() if v is not None and v != ""}
        if clean:
            url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(clean, doseq=True)
    h = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        h["Content-Type"] = "application/json"
    elif form is not None:
        data = urllib.parse.urlencode(form).encode("utf-8")
        h["Content-Type"] = "application/x-www-form-urlencoded"
    h.update(headers or {})

    for attempt in (1, 2):
        req = urllib.request.Request(url, data=data, headers=h, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                raw = resp.read()
            return json.loads(raw.decode("utf-8")) if raw else None
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 1:
                time.sleep(_retry_after(e.headers.get("Retry-After")))
                continue
            try:
                detail = e.read().decode("utf-8", errors="replace")[:300]
            except Exception:  # pragma: no cover
                detail = ""
            if e.code == 429:
                raise SourceError(f"{source_name}: too many requests (HTTP 429). Try again later.") from e
            raise SourceError(f"{source_name}: HTTP {e.code}. {detail}".strip()) from e
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            if attempt == 1:
                time.sleep(1.0)
                continue
            raise SourceError(f"{source_name} unreachable: {type(e).__name__}: {e}") from e
        except json.JSONDecodeError as e:
            raise SourceError(f"{source_name}: response is not JSON.") from e
    raise SourceError(f"{source_name}: failed after retry.")  # pragma: no cover
