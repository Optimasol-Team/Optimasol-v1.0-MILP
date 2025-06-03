def profile_setmode(index: int, value: int, config: dict = None) -> str:
    """
    Converts a binary heater state into a SETMODE MQTT command.

    Parameters:
        index (int): Time index (e.g. 0 for 00:00, 1 for 01:00, etc.)
        value (int): Binary heater value (0 or 1)
        config (dict): Optional parameters (unused here)

    Returns:
        str: MQTT command string
    """
    return "SETMODE 11" if value == 1 else "SETMODE 10"


def profile_dimmer(index: int, value: int, config: dict = None) -> str:
    """
    Converts a binary heater state into a DIMMER MQTT command based on index.

    Parameters:
        index (int): Time index used to compute the dimmer percentage
        value (int): Binary heater value (0 or 1)
        config (dict): Optional dict (can hold scaling factor, etc.)

    Returns:
        str: MQTT command string
    """
    if value == 0:
        return "SETMODE 10"

    # Optional scaling factor (default 4.5 per index step)
    step_value = config.get("step_value", 4.5) if config else 4.5
    percentage = round(index * step_value, 1)
    return f"DIMMER1 {percentage}"


# Dictionary of available translation profiles
AVAILABLE_PROFILES = {
    "setmode": profile_setmode,
    "dimmer": profile_dimmer,
}
