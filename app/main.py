from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.api import api_router
from app.core.config import get_settings
from app.database.db import Base, engine

# create DB tables (would be better to use Alembic)
Base.metadata.create_all(bind=engine)


app = FastAPI(title="Simple To-Do API")

# add CORS middleware to allow requests from any origin (public API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# add Session middleware so Authlib can access the request session
app.add_middleware(SessionMiddleware, secret_key=get_settings().SECRET_KEY)

app.include_router(api_router, prefix="/api")
