import json
import shutil
import sys
from io import BytesIO
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests
from sphinx.util.inventory import InventoryFile

from . import __version__, get_intersphinx_mapping
from .utils import (
    _are_dependencies_available,
    _compress_user_path,
    _get_cache_dir,
    _install_cache,
)


def clear_cache() -> None:
    """Clear the intersphinx inventory cache for the current version."""
    if not _are_dependencies_available():
        return

    cache_dir = _get_cache_dir()

    if cache_dir.exists():
        for item in cache_dir.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception as e:
                print(f"Warning: Could not remove {item}: {e}")

    print("Cache cleared successfully")


def get_info() -> dict[str, str]:
    """
    Get information about the intersphinx-registry installation.

    Returns
    -------
    dict[str, str]
        Dictionary containing version and cache location
    """
    info = {
        "version": __version__,
    }

    try:
        cache_dir = _get_cache_dir()
        info["cache_location"] = str(cache_dir)
    except Exception:
        info["cache_location"] = "N/A (dependencies not installed)"

    return info


def print_info() -> None:
    """Print information about the intersphinx-registry installation."""
    info = get_info()

    cache_location = _compress_user_path(info["cache_location"])

    print("Intersphinx Registry Information")
    print("=" * 50)
    print(f"Version:               {info['version']}")
    print(f"Cache location:        {cache_location}")

    try:
        registry_file_path = Path(__file__).parent / "registry.json"
        registry = json.loads(registry_file_path.read_bytes())
        print(f"Packages in registry:  {len(registry)}")
    except Exception as e:
        print(f"Packages in registry:  Error reading registry ({e})")


def lookup_packages(packages_str: str, search_term: Optional[str] = None) -> None:
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

    packages = set(packages_str.split(","))

    _install_cache()

    urls = [
        (u[0], (u[1] if u[1] else "objects.inv"))
        for u in get_intersphinx_mapping(packages=packages).values()
    ]

    flattened: list[tuple[str, str, str, str, str, str]] = []
    for base_url, obj in urls:
        final_url = urljoin(base_url, obj)

        try:
            resp = requests.get(final_url, timeout=30)
            resp.raise_for_status()
            inv = InventoryFile.load(BytesIO(resp.content), base_url, urljoin)
        except requests.RequestException as e:
            print(f"Warning: Failed to fetch {final_url}: {e}", file=sys.stderr)
            continue
        except Exception as e:
            print(
                f"Warning: Failed to load inventory from {final_url}: {e}",
                file=sys.stderr,
            )
            continue

        for key, v in inv.items():
            inv_entries = sorted(v.items())
            for entry, item in inv_entries:
                flattened.append(
                    (
                        key,
                        entry,
                        item.project_name,
                        item.project_version,
                        item.display_name,
                        item.uri,
                    )
                )

    filtered: list[tuple[str, str, str, str, str, str]] = []
    for item_tuple in flattened:
        key, entry, proj, version, display_name, url_path = item_tuple
        if (
            (search_term is None)
            or (search_term in entry)
            or (search_term in display_name)
            or (search_term in url_path)
        ):
            filtered.append((key, entry, proj, version, display_name, url_path))

    if not filtered:
        return

    width = [0] * 6
    for item_tuple in filtered:
        for i, x in enumerate(item_tuple):
            width[i] = max(width[i], len(str(x)))

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
