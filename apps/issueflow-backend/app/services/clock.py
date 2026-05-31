from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return current UTC time. Centralized for deterministic testing via monkeypatch."""
    return datetime.now(UTC)
