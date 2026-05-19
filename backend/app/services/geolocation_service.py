import httpx
from typing import Optional

class GeolocationService:
    def __init__(self):
        self.api_url = "http://ip-api.com/json/"
    
    async def get_location_from_ip(self, ip: str) -> Optional[dict]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}{ip}?fields=status,zip", timeout=5.0)
                data = response.json()
                if data.get('status') == 'success':
                    return {'pincode': data.get('zip', '')}
                return None
        except Exception as e:
            print(f"Geolocation error: {e}")
            return None
    
    def get_client_ip(self, request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host
