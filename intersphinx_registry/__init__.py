"""
This package provides convenient utilities and data to write a sphinx config file.
"""
from __future__ import annotations

from pathlib import Path
import json
from typing import Dict, Tuple

__version__ = "0.0.1"

registry_file = Path(__file__).parent / "registry.json"


def get_intersphinx_mapping() -> Dict[str, Tuple[str, str]]:
    """
    Return values of intersphinx_mapping for sphinx configuration.

    For conveneience, the return dict is a copy so should be ok to mutate
    """
    return {k: tuple(v) for (k, v) in json.loads(registry_file.read_bytes()).items()}
