"""
This package provides convenient utilities and data to write a sphinx config file.
"""

from __future__ import annotations

from pathlib import Path
import json
from typing import Dict, Tuple, Set, Optional, cast

# I'm thinking of going YEAR.month.releasenumber

__version__ = "0.0.4"

registry_file = Path(__file__).parent / "registry.json"

def _get_all_mappings() ->  Dict[str, Tuple[str, Optional[str]]]:
    return cast(
        Dict[str, Tuple[str, Optional[str]]],
        {k: tuple(v) for (k, v) in json.loads(registry_file.read_bytes()).items()},
    )


def get_intersphinx_mapping(
    *, packages: Set[str] = set()
) -> Dict[str, Tuple[str, Optional[str]]]:
    """
    Return values of intersphinx_mapping for sphinx configuration.

    For convenience, the returned dictionary is a copy so should be ok to
    mutate.

    Parameters
    ----------
    packages: Set of Str
        Libraries to include.

        Sphinx will download and load all the `objects.inv` for listed 
        packages. Getting all mappings is discourage as it will download all
        the `object.inv` which can be a non-negligible amount of data.

    """
    if len(packages) == 0:
        raise ValueError('You now must explicitly give a list of package to download inter sphinx from: get_intersphinx_mapping(["IPython", "numpy",...]).')

    mapping = _get_all_mappings()
    missing = set(packages) - set(mapping)
    if missing:
        raise ValueError(f"Missing libraries in 'packages': {repr(sorted(missing))}")
    return {k: v for k, v in mapping.items() if k in packages}
