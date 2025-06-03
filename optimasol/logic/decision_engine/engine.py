from .scheduler import generate_schedule
from .translator import translate


def format_decision(sequence, n: int, profile: str = "setmode", start: str = "00:00", config: dict = None) -> dict:
    """
    Formats a binary sequence into a timestamped MQTT command dictionary.

    Parameters:
        sequence (List[int]): List of 0s and 1s representing ON/OFF schedule.
        n (int): Total number of time intervals.
        profile (str): Name of the command translation profile (default: "setmode").
        start (str): Starting time in HH:MM format (default: "00:00").
        config (dict): Optional configuration for the profile logic.

    Returns:
        Dict[str, str]: A mapping from time (HH:MM) to MQTT command.
    """
    timestamps = generate_schedule(n, start=start)
    return {
        timestamps[i]: translate(i, value, profile_name=profile, config=config)
        for i, value in enumerate(sequence)
    }
