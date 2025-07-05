import yaml
from typing import Any, Dict

def load_config(path: str) -> Dict[str, Any]:
    """
    Load YAML configuration from *path*.
    If file doesn't exist, returns an empty dict (używa domyślnych ustawień).
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        print(f"[WARN] Nie znaleziono pliku konfiguracyjnego '{path}', używam ustawień domyślnych.")
        return {}
