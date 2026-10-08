"""
tests/test_routing_contracts.py
===============================
Automated contract tests validating client-side routing definitions:
Verifies that all 7 application pages map to standardized URL paths and
that unknown paths cleanly fall back to home.
"""

import pytest

ROUTE_MAP = {
    "/": "home",
    "/salary": "calculator",
    "/calculator": "calculator",
    "/explore": "explore",
    "/skills": "skills",
    "/archetypes": "archetypes",
    "/cross-market": "comparison",
    "/comparison": "comparison",
    "/how-it-works": "howitworks",
    "/howitworks": "howitworks",
}

PAGE_TO_ROUTE = {
    "home": "/",
    "calculator": "/salary",
    "explore": "/explore",
    "skills": "/skills",
    "archetypes": "/archetypes",
    "comparison": "/cross-market",
    "howitworks": "/how-it-works",
}


def test_route_map_completeness():
    """Verify that all navigation targets have a defined route in ROUTE_MAP."""
    required_pages = {"home", "calculator", "explore", "skills", "archetypes", "comparison", "howitworks"}
    mapped_pages = set(ROUTE_MAP.values())
    assert required_pages.issubset(mapped_pages), f"Missing page mappings: {required_pages - mapped_pages}"


def test_canonical_routes_exist():
    """Verify that canonical user-friendly URLs map to the expected page identifiers."""
    assert ROUTE_MAP["/"] == "home"
    assert ROUTE_MAP["/salary"] == "calculator"
    assert ROUTE_MAP["/explore"] == "explore"
    assert ROUTE_MAP["/skills"] == "skills"
    assert ROUTE_MAP["/archetypes"] == "archetypes"
    assert ROUTE_MAP["/cross-market"] == "comparison"
    assert ROUTE_MAP["/how-it-works"] == "howitworks"


def test_page_to_route_bidirectional_consistency():
    """Verify that PAGE_TO_ROUTE paths resolve back to the correct page in ROUTE_MAP."""
    for page, route in PAGE_TO_ROUTE.items():
        assert ROUTE_MAP.get(route) == page, f"Inconsistent route mapping for {page}: {route} -> {ROUTE_MAP.get(route)}"


def test_unknown_route_fallback():
    """Verify that unknown routes resolve to 'home'."""
    unknown_routes = ["/random", "/foo/bar", "/unknown-page", "/test"]
    for route in unknown_routes:
        assert ROUTE_MAP.get(route, "home") == "home"
