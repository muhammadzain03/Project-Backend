import os
from pathlib import Path

from dotenv import load_dotenv

# Monorepo root: backend/utils -> parents[2] == SENG 533 - Project
PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


def _resolve_optional_path(value: str | None) -> str | None:
    """Resolve relative paths from the monorepo root (e.g. credentials/key.json)."""
    if not value:
        return None
    p = Path(value)
    if p.is_absolute():
        return str(p.resolve())
    return str((PROJECT_ROOT / p).resolve())


def _resolve_gcp_credentials_path(env_value: str | None) -> str | None:
    """Resolve service account JSON; try monorepo root then backend/ for relative paths."""
    if not env_value:
        return None
    p = Path(env_value)
    if p.is_absolute():
        return str(p.resolve())
    rel = Path(env_value)
    candidates = [
        PROJECT_ROOT / rel,
        PROJECT_ROOT / "backend" / rel,
    ]
    for c in candidates:
        if c.is_file():
            return str(c.resolve())
    return str((PROJECT_ROOT / rel).resolve())


class BaseConfig:
    GCS_BUCKET = os.environ.get("GCS_BUCKET")
    GOOGLE_APPLICATION_CREDENTIALS = _resolve_gcp_credentials_path(
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    )

    DATABASE_HOST = os.environ.get("DATABASE_HOST")
    DATABASE_USER = os.environ.get("DATABASE_USER")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")
    DATABASE_PORT = int(os.environ.get("DATABASE_PORT", "3306"))

    # Connection pool size (0 = disabled, falls back to per-query connections)
    DB_POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", "10"))