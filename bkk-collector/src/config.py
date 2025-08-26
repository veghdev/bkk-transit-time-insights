import os
from typing import List

class Config:
    def __init__(self):
        self.POSTGRES_USER: str = self._get_env("POSTGRES_USER", required=True)
        self.POSTGRES_PASSWORD: str = self._get_env("POSTGRES_PASSWORD", required=True)
        self.POSTGRES_DB: str = self._get_env("POSTGRES_DB", required=True)
        self.POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
        self.POSTGRES_PORT: int = self._get_int_env("POSTGRES_PORT", 5432)

        self.TZ: str = os.getenv("TZ", "Europe/Budapest")

        self.BKK_API_KEY: str = self._get_env("BKK_API_KEY", required=True)
        self.BKK_API_URL: str = os.getenv(
            "BKK_API_URL",
            "https://go.bkk.hu/api/query/v1/ws/gtfs-rt/full/TripUpdates.pb"
        )
        self.ROUTE_IDS: List[str] = os.getenv("ROUTE_IDS", "0050,0070,0090").split(",")

    def _get_env(self, key: str, required: bool = False) -> str:
        value = os.getenv(key)
        if required and not value:
            raise ValueError(f"Environment variable {key} is required but not set")
        return value

    def _get_int_env(self, key: str, default: int) -> int:
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            raise ValueError(f"Environment variable {key} must be an integer")
