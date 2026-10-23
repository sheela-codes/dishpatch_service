"""Turning the partner's timestamps into Python datetimes."""
from datetime import datetime, timezone


def parse_timestamp(text):
    """'2026-09-01T17:03:21.992Z' -> a datetime in UTC.  None (or empty) stays None."""
    if text is None or text == "":
        return None
    moment = datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%fZ")
    return moment.replace(tzinfo=timezone.utc)
