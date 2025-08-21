from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv


# Load environment variables from .env for local development
load_dotenv()


class Settings:
	"""Simple settings container without extra dependencies."""

	app_name: str = os.getenv("APP_NAME", "Brand Reg Backend")
	app_version: str = os.getenv("APP_VERSION", "0.1.0")
	frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
	# Comma-separated list of CORS origins; defaults to local Next.js dev
	_cors = os.getenv(
		"CORS_ORIGINS", f"http://localhost:3000,http://127.0.0.1:3000,{frontend_url}"
	)
	cors_origins: list[str] = [o.strip() for o in _cors.split(",") if o.strip()]

	# Turso/libSQL connection
	turso_url: str | None = os.getenv("TURSO_URL")
	turso_auth_token: str | None = os.getenv("TURSO_AUTH_TOKEN")


@lru_cache
def get_settings() -> Settings:
	return Settings()
