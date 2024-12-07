import sys

from . import get_intersphinx_mapping
from . import __version__
from urllib.parse import urljoin

from typing import Optional

from sphinx.util.inventory import InventoryFile
from io import BytesIO

import requests

if len(sys.argv) not in [2, 3]:
    sys.exit(
        """Usage: python -m intersphinx_registry.lookup <package>[,package] [search_term]

        Example:

        $ python -m intersphinx_registry.lookup numpy,scipy array
        $ python -m intersphinx_registry.lookup ipython formatters.html

        """
    )


def main():
    print(f"Instersphinx-registry version {__version__}")

    packages = set(sys.argv[1].split(","))

    search_term: Optional[str]
    if len(sys.argv) == 3:
        search_term = sys.argv[2]
    else:
        search_term = None

    # there will be only one url
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
            f"{key:<{w_key}}  {entry:<{w_entry}}  {proj:<{w_proj}}  {version:<{w_version}}  {display_name!r:<{w_di+2}}  {url_path}"
        )


if __name__ == "__main__":
    main()
