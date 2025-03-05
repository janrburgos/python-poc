from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down gracefully...")

@app.get("/")
def read_root():
    return {
        "message": "Hello, FastAPI!",
    }
