import json
import sys
from io import BytesIO
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse
from datetime import timedelta
import requests
import requests_cache
from sphinx.util.inventory import InventoryFile

from . import get_intersphinx_mapping


def reverse_lookup(urls: list[str]):
    """
    Reverse lookup: given URLs, find which packages they belong to and their rst references.

    Parameters
    ----------
    urls : list[str]
        List of URLs
    """
    if not urls:
        print("ERROR: No URLs provided")
        return

    if not _are_dependencies_available():
        return

    requests_cache.install_cache(
        "intersphinx_cache",
        backend="filesystem",
        expire_after=timedelta(hours=6),
        use_cache_dir=True,
        stale_if_error=True,
        cache_control=True,
    )

    registry_file = Path(__file__).parent / "registry.json"
    registry = json.loads(registry_file.read_bytes())

    results = []

    for url_str in urls:
        matching_packages = []
        base_str = url_str
        if url_str.endswith("/index.html"):
            url_str_index = url_str
            url_str = url_str[:-10]  # remove index.html, keep /
        elif url_str.endswith("/"):
            url_str_index = url_str + "index.html"
        else:
            url_str_index = None

        for package, (base_url, obj_path) in registry.items():
            if url_str.startswith(base_url):
                matching_packages.append((package, base_url, obj_path))

        if matching_packages:
            matching_packages.sort(key=lambda x: -len(x[1]))
            for package, base_url, obj_path in matching_packages:
                inv_url = urljoin(base_url, obj_path if obj_path else "objects.inv")

                resp = requests.get(inv_url)
                cache_hit = getattr(resp, "from_cache", False)
                inv = InventoryFile.load(BytesIO(resp.content), base_url, urljoin)

                found = False

                for key, v in inv.items():
                    for entry, item in v.items():
                        if item.uri in (url_str, url_str_index):
                            results.append(
                                (
                                    base_str,
                                    package,
                                    key,
                                    entry,
                                    item.display_name,
                                    cache_hit,
                                )
                            )
                            found = True
                            break
                    if found:
                        break

                if not found:
                    results.append((url_str, package, None, None, None, cache_hit))

        # else:
        #   results.append((url_str, None, None, None, None, False))

    width_url = max(len(r[0]) for r in results) if results else 0
    width_rst = (
        max((len(f":{r[1]}:`{r[3]}`") if r[3] else 7) for r in results)
        if results
        else 0
    )
    width_display = max((len(r[4]) if r[4] else 0) for r in results) if results else 0

    for url_str, package, key, entry, display_name, cache_hit in results:
        cache_status = "(cache hit)" if cache_hit else ""
        if entry:
            rst_ref = f":{package}:`{entry}`"
            display = display_name if display_name and display_name != "-" else entry
            print(
                f"{url_str:<{width_url}}|  {rst_ref:<{width_rst}}  {display:<{width_display}}  {cache_status}"
            )
        elif package:
            print(f"{url_str:<{width_url}}|  NOT FOUND IN INVENTORY  {cache_status}")
        # else:
        #    print(f"{url_str:<{width_url}}|  PACKAGE NOT FOUND")


def clear_cache() -> None:
    """Clear the intersphinx inventory cache."""
    if not _are_dependencies_available():
        return

    import requests_cache

    cache = requests_cache.CachedSession(
        'intersphinx_cache',
        backend='filesystem',
        use_cache_dir=True,
    )
    cache.cache.clear()
    print("Cache cleared successfully")


def _are_dependencies_available() -> bool:
    """
    Check if CLI dependencies are missing or not.
    Returns True if all dependencies are available, False otherwise.
    """
    missing = []
    try:
        import sphinx  # noqa: F401
    except ModuleNotFoundError:
        missing.append("sphinx")

    try:
        import requests  # noqa: F401
    except ModuleNotFoundError:
        missing.append("requests")

    try:
        import requests_cache  # noqa: F401
    except ModuleNotFoundError:
        missing.append("requests-cache")

    if missing:
        print(
            "ERROR: the lookup functionality requires additional dependencies.",
            file=sys.stderr,
        )
        print(
            "Please install with: pip install 'intersphinx_registry[cli]'",
            file=sys.stderr,
        )
        print(f"Missing dependencies: {', '.join(missing)}", file=sys.stderr)
        return False

    return True


def lookup_packages(packages_str: str, search_term: Optional[str] = None):
    """
    Look up intersphinx targets for specified packages.

    Parameters
    ----------
    packages_str : str
        Comma-separated list of package names
    search_term : str, optional
        Search term to filter results
    """
    if not _are_dependencies_available():
        return

    from sphinx.util.inventory import InventoryFile
    import requests
    import requests_cache

    packages = set(packages_str.split(","))

    requests_cache.install_cache(
        'intersphinx_cache',
        backend='filesystem',
        expire_after=timedelta(hours=6),
        use_cache_dir=True,
        stale_if_error=True,
        cache_control=True,
    )

    urls = [
        (u[0], (u[1] if u[1] else "objects.inv"))
        for u in get_intersphinx_mapping(packages=packages).values()
    ]

    flattened = []
    for base_url, obj in urls:
        final_url = urljoin(base_url, obj)

        resp = requests.get(final_url)

        inv = InventoryFile.load(BytesIO(resp.content), base_url, urljoin)

        for key, v in inv.items():
            inv_entries = sorted(v.items())
            for entry, (_proj, _ver, url_path, display_name) in inv_entries:
                # display_name = display_name * (display_name != '-')
                flattened.append((key, entry, _proj, _ver, display_name, url_path))

    filtered = []

    width = [len(x) for x in flattened[0]]

    for item in flattened:
        key, entry, proj, version, display_name, url_path = item
        if (
            (search_term is None)
            or (search_term in entry)
            or (search_term in display_name)
            or (search_term in url_path)
        ):
            filtered.append((key, entry, proj, version, display_name, url_path))
            width = [max(w, len(x)) for w, x in zip(width, item)]

    for key, entry, proj, version, display_name, url_path in filtered:
        w_key, w_entry, w_proj, w_version, w_di, w_url = width
        print(
            f"{key:<{w_key}}  {entry:<{w_entry}}  {proj:<{w_proj}}  "
            f"{version:<{w_version}}  {display_name!r:<{w_di + 2}}  {url_path}"
        )


if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        sys.exit(
            """Usage: python -m intersphinx_registry.lookup <package>[,package] [search_term]

        Example:

        $ python -m intersphinx_registry.lookup numpy,scipy array
        $ python -m intersphinx_registry.lookup ipython formatters.html

        """
        )

    packages_str = sys.argv[1]
    search_term = sys.argv[2] if len(sys.argv) == 3 else None

    try:
        lookup_packages(packages_str, search_term)
    except Exception as e:
        sys.exit(f"ERROR: {e}")
