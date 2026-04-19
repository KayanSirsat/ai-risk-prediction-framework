"""Configuration helpers for environment-based runtime settings."""

from __future__ import annotations

import os
from pathlib import Path


def load_env_file(path: str | None = None) -> None:
    """Load key/value pairs from an .env file into process env."""
    env_path = Path(path) if path else Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_env(key: str, default: str = "") -> str:
    """Get an environment variable with a default."""
    return os.getenv(key, default)


def get_jira_oauth_settings() -> dict[str, str]:
    """Return Jira OAuth settings from environment with sensible defaults."""
    load_env_file()
    return {
        "client_id": get_env("JIRA_OAUTH_CLIENT_ID"),
        "client_secret": get_env("JIRA_OAUTH_CLIENT_SECRET"),
        "redirect_uri": get_env("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8501"),
    }
