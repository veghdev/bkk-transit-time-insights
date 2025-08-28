from typing import List
from datetime import date
from db_client import DBConnection
from config import Config

class TripRepository:
    def __init__(self, config: Config = Config()):
        self.db = DBConnection(config)

    def get_routes(self) -> List[str]:
        query = """
            SELECT DISTINCT route_id
            FROM trips;
        """
        with self.db.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        return [r[0] for r in rows]

    def get_latest_trips(self, route_id: str, start_date: date, end_date: date):
        query = """
            SELECT DISTINCT ON (trip_id) 
                trip_id, start_time, end_time, collected_at
            FROM trips
            WHERE route_id = %s
              AND start_time >= %s
              AND start_time < %s + interval '1 day'
            ORDER BY trip_id, collected_at DESC;
        """
        with self.db.cursor() as cur:
            cur.execute(query, (route_id, start_date, end_date))
            rows = cur.fetchall()

        return [
            {"trip_id": r[0], "start_time": r[1], "end_time": r[2], "collected_at": r[3]}
            for r in rows
        ]
