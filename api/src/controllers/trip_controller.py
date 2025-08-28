from fastapi import APIRouter, Query
from datetime import date, timedelta
from services.trip_service import TripService

router = APIRouter()
service = TripService()

@router.get("/routes")
def list_routes():
    return {"routes": service.list_routes()}

@router.get("/find/{route_id}")
def find_route(
    route_id: str,
    start_date: date | None = Query(None, description="YYYY-MM-DD"),
    end_date: date | None = Query(None, description="YYYY-MM-DD")
):
    if not start_date or not end_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=7)

    return service.get_trip_statistics(route_id, start_date, end_date)
