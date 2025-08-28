from fastapi import FastAPI
from controllers import trip_controller

def create_app() -> FastAPI:
    app = FastAPI(title="API")
    app.include_router(trip_controller.router, prefix="/api/trips", tags=["Trips"])
    return app

app = create_app()
