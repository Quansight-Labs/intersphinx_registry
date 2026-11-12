"""The URLs the network tests fetch, without importing any test module."""

from urllib.parse import urljoin

from intersphinx_registry import _get_all_mappings

MAPPING = _get_all_mappings()


def format_target(key: str) -> str:
    """URL test_format_reachable fetches: the inventory, or base/objects.inv."""
    url, obj = MAPPING[key]
    return obj if obj is not None else urljoin(url, "objects.inv")


def inv_targets(key: str) -> list[str]:
    """URLs test_reach_objects_inv fetches: <each non-None value>/objects.inv."""
    return [urljoin(v, "objects.inv") for v in MAPPING[key] if v is not None]


NETWORK_URLS = {format_target(k) for k in MAPPING} | {
    t for k in MAPPING for t in inv_targets(k)
}
