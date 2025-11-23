"""
Plugin system for custom transformation functions.

Allows users to write custom Python functions for complex wrangling logic.
"""

import importlib.util
from pathlib import Path
from typing import Dict, Callable, Any
from loguru import logger


# Global plugin registry
_PLUGIN_REGISTRY: Dict[str, Callable] = {}


def register_plugin(name: str):
    """
    Decorator to register a plugin function.

    Usage:
        @register_plugin("my_transform")
        def my_transform(df, **kwargs):
            # Your logic here
            return df
    """
    def decorator(func: Callable):
        _PLUGIN_REGISTRY[name] = func
        logger.debug(f"Registered plugin: {name}")
        return func
    return decorator


class PluginLoader:
    """Load and manage data wrangling plugins."""

    def __init__(self, plugin_dir: Path = None):
        """
        Initialize plugin loader.

        Args:
            plugin_dir: Directory containing plugin Python files
        """
        self.plugin_dir = plugin_dir or Path("plugins")
        self.loaded_modules: Dict[str, Any] = {}

    def load_plugin(self, plugin_path: str) -> Callable:
        """
        Load a plugin function by import path.

        Args:
            plugin_path: Import path like "plugins.my_transform.transform_func"

        Returns:
            Callable plugin function
        """
        # Check if already registered
        if plugin_path in _PLUGIN_REGISTRY:
            return _PLUGIN_REGISTRY[plugin_path]

        # Try to import from path
        parts = plugin_path.split('.')
        if len(parts) < 2:
            raise ValueError(f"Invalid plugin path: {plugin_path}")

        module_path = '.'.join(parts[:-1])
        function_name = parts[-1]

        # Try standard import first
        try:
            module = importlib.import_module(module_path)
            func = getattr(module, function_name)
            logger.info(f"Loaded plugin: {plugin_path}")
            return func
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load plugin {plugin_path}: {e}")
            raise

    def discover_plugins(self) -> Dict[str, Callable]:
        """
        Discover all plugins in plugin directory.

        Returns:
            Dict of discovered plugins
        """
        if not self.plugin_dir.exists():
            logger.warning(f"Plugin directory not found: {self.plugin_dir}")
            return {}

        plugins = {}

        for py_file in self.plugin_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            try:
                # Load module
                spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                self.loaded_modules[py_file.stem] = module
                logger.info(f"Discovered plugins in: {py_file.name}")

            except Exception as e:
                logger.warning(f"Failed to load plugin file {py_file}: {e}")

        # Return registered plugins
        plugins.update(_PLUGIN_REGISTRY)
        return plugins
