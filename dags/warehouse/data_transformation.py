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
