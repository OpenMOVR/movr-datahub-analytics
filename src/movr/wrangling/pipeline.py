"""
Data wrangling pipeline orchestration.

Executes transformation rules defined in YAML configuration.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

from movr.config import get_config
from movr.wrangling.rules import RuleInterpreter
from movr.wrangling.plugins import PluginLoader
from movr.data.audit import AuditLogger


class WranglingPipeline:
    """Execute data wrangling rules on tables."""

    def __init__(
        self,
        rules_file: Optional[Path] = None,
        strictness: Optional[str] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize wrangling pipeline.

        Args:
            rules_file: Path to YAML rules file
            strictness: Override strictness mode (strict/permissive/interactive)
            audit_logger: Optional audit logger
        """
        self.config = get_config()
        self.rules_file = rules_file or Path("config/wrangling_rules.yaml")
        self.strictness = strictness or self.config.wrangling.strictness
        self.audit = audit_logger or AuditLogger()

        self.rules = RuleInterpreter(self.rules_file)
        self.plugins = PluginLoader()

    def execute(self, tables: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Execute all wrangling rules on tables.

        Args:
            tables: Dict mapping table names to DataFrames

        Returns:
            Dict of cleaned DataFrames
        """
        logger.info(f"Starting wrangling pipeline in {self.strictness} mode")
        results = tables.copy()

        for rule in self.rules.get_rules():
            rule_name = rule.get('name', 'unnamed')
            tables_to_process = self._get_tables_for_rule(rule, results.keys())

            if not tables_to_process:
                continue

            logger.info(f"Applying rule: {rule_name}")

            for table_name in tables_to_process:
                try:
                    df = results[table_name]
                    rows_before = len(df)

                    # Apply rule
                    df_clean = self._apply_rule(rule, df, table_name)
                    rows_after = len(df_clean)

                    results[table_name] = df_clean

                    # Audit log
                    self.audit.log_transformation(
                        table=table_name,
                        rule_name=rule_name,
                        rows_before=rows_before,
                        rows_after=rows_after,
                        details={'rule': rule}
                    )

                    if rows_before != rows_after:
                        logger.info(
                            f"  {table_name}: {rows_before:,} → {rows_after:,} rows "
                            f"({rows_before - rows_after:,} removed)"
                        )

                except Exception as e:
                    self._handle_error(rule_name, table_name, e)

        logger.success("Wrangling pipeline complete")
        return results

    def _get_tables_for_rule(self, rule: dict, available_tables) -> list:
        """Determine which tables a rule applies to."""
        rule_tables = rule.get('tables', [])

        if 'all' in rule_tables or rule_tables == ['all']:
            return list(available_tables)

        return [t for t in rule_tables if t in available_tables]

    def _apply_rule(self, rule: dict, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Apply a single rule to a DataFrame."""
        action = rule.get('action')

        if action == 'drop_duplicates':
            subset = rule.get('subset', None)
            keep = rule.get('keep', 'first')
            return df.drop_duplicates(subset=subset, keep=keep)

        elif action == 'parse_dates':
            columns = rule.get('columns', [])
            formats = rule.get('formats', ['%Y-%m-%d'])
            on_error = rule.get('on_error', 'coerce')

            for col in columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors=on_error)
            return df

        elif action == 'replace_missing':
            values = rule.get('values', [])
            replace_with = rule.get('replace_with', None)
            return df.replace(values, replace_with)

        elif action == 'enforce_dtype':
            columns = rule.get('columns', [])
            dtype = rule.get('dtype', 'string')

            for col in columns:
                if col in df.columns:
                    df[col] = df[col].astype(dtype)
            return df

        elif action == 'validate_range':
            column = rule.get('column')
            min_val = rule.get('min')
            max_val = rule.get('max')
            on_error = rule.get('on_error', 'flag')

            if column in df.columns:
                out_of_range = (df[column] < min_val) | (df[column] > max_val)

                if on_error == 'flag':
                    df[f'{column}_OUT_OF_RANGE'] = out_of_range
                elif on_error == 'drop':
                    df = df[~out_of_range]
                elif on_error == 'raise' and out_of_range.any():
                    raise ValueError(f"{out_of_range.sum()} values out of range in {column}")

            return df

        elif action == 'plugin':
            plugin_path = rule.get('plugin')
            plugin_func = self.plugins.load_plugin(plugin_path)
            kwargs = {k: v for k, v in rule.items() if k not in ['name', 'tables', 'action', 'plugin']}
            return plugin_func(df, **kwargs)

        else:
            logger.warning(f"Unknown action: {action}")
            return df

    def _handle_error(self, rule_name: str, table_name: str, error: Exception):
        """Handle errors based on strictness mode."""
        if self.strictness == "strict":
            raise RuntimeError(f"Rule '{rule_name}' failed on {table_name}: {error}") from error
        elif self.strictness == "permissive":
            logger.warning(f"Rule '{rule_name}' failed on {table_name}: {error}")
        elif self.strictness == "interactive":
            response = input(f"Rule '{rule_name}' failed on {table_name}. Continue? [y/N]: ")
            if response.lower() != 'y':
                raise RuntimeError(f"Pipeline aborted by user") from error

    def get_cleaning_report(self) -> dict:
        """Get summary of cleaning operations."""
        return {
            'rules_applied': len(self.rules.get_rules()),
            'strictness': self.strictness,
            'audit_log': self.audit.session_log
        }
