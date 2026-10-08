"""
JobIntel Backend Services Package
=================================
Exposes modular inference and analytics services for USA, India, archetypes, and market statistics.
"""

from src.backend.services.usa_service import USAService
from src.backend.services.india_service import IndiaService
from src.backend.services.archetype_service import ArchetypeService
from src.backend.services.market_service import MarketService

__all__ = [
    "USAService",
    "IndiaService",
    "ArchetypeService",
    "MarketService",
]
