# config_weather_loader.py
from pathlib import Path
from typing import Union

def config_weather_loader(config_dir: Union[str, Path]) -> int:
    """
    Read the file `weather_frequency.txt` located in *config_dir*,
    extract the value of ``frequency`` (expressed in **hours**) and
    return the equivalent number of **seconds**.

    Parameters
    ----------
    config_dir : str | pathlib.Path
        Directory that contains ``weather_frequency.txt``.

    Returns
    -------
    int
        The frequency converted to seconds.

    Raises
    ------
    FileNotFoundError
        If the configuration file is missing.
    ValueError
        If no valid ``frequency`` line is found or the line is malformed.

    Example
    -------
    >>> seconds = config_weather_loader("/opt/my_app/config")
    >>> print(seconds)
    10800
    """
    cfg_path = Path(config_dir) / "weather_frequency.txt"

    if not cfg_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {cfg_path}")

    for raw_line in cfg_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        # Skip comments and empty lines
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("frequency"):
            try:
                _, value = line.split("=", 1)
                hours = int(value.strip())
            except (ValueError, IndexError):
                raise ValueError(
                    f"Malformed 'frequency' line in {cfg_path}: {raw_line!r}"
                )
            return hours * 3600  # hours → seconds

    # No frequency found
    raise ValueError(f"No 'frequency' entry found in {cfg_path}")
