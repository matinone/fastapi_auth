from fastapi import APIRouter

from app.api.endpoints import (login, login_google, password_recovery, todos,
                               users)

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(login.router)
api_router.include_router(login_google.router)
api_router.include_router(todos.router)
api_router.include_router(password_recovery.router)
