import os
import httpx

class ApiClient:
    def __init__(self):
        self.base_url = os.environ.get("API_BASE_URL", "http://api:8000/api/trips")

    async def get_routes(self):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/routes")
            data = resp.json()
            return data

    async def get_route(self, route_id: str):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/find/{route_id}")
            data = resp.json()
            return data
