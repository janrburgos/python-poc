from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine

from .routers import status, arithmetic, user

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def read_root():
    return {
        "message": "Hello, FastAPI!",
    }


app.include_router(user.router, prefix="/users", tags=["Users"])

app.include_router(status.router, prefix="/status", tags=["Status Classifier"])
app.include_router(arithmetic.router, prefix="/arithmetic", tags=["Math-Tinik"])
