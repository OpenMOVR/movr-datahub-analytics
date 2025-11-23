"""
Configuration loader with multi-layered priority system.

Priority order:
1. Environment variables
2. Local config file (config/local.yaml)
3. Default config file (config/config.yaml)
4. Built-in defaults
"""

import os
import yaml
from pathlib import Path
from typing import Optional
from loguru import logger

from movr.config.schema import MOVRConfig


class ConfigLoader:
    """Load and manage MOVR configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config loader.

        Args:
            config_path: Optional path to config file. If not provided,
                        will search for config/config.yaml
        """
        self.config_path = config_path or self._find_config_file()
        self._config: Optional[MOVRConfig] = None

    def _find_config_file(self) -> Optional[Path]:
        """Find config file in standard locations, including parent directories."""
        # First, check current directory and explicit cwd
        search_paths = [
            Path("config/local.yaml"),
            Path("config/config.yaml"),
            Path.cwd() / "config/local.yaml",
            Path.cwd() / "config/config.yaml",
        ]

        for path in search_paths:
            if path.exists():
                logger.info(f"Found config file: {path}")
                return path

        # Search parent directories (useful when running from subdirectories like notebooks/)
        current = Path.cwd().resolve()
        for _ in range(5):  # Limit search depth
            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            for config_name in ["config/local.yaml", "config/config.yaml"]:
                config_path = parent / config_name
                if config_path.exists():
                    logger.info(f"Found config file in parent: {config_path}")
                    return config_path
            current = parent

        logger.warning("No config file found, using defaults")
        return None

    def load(self) -> MOVRConfig:
        """
        Load configuration from file and environment.

        Returns:
            MOVRConfig instance
        """
        if self._config is not None:
            return self._config

        # Start with defaults
        config_dict = {}

        # Load from file if exists
        if self.config_path and self.config_path.exists():
            with open(self.config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    config_dict.update(file_config)

        # Override with environment variables
        env_overrides = self._load_env_vars()
        if env_overrides:
            config_dict.update(env_overrides)

        # Validate and create config
        self._config = MOVRConfig(**config_dict)

        # Resolve relative paths to absolute paths based on project root
        # Project root is the parent of the config directory
        if self.config_path:
            project_root = self.config_path.resolve().parent.parent
        else:
            project_root = Path.cwd()
        self._config.paths = self._config.paths.resolve_paths(project_root)

        return self._config

    def _load_env_vars(self) -> dict:
        """Load configuration from environment variables."""
        env_config = {}

        # Data directory
        if data_dir := os.getenv("MOVR_DATA_DIR"):
            env_config.setdefault("paths", {})["data_dir"] = data_dir

        # Output directory
        if output_dir := os.getenv("MOVR_OUTPUT_DIR"):
            env_config.setdefault("paths", {})["output_dir"] = output_dir

        # Strictness mode
        if strictness := os.getenv("MOVR_STRICTNESS"):
            env_config.setdefault("wrangling", {})["strictness"] = strictness

        # Debug mode
        if debug := os.getenv("MOVR_DEBUG"):
            env_config["debug"] = debug.lower() in ("true", "1", "yes")

        return env_config

    def reload(self) -> MOVRConfig:
        """Reload configuration from file."""
        self._config = None
        return self.load()


# Global config instance
_global_config: Optional[MOVRConfig] = None


def get_config(config_path: Optional[Path] = None, reload: bool = False) -> MOVRConfig:
    """
    Get global configuration instance.

    Args:
        config_path: Optional path to config file
        reload: Force reload from file

    Returns:
        MOVRConfig instance
    """
    global _global_config

    if _global_config is None or reload:
        loader = ConfigLoader(config_path)
        _global_config = loader.load()

    return _global_config
