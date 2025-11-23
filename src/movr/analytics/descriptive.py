"""
Descriptive statistics analyzer.

Provides basic demographic and clinical summaries.
"""

import pandas as pd
from typing import Dict
from loguru import logger

from movr.analytics.base import BaseAnalyzer, AnalysisResult
from movr.cohorts.manager import FieldResolver
from datetime import datetime


class DescriptiveAnalyzer(BaseAnalyzer):
    """Compute descriptive statistics for a cohort.

    Accepts an optional CohortManager + cohort_name to use the centrally-prepared
    cohort data (which includes prepared demographics and derived AGE).
    If cohort_manager and cohort_name are provided, the analyzer will prefer
    CohortManager.get_cohort_data(name, include_demographics=True) over
    merging against raw `demographics_maindata` in `tables`.
    """

    def __init__(self, cohort: pd.DataFrame, tables: Dict[str, pd.DataFrame], cohort_manager=None, cohort_name: str = None):
        super().__init__(cohort=cohort, tables=tables)
        self.cohort_manager = cohort_manager
        self.cohort_name = cohort_name

    def run_analysis(self) -> AnalysisResult:
        """
        Run descriptive analysis.

        Returns:
            AnalysisResult with demographic and clinical summaries
        """
        logger.info("Running descriptive analysis...")

        # Prefer CohortManager-prepared cohort data (centralized preprocessing)
        data = None
        if self.cohort_manager is not None and self.cohort_name:
            try:
                data = self.cohort_manager.get_cohort_data(self.cohort_name, include_demographics=True)
            except Exception:
                data = None

        # Fallback: merge with demographics table
        if data is None:
            data = self._merge_with_demographics()

        # Compute summary statistics
        summary = {
            "n_patients": len(data),
        }

        # Use field resolver so we respect config mappings and fallback names
        resolver = FieldResolver()

        # Gender distribution
        gender_col = resolver.resolve("gender", data)
        if gender_col:
            gender_dist = data[gender_col].value_counts().to_dict()
            summary["gender_distribution"] = gender_dist
            summary["gender_counts"] = {k: int(v) for k, v in gender_dist.items()}
            # record actual column used
            summary.setdefault("columns_used", {})["gender"] = gender_col

        # Age statistics
        # Age can be a derived field — resolve via resolver
        age_col = resolver.resolve("age", data)
        # if age is derived, try to calculate from birth_date if not present
        if not age_col and resolver.is_derived("age"):
            bd_col = resolver.resolve("birth_date", data)
            if bd_col and bd_col in data.columns:
                try:
                    dob = pd.to_datetime(data[bd_col], errors="coerce")
                    today = datetime.now()
                    data["AGE"] = ((today - dob).dt.days / 365.25).round(1)
                    age_col = "AGE"
                except Exception:
                    age_col = None

        if age_col and age_col in data.columns:
            age_valid = data[age_col].dropna()
            summary["age_stats"] = {
                "n": int(len(age_valid)),
                "mean": float(age_valid.mean()),
                "median": float(age_valid.median()),
                "std": float(age_valid.std()),
                "min": float(age_valid.min()),
                "max": float(age_valid.max()),
                "q25": float(age_valid.quantile(0.25)),
                "q75": float(age_valid.quantile(0.75)),
            }

        # Disease distribution (canonical: disease -> dstype or equivalent)
        disease_col = resolver.resolve("disease", data)
        if disease_col:
            disease_dist = data[disease_col].value_counts().to_dict()
            summary["disease_distribution"] = {k: int(v) for k, v in disease_dist.items()}
            summary.setdefault("columns_used", {})["disease"] = disease_col

        # Enrollment source
        registry_col = resolver.resolve("registry", data)
        if registry_col:
            usndr_dist = data[registry_col].value_counts().to_dict()
            summary["usndr_distribution"] = {str(k): int(v) for k, v in usndr_dist.items()}
            summary.setdefault("columns_used", {})["registry"] = registry_col

        logger.success(f"Analyzed {summary['n_patients']} patients")

        return AnalysisResult(
            name="descriptive_statistics",
            summary=summary,
            data=data,
            metadata={
                "analyzer": "DescriptiveAnalyzer",
                "version": "1.0",
                    "tables_used": list(self.tables.keys()),
                    # expose which actual columns were used for canonical names
                    "columns_used": summary.get("columns_used", {}),
            }
        )
