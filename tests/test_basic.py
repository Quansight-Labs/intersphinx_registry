from intersphinx_registry import _get_all_mappings, get_intersphinx_mapping
import pytest
import requests

MAPPING = _get_all_mappings()
keys = set(MAPPING.keys())


@pytest.mark.parametrize("key", list(sorted(keys - {"jinja"})))
def test_format(key: str):
    assert isinstance(key, str)
    url, obj = MAPPING[key]
    assert url.startswith("https://"), url
    assert url.endswith("/"), url
    assert "readthedocs.org" not in url, "should be readthedocs.io not org"

    if obj is None:
        requests.head(url + "objects.inv", allow_redirects=True).raise_for_status()
    else:
        assert obj.startswith("https://"), obj
        assert obj.endswith("/"), obj
        assert "readthedocs.org" not in obj
        assert obj.startswith(url)
        requests.head(obj, allow_redirects=True).raise_for_status()


@pytest.mark.parametrize("key", list(sorted(keys)))
def test_reach_objects_inv(key: str):
    for v in MAPPING[key]:
        if v is None:
            continue
        requests.head(v + "objects.inv").raise_for_status()


def test_bad():
    with pytest.raises(ValueError, match="Some libraries in"):
        get_intersphinx_mapping(packages={"-nonexistent-"})


@pytest.mark.parametrize('key', sorted(keys))
def test_lower_case(key):
    """
    We agreed that all keys in the mapping should be lower case
    """
    assert key == key.lower(), 'expecting all keys to be lowercase'


