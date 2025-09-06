import re
from typing import Optional


def parse_user_agent(user_agent: Optional[str]) -> Optional[str]:
    """
    Parse User-Agent string to extract browser and OS information
    Returns a formatted string like "Chrome 120.0.0.0 on Windows 10"
    """
    if not user_agent:
        return None
    
    try:
        user_agent = user_agent.strip()
        
        # Browser detection patterns
        browsers = [
            (r'Chrome/(\d+\.\d+\.\d+\.\d+)', 'Chrome'),
            (r'Firefox/(\d+\.\d+)', 'Firefox'),
            (r'Safari/(\d+\.\d+)', 'Safari'),
            (r'Edge/(\d+\.\d+)', 'Edge'),
            (r'Opera/(\d+\.\d+)', 'Opera'),
        ]
        
        # OS detection patterns
        os_patterns = [
            (r'Windows NT 10\.0', 'Windows 10'),
            (r'Windows NT 6\.3', 'Windows 8.1'),
            (r'Windows NT 6\.2', 'Windows 8'),
            (r'Windows NT 6\.1', 'Windows 7'),
            (r'Mac OS X (\d+[_\.]\d+)', 'macOS'),
            (r'iPhone OS (\d+[_\.]\d+)', 'iOS'),
            (r'Android (\d+\.\d+)', 'Android'),
            (r'Linux', 'Linux'),
        ]
        
        browser_info = None
        os_info = None
        
        # Extract browser info
        for pattern, browser_name in browsers:
            match = re.search(pattern, user_agent)
            if match:
                version = match.group(1)
                browser_info = f"{browser_name} {version}"
                break
        
        # Extract OS info
        for pattern, os_name in os_patterns:
            match = re.search(pattern, user_agent)
            if match:
                if 'macOS' in os_name or 'iOS' in os_name:
                    version = match.group(1).replace('_', '.')
                    os_info = f"{os_name} {version}"
                elif 'Android' in os_name:
                    version = match.group(1)
                    os_info = f"{os_name} {version}"
                else:
                    os_info = os_name
                break
        
        # Fallback browser detection
        if not browser_info:
            if 'Chrome' in user_agent:
                browser_info = 'Chrome'
            elif 'Firefox' in user_agent:
                browser_info = 'Firefox'
            elif 'Safari' in user_agent and 'Chrome' not in user_agent:
                browser_info = 'Safari'
            elif 'Edge' in user_agent:
                browser_info = 'Edge'
            else:
                browser_info = 'Unknown Browser'
        
        # Fallback OS detection
        if not os_info:
            if 'Windows' in user_agent:
                os_info = 'Windows'
            elif 'Macintosh' in user_agent or 'Mac OS' in user_agent:
                os_info = 'macOS'
            elif 'iPhone' in user_agent:
                os_info = 'iOS'
            elif 'Android' in user_agent:
                os_info = 'Android'
            elif 'Linux' in user_agent:
                os_info = 'Linux'
            else:
                os_info = 'Unknown OS'
        
        if browser_info and os_info:
            return f"{browser_info} on {os_info}"
        elif browser_info:
            return browser_info
        elif os_info:
            return os_info
        else:
            return "Unknown Device"
            
    except Exception as e:
        print(f"Error parsing User-Agent: {e}")
        return "Unknown Device"


def get_client_ip(request) -> str:
    """
    Extract client IP address from request headers
    Handles various proxy scenarios
    """
    try:
        # Check for forwarded headers (common with reverse proxies)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip.strip()
        
        # Fallback to client host
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return "Unknown"
        
    except Exception as e:
        print(f"Error extracting client IP: {e}")
        return "Unknown"


def calculate_session_duration(start_time, end_time) -> str:
    """
    Calculate session duration in human-readable format
    """
    if not start_time or not end_time:
        return None
    
    try:
        delta = end_time - start_time
        total_seconds = int(delta.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}시간 {minutes}분"
        elif minutes > 0:
            return f"{minutes}분"
        else:
            return "1분 미만"
            
    except Exception as e:
        print(f"Error calculating session duration: {e}")
        return None