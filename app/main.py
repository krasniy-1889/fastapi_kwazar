from fastapi.applications import FastAPI

app = FastAPI(debug=True, title="Квазар")


@app.get("/")
async def index():
    return {"message": "привет квазар"}
