alembic upgrade head

USE_ALEMBIC=true

uvicorn app.main:app --host 0.0.0.0 --port 80
