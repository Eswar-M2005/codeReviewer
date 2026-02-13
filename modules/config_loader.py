import tomllib
import os

DEFAULT_CONFIG = {
    "severity_threshold": "INFO",
    "exclude_paths": [],
    "rules": []
}


def load_config():
    config_path = "pyproject.toml"

    if not os.path.exists(config_path):
        return DEFAULT_CONFIG

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    return data.get("tool", {}).get("codereviewer", DEFAULT_CONFIG)
