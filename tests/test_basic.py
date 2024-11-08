from intersphinx_registry import _get_all_mappings, get_intersphinx_mapping
from urllib.parse import urljoin
import pytest
import requests

MAPPING = _get_all_mappings()
keys = set(MAPPING)

TIMEOUT = 5  # sec

# click does return a 301 instead of a 30
CLICK_WRONG_301 = 301


@pytest.mark.parametrize("key", sorted(keys - {"jinja"}))
def test_format(key: str):
    assert isinstance(key, str)
    url, obj = MAPPING[key]
    assert url.startswith("https://"), url
    assert "readthedocs.org" not in url, "should be readthedocs.io not org"

    if obj is None:
        requests.head(urljoin(url, "objects.inv"), allow_redirects=True).raise_for_status()
    else:
        assert obj.startswith("https://"), obj
        assert "readthedocs.org" not in obj
        assert obj.startswith(url)
        res = requests.head(obj, allow_redirects=True, timeout=TIMEOUT)
        res.raise_for_status()
        assert res.status_code in (200, 302, CLICK_WRONG_301)


@pytest.mark.parametrize("key", sorted(keys))
def test_url_end_in_slash(key: str):
    url, obj = MAPPING[key]
    assert url.endswith('/'), 'base url should generally ends with / (you can request an exception)'


@pytest.mark.parametrize("key", list(sorted(keys)))
def test_reach_objects_inv(key: str):
    for v in MAPPING[key]:
        if v is None:
            continue
        res = requests.head(urljoin(v, "objects.inv"), timeout=TIMEOUT)
        res.raise_for_status()
        assert res.status_code in (200, 302, CLICK_WRONG_301)


def test_bad():
    with pytest.raises(ValueError, match="Some libraries in"):
        get_intersphinx_mapping(packages={"-nonexistent-"})


@pytest.mark.parametrize("key", sorted(keys))
def test_lower_case(key):
    """
    We agreed that all keys in the mapping should be lower case
    """
    assert key == key.lower(), "expecting all keys to be lowercase"
