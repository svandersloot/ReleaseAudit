# src/config_loader.py
import json
import logging
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_config(config_file: str) -> Dict[str, object]:
    """Load configuration from JSON file and .env variables."""
    # Load .env from project root if present
    env_path = Path(config_file).resolve().parent / ".env"
    load_dotenv(env_path)

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            logger.debug("Loaded configuration from %s", config_file)
            return config
    except FileNotFoundError:
        logger.debug("Config file %s not found. Relying on environment variables.", config_file)
        return {}
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in config file %s: %s", config_file, exc)
        raise ValueError(f"Invalid JSON in config file: {exc}")