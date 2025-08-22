"""
Geocoding API endpoints
주소를 좌표로 변환하는 API
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api import deps
from app import models
from app.services.geocoding import geocoding_service
from app.core.config import settings

router = APIRouter()


class GeocodeRequest(BaseModel):
    address: str


class GeocodeResponse(BaseModel):
    address: str
    latitude: float
    longitude: float


class BatchGeocodeRequest(BaseModel):
    addresses: List[str]


class BatchGeocodeResponse(BaseModel):
    results: Dict[str, Optional[Dict[str, float]]]


@router.post("/geocode", response_model=GeocodeResponse)
async def geocode_address(
    request: GeocodeRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    단일 주소를 위도/경도 좌표로 변환
    """
    if not request.address:
        raise HTTPException(status_code=400, detail="Address is required")
    
    # Check if Naver Maps API is configured
    if not settings.NAVER_MAPS_CLIENT_ID or not settings.NAVER_MAPS_CLIENT_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Geocoding service is not configured. Please set NAVER_MAPS_CLIENT_ID and NAVER_MAPS_CLIENT_SECRET."
        )
    
    coords = await geocoding_service.get_coordinates(request.address)
    
    if not coords:
        raise HTTPException(
            status_code=404,
            detail=f"Could not geocode address: {request.address}"
        )
    
    latitude, longitude = coords
    return GeocodeResponse(
        address=request.address,
        latitude=latitude,
        longitude=longitude
    )


@router.post("/geocode/batch", response_model=BatchGeocodeResponse)
async def batch_geocode_addresses(
    request: BatchGeocodeRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    여러 주소를 일괄 처리하여 좌표로 변환
    """
    if not request.addresses:
        raise HTTPException(status_code=400, detail="Addresses list is required")
    
    # Check if Naver Maps API is configured
    if not settings.NAVER_MAPS_CLIENT_ID or not settings.NAVER_MAPS_CLIENT_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Geocoding service is not configured. Please set NAVER_MAPS_CLIENT_ID and NAVER_MAPS_CLIENT_SECRET."
        )
    
    results = await geocoding_service.batch_geocode(request.addresses)
    
    # Convert results to proper format
    formatted_results = {}
    for address, coords in results.items():
        if coords:
            formatted_results[address] = {
                "latitude": coords[0],
                "longitude": coords[1]
            }
        else:
            formatted_results[address] = None
    
    return BatchGeocodeResponse(results=formatted_results)