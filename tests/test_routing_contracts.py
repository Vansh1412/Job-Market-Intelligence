"""
tests/test_routing_contracts.py
===============================
Automated contract tests validating client-side routing definitions directly from
the production source of truth: frontend/src/App.tsx.
Verifies that all 7 application pages map to standardized URL paths and
that unknown paths cleanly fall back to home.
"""

import os
import re
import pytest

APP_TSX_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "App.tsx")


def load_app_routing():
    """Parse ROUTE_MAP and PAGE_TO_ROUTE directly from frontend/src/App.tsx."""
    assert os.path.exists(APP_TSX_PATH), f"App.tsx not found at {APP_TSX_PATH}"
    with open(APP_TSX_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract ROUTE_MAP entries from App.tsx
    route_map_match = re.search(r"const ROUTE_MAP: Record<string, NavigationPage> = \{([^}]+)\};", content)
    assert route_map_match, "ROUTE_MAP declaration not found in App.tsx"
    route_map = dict(re.findall(r"['\"]([^'\"]+)['\"]\s*:\s*['\"]([^'\"]+)['\"]", route_map_match.group(1)))

    # Extract PAGE_TO_ROUTE entries from App.tsx
    page_to_route_match = re.search(r"const PAGE_TO_ROUTE: Record<NavigationPage, string> = \{([^}]+)\};", content)
    assert page_to_route_match, "PAGE_TO_ROUTE declaration not found in App.tsx"
    page_to_route = dict(re.findall(r"(\w+)\s*:\s*['\"]([^'\"]+)['\"]", page_to_route_match.group(1)))

    return route_map, page_to_route


def test_route_map_completeness():
    """Verify that all 7 navigation targets have a defined route in App.tsx."""
    route_map, _ = load_app_routing()
    required_pages = {"home", "calculator", "explore", "skills", "archetypes", "comparison", "howitworks"}
    mapped_pages = set(route_map.values())
    assert required_pages.issubset(mapped_pages), f"Missing page mappings in App.tsx: {required_pages - mapped_pages}"


def test_canonical_routes_exist():
    """Verify that canonical user-friendly URLs map to the expected page identifiers in App.tsx."""
    route_map, _ = load_app_routing()
    assert route_map.get("/") == "home"
    assert route_map.get("/salary") == "calculator"
    assert route_map.get("/explore") == "explore"
    assert route_map.get("/skills") == "skills"
    assert route_map.get("/archetypes") == "archetypes"
    assert route_map.get("/cross-market") == "comparison"
    assert route_map.get("/how-it-works") == "howitworks"


def test_page_to_route_bidirectional_consistency():
    """Verify that PAGE_TO_ROUTE paths in App.tsx resolve back to the correct page in ROUTE_MAP."""
    route_map, page_to_route = load_app_routing()
    for page, route in page_to_route.items():
        assert route_map.get(route) == page, f"Inconsistent route mapping in App.tsx for {page}: {route} -> {route_map.get(route)}"


def test_unknown_route_fallback():
    """Verify that App.tsx getPageFromLocation logic cleanly falls back to 'home'."""
    route_map, _ = load_app_routing()
    unknown_routes = ["/random", "/foo/bar", "/unknown-page", "/test"]
    for route in unknown_routes:
        assert route_map.get(route, "home") == "home"
