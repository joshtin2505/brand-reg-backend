import os
from typing import Optional

from dotenv import load_dotenv
from libsql_client import create_client

# Load environment variables from .env if present
load_dotenv()

_client = None


def get_client():
	"""
	Returns a singleton libsql client connected to the configured Turso/libSQL database.
	Requires TURSO_URL and TURSO_AUTH_TOKEN in environment.
	"""
	global _client
	if _client is None:
		url = os.getenv("TURSO_URL")
		auth_token = os.getenv("TURSO_AUTH_TOKEN")
		print("Creating client with URL:", url)
		if not url:
			raise RuntimeError("Missing TURSO_URL env var")
		if not auth_token:
			raise RuntimeError("Missing TURSO_AUTH_TOKEN env var")
		_client = create_client(url, auth_token=auth_token)
	return _client


async def init_db():
	"""Create tables if they do not exist."""
	client = get_client()
	# SQLite/libSQL DDL for brands
	await client.execute(
		"""
		CREATE TABLE IF NOT EXISTS brands (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			brand TEXT NOT NULL,
			holder TEXT NOT NULL,
			status TEXT NOT NULL CHECK (status IN ('active','pending','inactive')),
			created_at TEXT DEFAULT CURRENT_TIMESTAMP
		);
		"""
	)


async def close_client():
	"""Close the global client if possible (for scripts or graceful shutdown)."""
	global _client
	if _client is None:
		return
	try:
		close = getattr(_client, "close", None)
		if close:
			if callable(close):
				res = close()
				if hasattr(res, "__await__"):
					await res
	except Exception:
		# Ignore close errors
		pass

