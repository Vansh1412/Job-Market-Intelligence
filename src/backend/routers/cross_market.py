"""
JobIntel Cross-Market API Router
================================
REST contracts for USA vs. India labor market comparative intelligence.
Strictly preserves separate currency presentations without FX conversion.
"""

from fastapi import APIRouter, HTTPException
from src.backend.services.market_service import MarketService

router = APIRouter(prefix="/cross-market", tags=["Cross-Market Intelligence"])


@router.get("/summary")
def get_cross_market_summary():
    """Retrieve macro comparative analytics contrasting USA and India tech job markets."""
    try:
        return MarketService.get_cross_market_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
