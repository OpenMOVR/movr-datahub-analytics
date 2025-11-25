"""
Audit logging for data operations.

Tracks conversions, transformations, and analyses for reproducibility.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger

from movr.config import get_config


class AuditLogger:
    """Log data operations for audit trail and reproducibility."""

    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize audit logger.

        Args:
            log_dir: Directory for audit logs (default from config)
        """
        config = get_config()
        self.log_dir = Path(log_dir) if log_dir else config.audit.log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.enabled = config.audit.enabled

        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log: List[Dict[str, Any]] = []

    def log_conversion(
        self,
        source: Path,
        sheet: str,
        table: str,
        rows: int,
        columns: List[str],
        output_path: Path,
        file_size_mb: float
    ):
        """
        Log Excel to Parquet conversion.

        Args:
            source: Source Excel file path
            sheet: Sheet name
            table: Table name
            rows: Number of rows
            columns: List of column names
            output_path: Output Parquet file path
            file_size_mb: File size in MB
        """
        if not self.enabled:
            return

        entry = {
            'operation': 'conversion',
            'timestamp': datetime.now().isoformat(),
            'source_file': str(source),
            'sheet_name': sheet,
            'table_name': table,
            'rows': rows,
            'columns': columns,
            'output_path': str(output_path),
            'file_size_mb': round(file_size_mb, 2)
        }

        self.session_log.append(entry)
        self._write_entry(entry)

    def log_transformation(
        self,
        table: str,
        rule_name: str,
        rows_before: int,
        rows_after: int,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log data transformation.

        Args:
            table: Table name
            rule_name: Name of transformation rule
            rows_before: Row count before transformation
            rows_after: Row count after transformation
            details: Optional additional details
        """
        if not self.enabled:
            return

        entry = {
            'operation': 'transformation',
            'timestamp': datetime.now().isoformat(),
            'table_name': table,
            'rule_name': rule_name,
            'rows_before': rows_before,
            'rows_after': rows_after,
            'rows_removed': rows_before - rows_after,
            'details': details or {}
        }

        self.session_log.append(entry)
        self._write_entry(entry)

    def log_analysis(
        self,
        analysis_type: str,
        cohort_name: str,
        n_patients: int,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Log analysis execution.

        Args:
            analysis_type: Type of analysis
            cohort_name: Name of cohort analyzed
            n_patients: Number of patients in cohort
            parameters: Optional analysis parameters
        """
        if not self.enabled:
            return

        entry = {
            'operation': 'analysis',
            'timestamp': datetime.now().isoformat(),
            'analysis_type': analysis_type,
            'cohort_name': cohort_name,
            'n_patients': n_patients,
            'parameters': parameters or {}
        }

        self.session_log.append(entry)
        self._write_entry(entry)

    def _write_entry(self, entry: Dict[str, Any]):
        """Write audit entry to log file."""
        log_file = self.log_dir / f"audit_{self.session_id}.jsonl"

        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def save_session_log(self, filename: Optional[str] = None):
        """
        Save complete session log to JSON file.

        Args:
            filename: Optional custom filename
        """
        if not self.session_log:
            logger.warning("No audit entries to save")
            return

        if filename is None:
            filename = f"audit_session_{self.session_id}.json"

        output_path = self.log_dir / filename

        with open(output_path, 'w') as f:
            json.dump({
                'session_id': self.session_id,
                'entries': self.session_log
            }, f, indent=2)

        logger.info(f"Audit log saved to: {output_path}")
        return output_path
