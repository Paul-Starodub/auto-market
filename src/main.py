from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.routes import categories_router, cars_router, customers_router

BASE_DIR = Path(__file__).resolve().parent.parent


app = FastAPI()
app.mount("/src/media", StaticFiles(directory=BASE_DIR / "src" / "media"), name="media")
app.mount("/src/static", StaticFiles(directory=BASE_DIR / "src" / "static"), name="static")
app.include_router(categories_router)
app.include_router(customers_router)
app.include_router(cars_router)


@app.get("/")
def root() -> dict:
    return {"message": "Test endpoint"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
