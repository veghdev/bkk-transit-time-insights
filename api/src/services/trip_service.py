from datetime import date, time
from statistics import mean
from typing import Dict, Any, List
from zoneinfo import ZoneInfo

from repositories.trip_repository import TripRepository
from config import Config

class TripService:
    PERIODS_ORDER = ["before_morning_peak", "morning_peak", "daytime", "afternoon_peak", "evening"]

    def __init__(self, repo: TripRepository | None = None, config: Config | None = None):
        self.config = config or Config()
        self.tz = ZoneInfo(self.config.TZ)
        self.repo = repo or TripRepository()

    def list_routes(self) -> List[str]:
        return self.repo.get_routes()

    def get_trip_statistics(self, route_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        trips = self.repo.get_latest_trips(route_id, start_date, end_date)
        if not trips:
            return {
                "route_id": route_id,
                "interval": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
                "overall_avg_minutes": None,
                "days": []
            }

        by_day: Dict[date, Dict[str, Any]] = {}
        all_durations: List[float] = []

        for t in trips:
            if not t["start_time"] or not t["end_time"]:
                continue

            start_local = t["start_time"].astimezone(self.tz)
            end_local = t["end_time"].astimezone(self.tz)
            if end_local <= start_local:
                continue

            duration_min = (end_local - start_local).total_seconds() / 60.0
            trip_day = start_local.date()
            day_name = start_local.strftime("%A")
            period = self._classify_period(start_local.time())

            if trip_day not in by_day:
                by_day[trip_day] = {
                    "durations": [],
                    "periods": {p: [] for p in self.PERIODS_ORDER},
                    "day_name": day_name
                }

            by_day[trip_day]["durations"].append(duration_min)
            by_day[trip_day]["periods"][period].append(duration_min)
            all_durations.append(duration_min)

        days_out = []
        for d in sorted(by_day.keys()):
            bucket = by_day[d]
            periods_avg = {p: round(mean(vals), 2) for p, vals in bucket["periods"].items() if vals}
            day_avg = round(mean(bucket["durations"]), 2) if bucket["durations"] else None
            days_out.append({
                "date": d.isoformat(),
                "day": bucket["day_name"],
                "avg_minutes": day_avg,
                "periods": periods_avg
            })

        overall_avg = round(mean(all_durations), 2) if all_durations else None

        return {
            "route_id": route_id,
            "interval": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "avg_minutes": overall_avg,
            "days": days_out
        }

    def _classify_period(self, t: time) -> str:
        if t < time(7, 0):
            return "before_morning_peak"
        elif t < time(10, 0):
            return "morning_peak"
        elif t < time(15, 0):
            return "daytime"
        elif t < time(18, 0):
            return "afternoon_peak"
        else:
            return "evening"
