import psycopg2
from typing import Dict, List, Any
from config import Config

class DBHandler:
    def __init__(self, config: Config):
        self.db_config: Dict[str, Any] = {
            "dbname": config.POSTGRES_DB,
            "user": config.POSTGRES_USER,
            "password": config.POSTGRES_PASSWORD,
            "host": config.POSTGRES_HOST,
            "port": config.POSTGRES_PORT,
        }
        self.conn = psycopg2.connect(**self.db_config)

    def insert_trips(self, trips: List[Dict[str, Any]]):
        if not trips:
            return
        try:
            with self.conn.cursor() as cur:
                for trip in trips:
                    cur.execute(
                        """
                        INSERT INTO trips (route_id, trip_id, start_time, end_time)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (trip["route_id"], trip["trip_id"], trip["start_time"], trip["end_time"])
                    )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
