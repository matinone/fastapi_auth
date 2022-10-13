from fastapi import APIRouter

from app.api.endpoints import users, login, todos

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(login.router)
api_router.include_router(todos.router)
