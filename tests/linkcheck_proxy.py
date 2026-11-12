"""Optional link-check-proxy support for the network tests.

When ``LCP_URL`` is set, results are taken from a link-check-proxy instance
(https://github.com/carreau/link-check-proxy) instead of hitting the
documentation hosts on every run, which gets CI rate limited:

- with credentials, every URL the tests would fetch is sent in one request.
  Credentials are ``LCP_API_KEY`` or, on GitHub Actions with
  ``permissions: id-token: write``, a GitHub OIDC token minted on the fly
  (this repository is on the proxy's allowlist). Push/scheduled runs may add
  new URLs; pull_request runs are read-only on the proxy side. Every URL
  submitted to the proxy becomes public (they all are, here);
- without credentials (e.g. fork PRs, which get neither secrets nor OIDC),
  the public hourly snapshot is downloaded instead: read-only.

The query happens **once per session**, in conftest.py, before collection.
URLs the proxy reports as working (2xx) get no live test at all; everything
else (not checked yet, failing, 4xx, bot challenge, proxy unreachable) still
gets the live check the tests always did. So:

- new registry entries are still checked live on the PR that adds them,
- real breakage is still reported by the live request,
- without ``LCP_URL`` (e.g. local runs), nothing changes.
"""

from __future__ import annotations

import logging
import os
import time
from collections import Counter
from collections.abc import Iterable
from typing import Any

import requests

log = logging.getLogger(__name__)

MAX_URLS_PER_REQUEST = 1000
TIMEOUT = 30  # sec
USER_AGENT = "intersphinx_registry-tests"
OIDC_AUDIENCE = "link-check-proxy"

Results = dict[str, dict[str, Any]]

# Session state, set once by conftest.py via load().
_results: Results = {}
_source = "off (LCP_URL not set)"


def load(results: Results, source: str) -> None:
    global _results, _source
    _results, _source = results, source


def state() -> tuple[Results, str]:
    return _results, _source


def fetch(urls: Iterable[str]) -> tuple[Results, str]:
    """Query the proxy for all URLs. Returns (results, description of source)."""
    base = os.environ.get("LCP_URL", "").rstrip("/")
    if not base:
        return {}, "off (LCP_URL not set)"
    try:
        key = os.environ.get("LCP_API_KEY")
        token = key or _oidc_token()
        if token:
            try:
                res = _from_check(base, token, sorted(set(urls)))
                return res, f"{base} with {'API key' if key else 'GitHub OIDC'}"
            except requests.HTTPError as e:
                source = f"{base} public snapshot (credentials refused: {e})"
                return _from_snapshot(base), source
        return _from_snapshot(base), f"{base} public snapshot (no credentials)"
    except (requests.RequestException, ValueError, KeyError, TypeError) as e:
        # Not a warnings.warn: pytest is configured with filterwarnings=error.
        log.warning("link-check-proxy unavailable, checking URLs live: %s", e)
        return {}, f"unavailable ({e}), all URLs checked live"


def _oidc_token() -> str | None:
    """Mint a GitHub Actions OIDC token, if this job is allowed to."""
    url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL")
    bearer = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    if not (url and bearer):
        return None
    r = requests.get(
        url,
        params={"audience": OIDC_AUDIENCE},
        headers={"Authorization": f"Bearer {bearer}", "User-Agent": USER_AGENT},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    value = r.json()["value"]
    return value if isinstance(value, str) else None


def _from_snapshot(base: str) -> Results:
    """Public read-only snapshot: {url: [status, error, checked_at, ...]}."""
    r = requests.get(
        f"{base}/v1/snapshot.json", headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT
    )
    r.raise_for_status()
    snap = r.json()
    idx = {name: i for i, name in enumerate(snap["fields"])}
    now = time.time()
    out: Results = {}
    for url, row in snap["urls"].items():
        expires = row[idx["expires_at"]]
        out[url] = {
            "state": "fresh" if expires is not None and now < expires else "stale",
            "status": row[idx["status"]],
            "error": row[idx["error"]],
        }
    return out


def _from_check(base: str, token: str, urls: list[str]) -> Results:
    headers = {"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT}
    results: Results = {}
    for i in range(0, len(urls), MAX_URLS_PER_REQUEST):
        r = requests.post(
            f"{base}/v1/check",
            json={"urls": urls[i : i + MAX_URLS_PER_REQUEST]},
            headers=headers,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        results.update(r.json()["results"])
    return results


def known_ok(url: str) -> bool:
    """True if the proxy has a recent successful (2xx) result for ``url``."""
    res = _results.get(url)
    if not res:
        return False
    status = res.get("status")
    return (
        res.get("state") in ("fresh", "stale")
        and res.get("error") is None
        and isinstance(status, int)
        and 200 <= status < 300
    )


def summary(urls: Iterable[str]) -> str:
    """One line for the pytest header: source and how many live checks we skip."""
    wanted = set(urls)
    if not _results:
        return f"link-check-proxy: {_source}"
    ok = sum(known_ok(u) for u in wanted)
    states = Counter(r.get("state") for u, r in _results.items() if u in wanted)
    return (
        f"link-check-proxy: {_source}: {ok}/{len(wanted)} URLs known OK "
        f"(not tested live), states {dict(states)}"
    )
