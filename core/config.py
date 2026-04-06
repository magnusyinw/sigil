"""
Sigil Configuration Loader
Loads and merges sigil.config.yaml with defaults.
"""

import os
import re
import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "llm": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-6",
        "api_key": "${ANTHROPIC_API_KEY}",
        "base_url": None,
    },
    "indexing": {
        "language": "auto",
        "anchor_min_chars": 7,
        "anchor_max_chars": 15,
        "confidence_threshold": 0.8,
        "auto_backlink": True,
        "max_chars": 12000,
    },
    "storage": {
        "backend": "sqlite",
        "path": "./sigil.db",
    },
    "interface": {
        "mcp":     {"enabled": True, "port": 3000},
        "rest_api": {"enabled": True, "port": 3001},
    },
    "logging": {
        "level": "info",
        "audit_trail": True,
    },
}


def load_config(config_path: str = "sigil.config.yaml") -> dict:
    config = _deep_copy(DEFAULT_CONFIG)
    if Path(config_path).exists():
        with open(config_path, "r", encoding="utf-8") as f:
            user = yaml.safe_load(f) or {}
        config = _deep_merge(config, user)
    return config


def resolve_env(value: str) -> str:
    """Resolve ${ENV_VAR} patterns in config values."""
    if not value:
        return ""
    match = re.match(r"^\$\{(.+)\}$", str(value))
    if match:
        return os.environ.get(match.group(1), "")
    return str(value)


def _deep_copy(d: dict) -> dict:
    import copy
    return copy.deepcopy(d)


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        elif v is not None:
            result[k] = v
    return result
