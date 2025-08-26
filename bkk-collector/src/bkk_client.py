import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple
import requests
from google.transit import gtfs_realtime_pb2
from config import Config

logger = logging.getLogger(__name__)

class BkkApiError(Exception):
    pass

class BkkClient:
    def __init__(self, config: Config):
        self.api_url = config.BKK_API_URL
        self.api_key = config.BKK_API_KEY

    def _epoch_to_dt(self, ts: Optional[int]) -> Optional[datetime]:
        if ts is None:
            return None
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    def _extract_first_last_times(self, stop_time_updates: List[gtfs_realtime_pb2.TripUpdate.StopTimeUpdate]) -> Tuple[Optional[datetime], Optional[datetime]]:
        if not stop_time_updates:
            return None, None
        first = stop_time_updates[0]
        last = stop_time_updates[-1]

        start_ts = getattr(first.departure if first.HasField("departure") else first.arrival, "time", None)
        end_ts = getattr(last.arrival if last.HasField("arrival") else last.departure, "time", None)

        return self._epoch_to_dt(start_ts), self._epoch_to_dt(end_ts)

    def fetch_tripupdates(self, route_id: str) -> List[dict]:
        headers = {
            "Accept": "application/x-google-protobuf",
            "User-Agent": "python-requests/3.12",
            "Accept-Encoding": "identity",
        }
        params = {"key": self.api_key}

        try:
            resp = requests.get(self.api_url, params=params, headers=headers, timeout=20)
            resp.raise_for_status()
        except Exception as e:
            logger.error("HTTP request failed: %s", e)
            raise BkkApiError(f"HTTP request failed: {e}") from e

        feed = gtfs_realtime_pb2.FeedMessage()
        try:
            feed.ParseFromString(resp.content)
        except Exception as e:
            logger.error("Failed to parse protobuf: %s", e)
            raise BkkApiError(f"Protobuf parse failed: {e}") from e

        results = []
        for entity in feed.entity:
            if not entity.HasField("trip_update"):
                continue
            tu = entity.trip_update
            if tu.trip.route_id != route_id:
                continue
            start_dt, end_dt = self._extract_first_last_times(tu.stop_time_update)
            results.append({
                "route_id": tu.trip.route_id,
                "trip_id": tu.trip.trip_id or "",
                "start_time": start_dt,
                "end_time": end_dt,
            })

        logger.info("Fetched %d trips for route %s", len(results), route_id)
        return results
