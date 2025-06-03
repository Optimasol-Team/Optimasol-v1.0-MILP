def generate_schedule(n: int, start: str = "00:00") -> list:
    """
    Generates a list of time labels in "HH:MM" format evenly spaced over 24 hours.

    Parameters:
        n (int): Number of time intervals.
        start (str): Starting time in "HH:MM" format (default: "00:00").

    Returns:
        List[str]: List of time strings (length n).
    """
    h0, m0 = map(int, start.split(":"))
    total_start_minutes = h0 * 60 + m0
    step_minutes = 1440 // n

    time_labels = []
    for i in range(n):
        total_minutes = (total_start_minutes + i * step_minutes) % 1440
        h, m = divmod(total_minutes, 60)
        time_labels.append(f"{h:02d}:{m:02d}")

    return time_labels
