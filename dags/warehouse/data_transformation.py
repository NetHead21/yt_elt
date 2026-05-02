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

    transformed_row = row.copy()
    if "duration" in transformed_row:
        transformed_row["duration"] = parse_duration(transformed_row["duration"])

    if transformed_row.get("video_type") is None and "duration" in transformed_row:
        transformed_row["video_type"] = (
            "Short"
            if transformed_row["duration"] <= timedelta(seconds=60)
            else "Normal"
        )

    for field in ("view_count", "like_count", "comment_count"):
        if field in transformed_row:
            transformed_row[field] = (
                int(transformed_row[field]) if transformed_row[field] is not None else 0
            )

    return transformed_row


if __name__ == "__main__":
    test_durations = [
        "PT15M33S",
        "PT2H45M",
        "PT1H30S",
        "PT20M",
        "PT45S",
        "PT3H",
        "PT1D2H30M15S",
    ]

    for dur in test_durations:
        print(f"{dur} -> {parse_duration(dur)}")

    test_row = {
        "video_id": "6W_841xoprg",
        "title": "Can a Window Stop a Wrecking Ball?",
        "published_at": "2026-04-14T16:00:01Z",
        "duration": "PT30S",
        "view_count": "48445009",
        "like_count": "1160445",
        "comment_count": "9400",
    }

    transformed = transform_data(test_row)
    print(transformed)
