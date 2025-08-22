"""
Naver Maps Geocoding Service
주소를 위도/경도 좌표로 변환하는 서비스
"""

import httpx
from typing import Optional, Dict, Tuple
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class NaverGeocodingService:
    """네이버 Maps Geocoding API를 사용한 주소-좌표 변환 서비스"""

    BASE_URL = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"

    def __init__(self):
        self.client_id = settings.NAVER_MAPS_CLIENT_ID
        self.client_secret = settings.NAVER_MAPS_CLIENT_SECRET

    async def get_coordinates(self, address: str) -> Optional[Tuple[float, float]]:
        """
        주소를 위도/경도 좌표로 변환

        Args:
            address: 변환할 주소 문자열

        Returns:
            (latitude, longitude) 튜플 또는 None
        """
        if not address:
            return None

        headers = {
            "X-NCP-APIGW-API-KEY-ID": self.client_id,
            "X-NCP-APIGW-API-KEY": self.client_secret,
        }

        params = {
            "query": address,
            "coordinate": "127.105399,37.3595704",  # 서울시청 기준점 (검색 정확도 향상)
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.BASE_URL, headers=headers, params=params, timeout=10.0
                )

                if response.status_code != 200:
                    logger.error(f"Geocoding API error: {response.status_code}")
                    return None

                data = response.json()

                # 검색 결과가 있는지 확인
                if data.get("meta", {}).get("totalCount", 0) == 0:
                    logger.warning(f"No geocoding results for address: {address}")
                    return None

                # 첫 번째 결과의 좌표 반환
                first_result = data.get("addresses", [])[0]
                longitude = float(first_result.get("x"))  # 경도
                latitude = float(first_result.get("y"))  # 위도

                logger.info(f"Geocoded '{address}' to ({latitude}, {longitude})")
                return (latitude, longitude)

        except httpx.RequestError as e:
            logger.error(f"Request error during geocoding: {e}")
            return None
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Error parsing geocoding response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during geocoding: {e}")
            return None

    async def batch_geocode(
        self, addresses: list[str]
    ) -> Dict[str, Optional[Tuple[float, float]]]:
        """
        여러 주소를 일괄 처리하여 좌표로 변환

        Args:
            addresses: 주소 문자열 리스트

        Returns:
            {주소: (위도, 경도)} 딕셔너리
        """
        results = {}

        for address in addresses:
            coords = await self.get_coordinates(address)
            results[address] = coords

        return results


# 싱글톤 인스턴스
geocoding_service = NaverGeocodingService()
