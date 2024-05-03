from intersphinx_registry import get_intersphinx_mapping
import pytest
import requests

MAPPING = get_intersphinx_mapping()
keys = MAPPING.keys()


@pytest.mark.parametrize("key", set(keys) - {"jinja"})
def test_format(key: str):
    assert isinstance(key, str)
    for v in MAPPING[key]:
        if v is None:
            continue
        assert v.startswith("https://"), v
        assert v.endswith("/"), v
        assert "readthedocs.org" not in v
        requests.head(v + "objects.inv").raise_for_status()


@pytest.mark.parametrize("key", set(keys))
def test_reach_objects_inv(key: str):
    for v in MAPPING[key]:
        if v is None:
            continue
        requests.head(v + "objects.inv").raise_for_status()
