"""
Base analyzer class and result containers.

Provides abstract base class for all analyzers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict
from pathlib import Path
import pandas as pd
from loguru import logger


@dataclass
class AnalysisResult:
    """Container for analysis results."""

    name: str
    summary: Dict[str, Any]
    data: pd.DataFrame
    metadata: Dict[str, Any]

    def to_excel(self, path: str):
        """Export results to Excel file."""
        with pd.ExcelWriter(path) as writer:
            # Write summary
            summary_df = pd.DataFrame([self.summary])
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

            # Write data
            self.data.to_excel(writer, sheet_name="Data", index=False)

            # Write metadata
            metadata_df = pd.DataFrame([self.metadata])
            metadata_df.to_excel(writer, sheet_name="Metadata", index=False)

        logger.info(f"Results exported to: {path}")

    def to_csv(self, path: str):
        """Export data to CSV file."""
        self.data.to_csv(path, index=False)
        logger.info(f"Data exported to: {path}")

    def to_json(self, path: str):
        """Export results to JSON file."""
        import json

        output = {
            "name": self.name,
            "summary": self.summary,
            "metadata": self.metadata,
            "data": self.data.to_dict(orient="records"),
        }

        with open(path, "w") as f:
            json.dump(output, f, indent=2, default=str)

        logger.info(f"Results exported to: {path}")


class BaseAnalyzer(ABC):
    """Abstract base class for analyzers."""

    def __init__(self, cohort: pd.DataFrame, tables: Dict[str, pd.DataFrame]):
        """
        Initialize analyzer.

        Args:
            cohort: DataFrame with FACPATID column
            tables: Dict mapping table names to DataFrames
        """
        self.cohort = cohort
        self.tables = tables

    @abstractmethod
    def run_analysis(self) -> AnalysisResult:
        """
        Execute the analysis.

        Returns:
            AnalysisResult instance
        """
        pass

    def _merge_with_demographics(self) -> pd.DataFrame:
        """Merge cohort with demographics table."""
        if "demographics_maindata" in self.tables:
            return self.cohort.merge(
                self.tables["demographics_maindata"],
                on="FACPATID",
                how="left"
            )
        else:
            logger.warning("demographics_maindata table not found")
            return self.cohort
