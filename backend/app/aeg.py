from datetime import datetime, timezone


def nyyd() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)


def nyyd_ms() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
