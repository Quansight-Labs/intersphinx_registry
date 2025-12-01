"""
Experimental, print info about all (or a subset of), all the known inventories.

As this is likely to make _many_ concurrent connections;
we use aiohttp and sphobjinv which are not listed as dependencies.
"""

import asyncio
import sys
from urllib.parse import urljoin

import aiohttp
from sphobjinv import Inventory  # type: ignore

from intersphinx_registry import get_intersphinx_mapping

if len(sys.argv) not in [2, 3]:
    sys.exit(
        """Usage: python -m intersphinx_registry._info <package>[,package|:all]

        This prints debug info about registered package.

        WARNING: :all: will query _all_ the domains; this can be considered

        """
    )

packages = set(sys.argv[1].split(","))
if packages == {":all:"}:
    from intersphinx_registry import _get_all_mappings

    packages = set(list(_get_all_mappings().keys()))

print("Looking up metadata for", len(packages), "package")

# there will be only one url
urls = [
    (k, u[0], (u[1] if u[1] else "objects.inv"))
    for k, u in get_intersphinx_mapping(packages=packages).items()
]


async def fetch(session, key, base_url, obj):
    final_url = urljoin(base_url, obj)
    if obj != "objects.inv":
        print("Obj for ", base_url, obj)
    async with session.get(final_url) as response:
        return key, base_url, await response.read()


async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, *url) for url in urls]
        return await asyncio.gather(*tasks)


results = asyncio.run(fetch_all(urls))

flattened = []
for key, base_url, data in results:
    try:
        inv = Inventory(zlib=data)
    except Exception:
        print("ERROR with", key, base_url, file=sys.stderr)
        continue
    flattened.append((key, base_url, inv.project, inv.version, inv.count))

if not flattened:
    sys.exit("Could not reach any packages")
width = [len(x) for x in flattened[0][:-1]]

for item in flattened:
    width = [max(w, len(x)) for w, x in zip(width, item[:-1])]


for key, url, proj, version, count in flattened:
    w_key, w_url, w_proj, w_version = width
    print(
        f"{key:<{w_key}}  {proj!r:<{w_proj + 2}} {version:<{w_version}} {count:<5} {url:<{w_url}}"
    )
