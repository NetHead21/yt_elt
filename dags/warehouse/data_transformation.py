from datetime import timedelta


def parse_duration(duration_str: str) -> timedelta:
    """Converts an ISO 8601 duration string to a timedelta.

    Supports days, hours, minutes, and seconds (e.g. 'PT10M30S', 'PT2H', 'PT1D2H30M15S').
    Returns timedelta(0) if the input is None.

    Args:
        duration_str: ISO 8601 duration string as returned by the YouTube Data API
                      (e.g. 'PT15M33S').

    Returns:
        A timedelta representing the duration.
    """

    if duration_str is None:
        return timedelta(0)

    duration_str = duration_str.removeprefix("P")
    day, hour, minute, second = 0, 0, 0, 0

    if "D" in duration_str:
        day, duration_str = duration_str.split("D")
        day = int(day)
        duration_str = duration_str.removeprefix("T")
    else:
        duration_str = duration_str.removeprefix("T")

    if "H" in duration_str:
        hour, duration_str = duration_str.split("H")
        hour = int(hour)
    if "M" in duration_str:
        minute, duration_str = duration_str.split("M")
        minute = int(minute)
    if "S" in duration_str:
        second, _ = duration_str.split("S")
        second = int(second)

    return timedelta(days=day, hours=hour, minutes=minute, seconds=second)


def transform_data(row: dict) -> dict:
    """Transforms a raw YouTube API row into a cleaned row ready for the core schema.

    Transformations applied:
    - Converts 'duration' from ISO 8601 string to timedelta.
    - Derives 'video_type' as 'Short' (≤ 60s) or 'Normal' if not already set.
    - Casts 'view_count', 'like_count', 'comment_count' from string to int (defaults to 0 if None).

    Args:
        row: A dict representing a single video record from the staging layer.

    Returns:
        A new dict with the transformed values — the original row is not mutated.
    """
