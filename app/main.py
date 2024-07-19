from fastapi.applications import FastAPI

from app.users.routes import route as user_route


def create_app():
    app = FastAPI(debug=True, title="Квазар")

    # Добавляем роуты
    routes = [
        user_route,
    ]
    for route in routes:
        app.include_router(route)

    return app


app = create_app()


@app.get("/")
async def index():
    return {"message": "привет квазар"}
