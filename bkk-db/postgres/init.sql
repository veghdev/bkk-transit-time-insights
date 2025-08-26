CREATE TABLE IF NOT EXISTS trips (
    id BIGSERIAL PRIMARY KEY,
    route_id TEXT NOT NULL,
    trip_id TEXT NOT NULL,
    start_time TIMESTAMPTZ,
    end_time   TIMESTAMPTZ,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trips_route_trip_latest
ON trips (route_id, trip_id, collected_at DESC);