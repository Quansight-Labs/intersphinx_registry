"""
This package provides convenient utilities and data to write a sphinx config file.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Optional, Tuple, cast

# See issue 4, we this the best format is Major.YYMM.day,
# in case of multiple releases a day we can borrow the next day's date.
# no 0 in front of the day as it is not pep440 compliant.
version_info = (0, 2601, 5)
__version__ = ".".join(map(str, version_info))

registry_file = Path(__file__).parent / "registry.json"

# Mapping of removed aliases to their canonical package names
_ALIASES = {
    "rtd": "readthedocs",
    "server": "jupyter-server",
}


def _get_all_mappings() -> dict[str, tuple[str, str | None]]:
    return cast(
        dict[str, Tuple[str, Optional[str]]],
        {k: tuple(v) for (k, v) in json.loads(registry_file.read_bytes()).items()},
    )


def get_intersphinx_mapping(
    *, packages: set[str] = set()
) -> dict[str, tuple[str, str | None]]:
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
        raise ValueError(
            'You must explicitly give a list of packages for which to download intersphinx inventories: get_intersphinx_mapping(packages=["IPython", "numpy",...]).'
        )

    mapping = _get_all_mappings()

    # Check for aliases and replace them with canonical names
    resolved_packages = set()
    for pkg in packages:
        if pkg in _ALIASES:
            canonical = _ALIASES[pkg]
            warnings.warn(
                f"Package alias '{pkg}' is deprecated. Use '{canonical}' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            resolved_packages.add(canonical)
        else:
            resolved_packages.add(pkg)

    missing = resolved_packages - set(mapping)
    if missing:
        raise ValueError(
            f"Some libraries in 'packages' not found in registry: {repr(sorted(missing))}"
        )
    return {k: v for k, v in mapping.items() if k in resolved_packages}
