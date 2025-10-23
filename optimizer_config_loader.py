# optimizer_config_loader.py
from pathlib import Path

def config_optimizer_loader(config_dir: Path | str) -> int:
    cfg_path = Path(config_dir) / "optimize_config.txt"
    for raw in cfg_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("step_minutes"):
            _, val = line.split("=", 1)
            return int(val.strip())
    raise ValueError("step_minutes non trouvé")
