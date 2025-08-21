from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db import init_db
from app.routers.brands import router as brands_router


settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)

# CORS
app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.cors_origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
  # Ensure DB schema exists
  await init_db()


@app.get("/health")
async def health():
  return {"status": "ok"}


@app.get("/")
async def root():
  return {"message": f"{settings.app_name} running"}


# Routers
app.include_router(brands_router)