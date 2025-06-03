from .profiles import AVAILABLE_PROFILES


def translate(index: int, value: int, profile_name: str = "setmode", config: dict = None) -> str:
    """
    Translates a binary heater state into a corresponding MQTT command string
    using the selected translation profile.

    Parameters:
        index (int): Index of the time interval.
        value (int): Heater ON/OFF status (1 or 0).
        profile_name (str): Name of the translation profile to use.
        config (dict): Optional configuration dictionary for the profile.

    Returns:
        str: MQTT command string.

    Raises:
        ValueError: If the specified profile is not defined.
    """
    if profile_name not in AVAILABLE_PROFILES:
        raise ValueError(f"Unknown translation profile: {profile_name}")

    return AVAILABLE_PROFILES[profile_name](index, value, config)
