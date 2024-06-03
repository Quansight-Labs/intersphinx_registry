import sys

from intersphinx_registry import get_intersphinx_mapping
import logging as _logging
from sphinx.ext.intersphinx import inspect_main

if len(sys.argv) != 2:
    sys.exit("Usage: python -m intersphinx_registry.lookup <package>")

packages = set([sys.argv[1]])

# there will be only one url
urls = [
    u[0] + (u[1] if u[1] else "objects.inv")
    for u in get_intersphinx_mapping(packages=packages).values()
]


_logging.basicConfig()
raise SystemExit(inspect_main(urls))
