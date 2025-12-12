import json
import re
import sys
import warnings
from collections import namedtuple
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from sphinx.util.inventory import InventoryFile

from .utils import _are_dependencies_available, _install_cache

ReverseLookupResult = namedtuple(
    "ReverseLookupResult",
    ["url", "package", "domain", "rst_entry", "display_name", "inventory_url"],
)


def _normalize_url_for_matching(url: str) -> str:
    """
    Normalize URL for fuzzy matching by removing version-specific segments.

    This helps match URLs like:
    - /stable/ vs /latest/ vs /main/
    - /v1.2.3/ vs /v2.0/ vs /1.5/
    """
    normalized = re.sub(r"/(latest|stable|main|dev|master)/", "/_VERSION_/", url)
    normalized = re.sub(r"/v?\d+(\.\d+)*/", "/_VERSION_/", normalized)
    return normalized


def uri_match(user_url: str, inv_url: str) -> bool:
    """
    Check if two URIs match, handling index.html variations and version normalization.

    Parameters
    ----------
    user_url : str
        URL from user input or RST file
    inv_url : str
        URL from intersphinx inventory

    Returns
    -------
    bool
        True if the URLs match (considering index.html and version variations), False otherwise
    """
    if user_url == inv_url:
        return True

    variants = [user_url]
    if user_url.endswith("/index.html"):
        variants.append(user_url[:-10])  # Remove index.html, keep /
    elif user_url.endswith("/"):
        variants.append(user_url + "index.html")
    else:
        variants.append(user_url + "/index.html")

    if inv_url in variants:
        return True

    inv_url_normalized = (
        _normalize_url_for_matching(inv_url).rstrip("/").replace("/index.html", "")
    )
    for variant in variants:
        variant_normalized = (
            _normalize_url_for_matching(variant).rstrip("/").replace("/index.html", "")
        )
        if variant_normalized == inv_url_normalized:
            return True

    return False


def _do_reverse_lookup(
    urls: list[str],
) -> list[ReverseLookupResult]:
    """
    Core reverse lookup logic: given URLs, find which packages they belong to and their rst references.

    Parameters
    ----------
    urls : list[str]
        List of URLs

    Returns
    -------
    list[ReverseLookupResult]
        List of ReverseLookupResult named tuples with fields:
        url, package, domain, rst_entry, display_name
    """
    _install_cache()

    registry_file = Path(__file__).parent / "registry.json"
    registry = json.loads(registry_file.read_bytes())

    package_urls: dict[str, list[str]] = {}

    for url_str in urls:
        matched = False
        for package, (base_url, obj_path) in registry.items():
            if url_str.startswith(base_url):
                package_urls.setdefault(package, []).append(url_str)
                matched = True
                break

        if not matched:
            url_domain = urlparse(url_str).netloc
            url_path_normalized = (
                _normalize_url_for_matching(urlparse(url_str).path)
                .rstrip("/")
                .replace("/index.html", "")
            )

            for package, (base_url, obj_path) in registry.items():
                base_domain = urlparse(base_url).netloc
                if url_domain == base_domain:
                    base_path_normalized = _normalize_url_for_matching(
                        urlparse(base_url).path
                    ).rstrip("/")
                    if url_path_normalized.startswith(
                        base_path_normalized
                    ) or base_path_normalized.startswith(url_path_normalized):
                        package_urls.setdefault(package, []).append(url_str)
                        break

    results: list[ReverseLookupResult] = []

    for package, url_list in package_urls.items():
        base_url, obj_path = registry[package]
        inv_url = urljoin(base_url, obj_path if obj_path else "objects.inv")

        try:
            resp = requests.get(inv_url, timeout=25)
            resp.raise_for_status()
            inv = InventoryFile.load(BytesIO(resp.content), base_url, urljoin)
        except Exception as e:
            warnings.warn(
                f"Failed to load inventory for '{package}' from {inv_url}: {e}",
                UserWarning,
                stacklevel=2,
            )
            for url_str in url_list:
                results.append(
                    ReverseLookupResult(url_str, package, None, None, None, None)
                )
            continue

        inv_urls = {}
        for key, v in inv.items():
            for entry, (proj, ver, uri, display_name) in v.items():
                inv_urls[uri] = (key, entry, display_name)

        for url_str in url_list:
            found = False

            for inv_uri, (key, entry, display_name) in inv_urls.items():
                if uri_match(url_str, inv_uri):
                    results.append(
                        ReverseLookupResult(
                            url_str, package, key, entry, display_name, inv_uri
                        )
                    )
                    found = True
                    break

            if not found:
                results.append(
                    ReverseLookupResult(url_str, package, None, None, None, None)
                )

    return results


def _print_reverse_lookup_results(
    results: list[ReverseLookupResult],
) -> None:
    """
    Print formatted reverse lookup results.

    Parameters
    ----------
    results : list[ReverseLookupResult]
        List of ReverseLookupResult named tuples
    """
    if not results:
        return

    header_url = "URL"
    header_rst = "Sphinx Reference"
    header_display = "Description"

    width_url = max(len(header_url), max(len(r.url) for r in results))
    width_rst = max(
        len(header_rst),
        max(
            (
                len(f":{r.domain}:`{r.package}:{r.rst_entry}`")
                if r.rst_entry
                else len("NOT FOUND")
            )
            for r in results
        ),
    )
    width_display = max(
        len(header_display),
        max((len(r.display_name) if r.display_name else 0) for r in results),
    )

    print(f"{header_url:<{width_url}}  {header_rst:<{width_rst}}  {header_display}")
    print(f"{'-' * width_url}  {'-' * width_rst}  {'-' * width_display}")

    for result in results:
        if result.rst_entry:
            rst_ref = f":{result.domain}:`{result.package}:{result.rst_entry}`"
            display = (
                result.display_name
                if result.display_name and result.display_name != "-"
                else result.rst_entry
            )
            print(
                f"{result.url:<{width_url}}  {rst_ref:<{width_rst}}  {display:<{width_display}}"
            )
        elif result.package:
            print(f"{result.url:<{width_url}}  {'NOT FOUND':<{width_rst}}")


def reverse_lookup(urls: list[str]) -> None:
    """
    Reverse lookup: given URLs, find which packages they belong to and their rst references.

    Parameters
    ----------
    urls : list[str]
        List of URLs
    """
    if not urls:
        print("ERROR: No URLs provided", file=sys.stderr)
        return

    if not _are_dependencies_available():
        return

    results = _do_reverse_lookup(urls)
    _print_reverse_lookup_results(results)
