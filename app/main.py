from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.api.endpoints.login_google import google_auth_app
from app.core.security import get_settings
from app.database.db import Base, engine

if get_settings().ENVIRONMENT != "test":
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

app.include_router(api_router, prefix="/api")

# use a subapp so the Session middleware required for Google authentication
# is only present in those endpoints
app.mount("/api", google_auth_app)
