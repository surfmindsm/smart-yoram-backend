"""
IP 기반 지오로케이션 유틸리티
안전한 위치 정보 조회 기능
"""

import requests
from typing import Optional
import time
import json


def get_location_from_ip(ip_address: Optional[str], timeout: int = 3) -> str:
    """
    IP 주소로부터 위치 정보 조회
    
    Args:
        ip_address: IP 주소 (None이면 "위치 정보 없음" 반환)
        timeout: 요청 타임아웃 (초)
        
    Returns:
        위치 정보 문자열 (예: "대한민국, 서울특별시, 서울")
    """
    if not ip_address or ip_address in ["127.0.0.1", "localhost", "::1"]:
        return "로컬 환경"
    
    try:
        # ip-api.com 무료 서비스 사용 (한글 지원)
        # 제한: 분당 45회 요청
        response = requests.get(
            f"http://ip-api.com/json/{ip_address}",
            params={
                "lang": "ko",  # 한국어 응답
                "fields": "status,country,regionName,city,message"
            },
            timeout=timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                country = data.get('country', '').strip()
                region = data.get('regionName', '').strip()  
                city = data.get('city', '').strip()
                
                # 위치 정보 조합
                location_parts = []
                if country:
                    location_parts.append(country)
                if region and region != country:
                    location_parts.append(region)
                if city and city not in [country, region]:
                    location_parts.append(city)
                
                if location_parts:
                    return ", ".join(location_parts)
                else:
                    return "위치 정보 불명"
            else:
                # API에서 실패 응답
                error_msg = data.get('message', 'Unknown error')
                print(f"⚠️ IP geolocation failed: {error_msg}")
                return "위치 조회 실패"
        else:
            print(f"⚠️ IP geolocation HTTP error: {response.status_code}")
            return "위치 조회 실패"
            
    except requests.exceptions.Timeout:
        print(f"⚠️ IP geolocation timeout for {ip_address}")
        return "위치 조회 시간초과"
    except requests.exceptions.ConnectionError:
        print(f"⚠️ IP geolocation connection error for {ip_address}")
        return "위치 조회 연결실패"
    except Exception as e:
        print(f"⚠️ IP geolocation error for {ip_address}: {str(e)}")
        return "위치 정보 없음"


def get_location_from_ip_with_cache(ip_address: Optional[str]) -> str:
    """
    캐시를 사용한 위치 정보 조회 (향후 Redis 캐시 연동 가능)
    현재는 단순 버전으로 구현
    """
    return get_location_from_ip(ip_address)


# 테스트용 함수
def test_geolocation():
    """지오로케이션 기능 테스트"""
    test_ips = [
        "8.8.8.8",          # Google DNS (미국)
        "1.1.1.1",          # Cloudflare (미국) 
        "208.67.222.222",   # OpenDNS (미국)
        "127.0.0.1",        # 로컬
        None                # None
    ]
    
    print("🌍 IP 지오로케이션 테스트")
    print("=" * 40)
    
    for ip in test_ips:
        location = get_location_from_ip(ip)
        print(f"IP: {ip or 'None':<15} → {location}")
    
    print("=" * 40)
    print("✅ 테스트 완료")


if __name__ == "__main__":
    test_geolocation()