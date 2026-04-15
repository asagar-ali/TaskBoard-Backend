from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.tasks import router as tasks_router
from app.api.webhooks import router as webhooks_router  # ✅ was never imported
from app.core.config import settings
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Management API",
    version="1.0.0",
    description="A simple API for managing tasks",
)

# ✅ Fix: allow_origins must be explicit (not "*") when allow_credentials=True.
# Wildcard + credentials is rejected by browsers per the CORS spec.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router)
app.include_router(webhooks_router)  # ✅ webhook routes now actually registered