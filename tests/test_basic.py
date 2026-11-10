import warnings

import pytest
import requests
from linkcheck_proxy import known_ok
from registry_urls import MAPPING, format_target, inv_targets

from intersphinx_registry import _ALIASES, get_intersphinx_mapping

keys = set(MAPPING)

TIMEOUT = 5  # sec

# click does return a 301 instead of a 30
CLICK_WRONG_301 = 301

FORMAT_KEYS = sorted(keys - {"jinja", "scipy"})

# Network tests are only generated for URLs that link-check-proxy does not
# already report as working (see linkcheck_proxy.py / conftest.py). Without
# LCP_URL, that is all of them.
FORMAT_LIVE = [k for k in FORMAT_KEYS if not known_ok(format_target(k))]
INV_LIVE = [k for k in sorted(keys) if not all(map(known_ok, inv_targets(k)))]


@pytest.mark.parametrize("key", FORMAT_KEYS)
def test_format(key: str):
    url, obj = MAPPING[key]
    assert url.startswith("https://"), url
    assert "readthedocs.org" not in url, "should be readthedocs.io not org"
    if obj is not None:
        assert obj.startswith("https://"), obj
        assert "readthedocs.org" not in obj
        assert obj.startswith(url)


@pytest.mark.parametrize("key", FORMAT_LIVE)
def test_format_reachable(key: str):
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=1)
    session.mount("https://", adapter)
    url, obj = MAPPING[key]
    if obj is None:
        session.head(format_target(key), allow_redirects=True).raise_for_status()
    else:
        res = session.head(obj, allow_redirects=True, timeout=TIMEOUT)
        res.raise_for_status()
        assert res.status_code in (200, 302, CLICK_WRONG_301)


@pytest.mark.parametrize("key", sorted(keys))
def test_url_end_in_slash(key: str):
    url, obj = MAPPING[key]
    assert url.endswith("/"), (
        "base url should generally ends with / (you can request an exception)"
    )


@pytest.mark.parametrize("key", INV_LIVE)
def test_reach_objects_inv(key: str):
    for target in inv_targets(key):
        if known_ok(target):
            continue
        res = requests.head(target, timeout=TIMEOUT)
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


def test_unique_base_urls():
    """
    Two packages should not have the same base URL.
    This is important for reverse lookup functionality to work correctly.
    """
    DUPLICATE_EXCLUSION = {"pyqt", "pyqt5"}
    base_urls = {}
    for package, (base_url, _obj) in MAPPING.items():
        if base_url in base_urls:
            if package not in DUPLICATE_EXCLUSION:
                pytest.fail(
                    f"Duplicate base URL found: {base_url}\n"
                    f"  Used by packages: {base_urls[base_url]} and {package}"
                )
        base_urls[base_url] = package


@pytest.mark.parametrize("alias,canonical", list(_ALIASES.items()))
def test_alias_warning(alias, canonical):
    """
    Test that using an alias emits a deprecation warning and resolves to the canonical package.
    """
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = get_intersphinx_mapping(packages={alias})

        # Check that a warning was raised
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert alias in str(w[0].message)
        assert canonical in str(w[0].message)

        # Check that the canonical package is returned
        assert canonical in result
        assert alias not in result


def test_alias_not_in_registry():
    """
    Test that aliases are not present in the registry itself.
    """
    for alias in _ALIASES:
        assert alias not in MAPPING, f"Alias '{alias}' should not be in the registry"


def test_canonical_packages_exist():
    """
    Test that all canonical packages referenced by aliases exist in the registry.
    """
    for alias, canonical in _ALIASES.items():
        assert canonical in MAPPING, (
            f"Canonical package '{canonical}' for alias '{alias}' not found in registry"
        )
