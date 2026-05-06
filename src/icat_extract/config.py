import logging

import yaml
import os
from pathlib import Path


logger = logging.getLogger(__name__)


def load_config(path: Path) -> dict:
    """
    Load configuration from a YAML file.

    Parameters:
    - path: The path to the YAML configuration file

    Returns:
    - A dictionary containing the configuration
    """
    if not path.exists():
        logger.error(f"Config file not found: {path}")
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open() as f:
        return yaml.safe_load(f)


def resolve_secrets(value: str) -> str:
    """
    Resolve secrets in a configuration value. If the value is in the format ${ENV_VAR},
    it will be replaced with the value of the corresponding environment variable.

    Parameters:
    - value: The configuration value to resolve

    Returns:
    - The resolved configuration value
    """
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        var = value[2:-1]
        if var not in os.environ:
            logger.warning(
                f"Environment variable {var} not set for config value {value}"
            )
            raise RuntimeError(
                f"Environment variable {var} not set for config value {value}"
            )
        return os.environ[var]
    return value
