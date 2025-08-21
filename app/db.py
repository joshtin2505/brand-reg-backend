import os
import asyncio
from typing import Optional, Any

from dotenv import load_dotenv
from libsql_client import create_client

# Load environment variables from .env if present
load_dotenv()

_client = None
_client_loop: Optional[asyncio.AbstractEventLoop] = None
_recreating = False  # evita carrera en alta concurrencia


def _need_recreate(stored_loop: Optional[asyncio.AbstractEventLoop], current_loop: Optional[asyncio.AbstractEventLoop]) -> bool:
    # Si no hay cliente asociado aún
    if stored_loop is None:
        return False
    # Loop original cerrado
    if stored_loop.is_closed():
        return True
    # En entornos serverless puede cambiar el loop entre invocaciones;
    # si cambia y el anterior ya no está vivo, recreamos. Si sigue vivo, lo dejamos.
    if current_loop is not None and current_loop is not stored_loop and stored_loop.is_closed():
        return True
    return False


def get_client():
    """
    Devuelve un singleton libsql client. Si el event loop original está cerrado
    (se da en funciones serverless reutilizadas), recrea el cliente.
    """
    global _client, _client_loop, _recreating

    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None  # llamado desde contexto sync (p.e. arranque)
    
    if _client is not None and _need_recreate(_client_loop, current_loop):
        _client = None
        _client_loop = None

    if _client is None and not _recreating:
        _recreating = True
        try:
            url = os.getenv("TURSO_URL")
            auth_token = os.getenv("TURSO_AUTH_TOKEN")
            print("Creating libsql client. URL:", url)
            if not url:
                raise RuntimeError("Missing TURSO_URL env var")
            if not auth_token:
                raise RuntimeError("Missing TURSO_AUTH_TOKEN env var")
            _client = create_client(url, auth_token=auth_token)
            _client_loop = current_loop
        finally:
            _recreating = False

    return _client


async def execute_safe(sql: str, *params: Any, **kw) -> Any:
    """
    (Optativo) Ejecuta una sentencia intentando recrear el cliente si aparece
    'Event loop is closed'. Útil si quieres envolver llamadas en código existente.
    """
    client = get_client()
    try:
        return await client.execute(sql, *params, **kw)
    except RuntimeError as e:
        msg = str(e)
        if "Event loop is closed" in msg:
            # Forzar recreación y reintentar una vez
            global _client, _client_loop
            _client = None
            _client_loop = None
            client = get_client()
            return await client.execute(sql, *params, **kw)
        raise


async def init_db():
    """Create tables if they do not exist."""
    client = get_client()
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
    """
    Cerrar el cliente manualmente (para scripts locales).
    No llamar en cada request en Vercel / serverless.
    """
    global _client, _client_loop
    if _client is None:
        return
    try:
        close = getattr(_client, "close", None)
        if close:
            res = close()
            if hasattr(res, "__await__"):
                await res
    except Exception:
        pass
    finally:
        _client = None
        _client_loop = None

