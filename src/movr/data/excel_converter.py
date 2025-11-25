"""
Excel to Parquet conversion with audit logging.

Handles multi-sheet Excel files and converts them to efficient Parquet format.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
from datetime import datetime

from movr.config import get_config
from movr.data.audit import AuditLogger


class ExcelConverter:
    """Convert Excel files to Parquet with audit logging."""

    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        """
        Initialize Excel converter.

        Args:
            audit_logger: Optional audit logger instance
        """
        self.config = get_config()
        self.audit = audit_logger or AuditLogger()

    def convert_file(
        self,
        excel_path: Path,
        sheet_mappings: Dict[str, str],
        skip_sheets: Optional[List[str]] = None,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Path]:
        """
        Convert Excel file to Parquet files.

        Args:
            excel_path: Path to Excel file
            sheet_mappings: Dict mapping sheet names to table names
            skip_sheets: Optional list of sheets to skip
            output_dir: Optional output directory (default: data/parquet)

        Returns:
            Dict mapping table names to Parquet file paths
        """
        excel_path = Path(excel_path)
        if not excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")

        skip_sheets = skip_sheets or []
        output_dir = output_dir or self.config.paths.parquet_dir
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Converting Excel file: {excel_path}")

        # Read Excel file
        excel_file = pd.ExcelFile(excel_path)
        results = {}
        conversion_start = datetime.now()

        for sheet_name, table_name in sheet_mappings.items():
            if sheet_name in skip_sheets:
                logger.info(f"Skipping sheet: {sheet_name}")
                continue

            if sheet_name not in excel_file.sheet_names:
                logger.warning(f"Sheet not found in Excel file: {sheet_name}")
                continue

            # Read sheet
            logger.info(f"Reading sheet: {sheet_name} → {table_name}")
            df = pd.read_excel(excel_file, sheet_name=sheet_name)

            # Basic info
            n_rows = len(df)
            n_cols = len(df.columns)
            logger.info(f"  Rows: {n_rows:,}, Columns: {n_cols}")

            # Write to Parquet
            output_path = output_dir / f"{table_name}.parquet"
            df.to_parquet(output_path, index=False, compression='snappy')

            # Get file size
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"  Written to: {output_path} ({file_size_mb:.2f} MB)")

            # Audit log
            self.audit.log_conversion(
                source=excel_path,
                sheet=sheet_name,
                table=table_name,
                rows=n_rows,
                columns=list(df.columns),
                output_path=output_path,
                file_size_mb=file_size_mb
            )

            results[table_name] = output_path

        conversion_end = datetime.now()
        duration = (conversion_end - conversion_start).total_seconds()

        logger.success(
            f"Conversion complete: {len(results)} tables in {duration:.1f}s"
        )

        return results

    def convert_all_sources(self, clean_existing: bool = False) -> Dict[str, Path]:
        """
        Convert all data sources defined in config.

        Args:
            clean_existing: If True, remove all existing Parquet files before conversion

        Returns:
            Dict mapping table names to Parquet file paths
        """
        output_dir = Path(self.config.paths.parquet_dir)

        # Clean existing Parquet files if requested
        if clean_existing and output_dir.exists():
            existing_files = list(output_dir.glob("*.parquet"))
            if existing_files:
                logger.info(f"Cleaning {len(existing_files)} existing Parquet files...")
                for file in existing_files:
                    file.unlink()
                    logger.debug(f"  Removed: {file.name}")

        all_results = {}

        for source in self.config.data_sources:
            logger.info(f"Converting data source: {source.name}")
            results = self.convert_file(
                excel_path=Path(source.excel_path),
                sheet_mappings=source.sheet_mappings,
                skip_sheets=source.skip_sheets
            )
            all_results.update(results)

        return all_results
