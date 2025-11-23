"""
MOVR DataHub Analytics

Clinical data analytics framework for neuromuscular disease registries.
"""

__version__ = "0.1.0"

# High-level API exports
from movr.data import load_data
from movr.cohorts import CohortManager
from movr.analytics import DescriptiveAnalyzer
from movr.config import get_config

# Convenience functions
def setup(excel_files=None, config_path=None):
    """
    Interactive setup wizard for first-time users.

    Args:
        excel_files: List of Excel file paths (optional)
        config_path: Path to config file (optional)
    """
    from movr.cli.commands.setup import setup_wizard
    return setup_wizard(excel_files=excel_files, config_path=config_path)


__all__ = [
    "__version__",
    "load_data",
    "CohortManager",
    "DescriptiveAnalyzer",
    "get_config",
    "setup",
]
