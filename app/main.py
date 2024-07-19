from fastapi.applications import FastAPI

from app.users.routes import route as user_route


def create_app():
    app = FastAPI(debug=True, title="Квазар")

    # Добаляем роуты
    routes = [
        user_route,
    ]
    for route in routes:
        app.include_router(route)

    @app.get("/")
    async def index():
        return {"message": "привет квазар"}

    return app


app = create_app()
