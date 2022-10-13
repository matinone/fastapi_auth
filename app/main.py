from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.db import engine, Base
from app.api.api import api_router

# create DB tables (would be better to use Alembic)
Base.metadata.create_all(bind=engine)


app = FastAPI(title="Simple To-Do API")

# Add CORS middleware to allow requests from any origin (public API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_credentials=True,   # not compatible with allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
