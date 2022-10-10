from fastapi import FastAPI

from app.database.db import engine, Base
from app.api.api import api_router

# create DB tables (would be better to use Alembic)
Base.metadata.create_all(bind=engine)


app = FastAPI(title="Simple To-Do API")

app.include_router(api_router, prefix="/api")
