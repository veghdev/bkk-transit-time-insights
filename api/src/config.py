import os

class Config:
    def __init__(self):
        self.POSTGRES_USER: str = self._get_env("POSTGRES_USER", required=True)
        self.POSTGRES_PASSWORD: str = self._get_env("POSTGRES_PASSWORD", required=True)
        self.POSTGRES_DB: str = self._get_env("POSTGRES_DB", required=True)
        self.POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
        self.POSTGRES_PORT: int = self._get_int_env("POSTGRES_PORT", 5432)

        self.TZ: str = os.getenv("TZ", "Europe/Budapest")

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
