"""Value formats shared by the partner's files (see requirements/provider.md)."""
from datetime import datetime, timezone


def utc_timestamp(dt: datetime) -> str:
    """A timezone-aware datetime as UTC text with milliseconds: 2026-10-19T19:05:00.000Z"""
    if dt.tzinfo is None:
        raise ValueError(f"{dt!r} has no timezone; use a timezone-aware datetime")
    utc = dt.astimezone(timezone.utc)
    return utc.strftime("%Y-%m-%dT%H:%M:%S.") + f"{utc.microsecond // 1000:03d}Z"
