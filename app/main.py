from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core.security import get_settings
from app.database.init_db import init_db

if get_settings().ENVIRONMENT != "test":
    init_db()

app = FastAPI(title="Simple To-Do API")

# add CORS middleware to allow requests from any origin (public API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
