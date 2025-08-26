import os
import random
import psycopg2
from datetime import datetime, timezone, timedelta
from typing import List, Dict


ROUTES = ["0050", "0070", "0090"]

DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", 5432),
}

FIRST_TRIP_HOUR = 4
LAST_TRIP_HOUR = 24
TRIP_BASE_DURATION_MIN = 60
PEAK_HOURS = [(7, 10), (15, 18)]
COLLECTION_OFFSET_MIN = 30


class DBHandler:
    def __init__(self, db_config: Dict):
        self.db_config = db_config

    def __enter__(self):
        self.conn = psycopg2.connect(**self.db_config)
        self.cur = self.conn.cursor()
        self._create_table()
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def _create_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id BIGSERIAL PRIMARY KEY,
            route_id TEXT NOT NULL,
            trip_id TEXT NOT NULL,
            start_time TIMESTAMPTZ,
            end_time TIMESTAMPTZ,
            collected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """)
        self.cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_trips_route_trip_latest
        ON trips (route_id, trip_id, collected_at DESC);
        """)


class TripGenerator:
    def __init__(self, peak_hours=PEAK_HOURS):
        self.peak_hours = peak_hours

    def generate_trips_for_day(self, route_id: str, base_date: datetime.date) -> List[Dict]:
        trips = []

        DURATION_VARIANCE = 2
        PEAK_EXTRA_MIN_MIN = 5
        PEAK_EXTRA_MIN_MAX = 15

        first_trip_time = datetime.combine(base_date, datetime.min.time()) + timedelta(
            hours=FIRST_TRIP_HOUR
        )
        last_trip_time = datetime.combine(base_date, datetime.min.time()) + timedelta(
            hours=LAST_TRIP_HOUR
        )

        trip_start = first_trip_time
        while trip_start < last_trip_time:
            duration = timedelta(minutes=TRIP_BASE_DURATION_MIN + random.randint(-DURATION_VARIANCE, DURATION_VARIANCE))
            if any(start <= trip_start.hour < end for start, end in self.peak_hours):
                duration += timedelta(minutes=random.randint(PEAK_EXTRA_MIN_MIN, PEAK_EXTRA_MIN_MAX))
            trip_end = trip_start + duration

            trip_id = self._generate_trip_id(route_id, trip_start)

            trips.extend(self._generate_collected_times(route_id, trip_id, trip_start, trip_end))

            trip_start += timedelta(minutes=10 + random.randint(-DURATION_VARIANCE, DURATION_VARIANCE))

        return trips

    @staticmethod
    def _generate_trip_id(route_id: str, trip_start: datetime) -> str:
        TRIP_ID_MIN = 1000
        TRIP_ID_MAX = 9999
        return f"{route_id}_{trip_start.strftime('%H%M')}_{random.randint(TRIP_ID_MIN,TRIP_ID_MAX)}"

    @staticmethod
    def _generate_collected_times(route_id: str, trip_id: str, start: datetime, end: datetime) -> List[Dict]:
        collected_times = []
        current_collected = start - timedelta(minutes=COLLECTION_OFFSET_MIN)
        collected_end = end + timedelta(minutes=COLLECTION_OFFSET_MIN)

        END_TIME_VARIANCE_SEC = 30
        while current_collected <= collected_end:
            effective_end = end if current_collected < start or current_collected > end else end + timedelta(
                seconds=random.randint(-END_TIME_VARIANCE_SEC, END_TIME_VARIANCE_SEC)
            )
            collected_times.append({
                "route_id": route_id,
                "trip_id": trip_id,
                "start_time": start,
                "end_time": effective_end,
                "collected_at": current_collected
            })
            current_collected += timedelta(minutes=1)

        return collected_times


class TripSeeder:
    def __init__(self, routes: List[str], db_config: Dict, days_back: int = 7):
        self.routes = routes
        self.days_back = days_back
        self.generator = TripGenerator()
        self.db_config = db_config

    def seed(self):
        today = datetime.now(timezone.utc).date()
        all_rows = []

        for days_ago in range(self.days_back, 0, -1):
            date_to_seed = today - timedelta(days=days_ago)
            for route in self.routes:
                trips = self.generator.generate_trips_for_day(route, date_to_seed)
                all_rows.extend(trips)

        all_rows.sort(key=lambda x: x["collected_at"])

        with DBHandler(self.db_config) as cur:
            for row in all_rows:
                cur.execute("""
                    INSERT INTO trips (route_id, trip_id, start_time, end_time, collected_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    row["route_id"],
                    row["trip_id"],
                    row["start_time"],
                    row["end_time"],
                    row["collected_at"],
                ))

        print("Seeding complete")


if __name__ == "__main__":
    seeder = TripSeeder(ROUTES, DB_CONFIG, days_back=7)
    seeder.seed()
