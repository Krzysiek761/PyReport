import yaml
from typing import Any, Dict

def load_config(path: str) -> Dict[str, Any]:
    """Load YAML configuration from *path*."""
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}
