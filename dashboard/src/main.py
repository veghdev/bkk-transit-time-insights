from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from api_client import ApiClient
from data_transformer import transform_to_vizzu
from frontend import get_html

def create_app() -> FastAPI:
    app = FastAPI(title="BKK Dashboard")
    api_client = ApiClient()

    @app.get("/routes")
    async def routes():
        return await api_client.get_routes()

    @app.get("/route/{route_id}")
    async def route(route_id: str):
        return await api_client.get_route(route_id)

    @app.get("/transform/{route_id}")
    async def route_transform(route_id: str):
        stats = await api_client.get_route(route_id)
        data = transform_to_vizzu(stats)
        return JSONResponse(content=data)

    @app.get("/", response_class=HTMLResponse)
    async def index():
        return get_html()

    return app

app = create_app()
