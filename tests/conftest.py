"""Query link-check-proxy once per session, before tests are collected.

test_basic.py only generates live network tests for URLs the proxy does not
already report as working, so the query must happen here, before collection.

xdist is not used by default anymore, but `pytest -n N` still works: the main
process does the single proxy request and passes the result to the workers,
so they all collect the same tests (xdist requires that).
"""

import json

import linkcheck_proxy
import pytest
from registry_urls import NETWORK_URLS

_KEY = "link_check_proxy"


def pytest_configure(config):
    workerinput = getattr(config, "workerinput", None)
    if workerinput is not None:  # xdist worker: use the controller's result
        results, source = json.loads(workerinput[_KEY])
    else:  # main process (with or without xdist): the one request
        results, source = linkcheck_proxy.fetch(NETWORK_URLS)
    linkcheck_proxy.load(results, source)


@pytest.hookimpl(optionalhook=True)  # only exists when pytest-xdist is installed
def pytest_configure_node(node):
    node.workerinput[_KEY] = json.dumps(linkcheck_proxy.state())


def pytest_report_header(config):
    return linkcheck_proxy.summary(NETWORK_URLS)
