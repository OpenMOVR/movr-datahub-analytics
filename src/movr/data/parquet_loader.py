
"""
Parquet file loader with caching support.

Provides efficient loading of Parquet files with optional caching.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional, List
from loguru import logger
from datetime import datetime

from movr.config import get_config


class ParquetLoader:
    """Load Parquet files with optional caching."""

    def __init__(self, cache_enabled: bool = True, verbose: bool = True):
        """
        Initialize Parquet loader.

        Args:
            cache_enabled: Enable in-memory caching of loaded tables
            verbose: Enable verbose logging
        """
        self.config = get_config()
        self.cache_enabled = cache_enabled
        self.verbose = verbose
        self._cache: Dict[str, pd.DataFrame] = {}
        self.load_history: List[dict] = []

    def load_table(self, table_name: str, force_reload: bool = False) -> pd.DataFrame:
        """
        Load a single Parquet table.

        Args:
            table_name: Name of the table to load
            force_reload: Force reload even if cached

        Returns:
            DataFrame
        """
        # Check cache
        if self.cache_enabled and not force_reload and table_name in self._cache:
            if self.verbose:
                logger.info(f"Loading {table_name} from cache")
            return self._cache[table_name]

        # Find Parquet file
        parquet_path = self.config.paths.parquet_dir / f"{table_name}.parquet"

        if not parquet_path.exists():
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")

        # Load
        start_time = datetime.now()
        df = pd.read_parquet(parquet_path)
        load_time = (datetime.now() - start_time).total_seconds()

        # Log stats
        file_size_mb = parquet_path.stat().st_size / (1024 * 1024)
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

        if self.verbose:
            logger.info(
                f"Loaded {table_name}: "
                f"{len(df):,} rows, {len(df.columns)} cols, "
                f"{file_size_mb:.2f} MB on disk, {memory_mb:.2f} MB in memory, "
                f"{load_time:.2f}s"
            )

        # Record load history
        self.load_history.append({
            'table_name': table_name,
            'timestamp': datetime.now(),
            'rows': len(df),
            'columns': len(df.columns),
            'file_size_mb': file_size_mb,
            'memory_mb': memory_mb,
            'load_time_sec': load_time
        })

        # Cache if enabled
        if self.cache_enabled:
            self._cache[table_name] = df

        return df

    def load_all(
        self,
        table_names: Optional[List[str]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Load multiple tables.

        Args:
            table_names: Optional list of table names. If None, loads all available.

        Returns:
            Dict mapping table names to DataFrames
        """
        if table_names is None:
            # Find all Parquet files
            parquet_dir = self.config.paths.parquet_dir
            if not parquet_dir.exists():
                raise FileNotFoundError(f"Parquet directory not found: {parquet_dir}")

            parquet_files = list(parquet_dir.glob("*.parquet"))
            table_names = [f.stem for f in parquet_files]

        tables = {}
        for table_name in table_names:
            try:
                tables[table_name] = self.load_table(table_name)
            except FileNotFoundError as e:
                logger.warning(f"Skipping {table_name}: {e}")
                continue

        logger.success(f"Loaded {len(tables)} tables")
        return tables

    def clear_cache(self):
        """Clear the in-memory cache."""
        self._cache.clear()
        logger.info("Cache cleared")

    def get_load_summary(self) -> pd.DataFrame:
        """
        Get summary of all loads performed.

        Returns:
            DataFrame with load statistics
        """
        if not self.load_history:
            return pd.DataFrame()

        return pd.DataFrame(self.load_history)


def load_data(
    table_names: Optional[List[str]] = None,
    config_path: Optional[Path] = None,
    verbose: bool = True
) -> Dict[str, pd.DataFrame]:
    """
    Convenience function to load MOVR data.

    Args:
        table_names: Optional list of specific tables to load
        config_path: Optional path to config file
        verbose: Enable verbose logging

    Returns:
        Dict mapping table names to DataFrames
    """
    if config_path:
        from movr.config import get_config
        get_config(config_path=config_path, reload=True)

    loader = ParquetLoader(verbose=verbose)
    return loader.load_all(table_names=table_names)
