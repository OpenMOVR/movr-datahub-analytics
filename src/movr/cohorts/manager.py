"""
Cohort management system.

Provides cohort creation, filtering, and validation with field resolution.
"""

import pandas as pd
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Callable, Any, List, Union
from loguru import logger

from movr.cohorts.validation import EnrollmentValidator
from movr.config import get_config


class FieldResolver:
    """Resolve canonical field names to actual column names."""

    # Default field mappings (used if config not available)
    DEFAULT_MAPPINGS = {
        "disease": "dstype",
        "registry": "usndr",
        "gender": "gender",
        "birth_date": "dob",
        "age": None,  # Derived field
        "patient_id": "FACPATID",
        "enrollment_date": "enroldt",
        "encounter_date": "encntdt",
    }

    def __init__(self, field_mappings_path: Optional[Path] = None):
        """
        Initialize field resolver.

        Args:
            field_mappings_path: Path to field_mappings.yaml
        """
        self._mappings = {}
        self._load_mappings(field_mappings_path)

    def _load_mappings(self, path: Optional[Path] = None):
        """Load field mappings from YAML file."""
        if path is None:
            # Try to find field_mappings.yaml
            try:
                config = get_config()
                # Look relative to config location
                config_dir = Path(__file__).parent.parent.parent.parent / "config"
                path = config_dir / "field_mappings.yaml"
            except Exception:
                path = Path("config/field_mappings.yaml")

        if path and path.exists():
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                if data and "fields" in data:
                    for canonical, info in data["fields"].items():
                        if isinstance(info, dict):
                            self._mappings[canonical] = info.get("source_field")
                        elif isinstance(info, list):
                            self._mappings[canonical] = info[0] if info else None
            logger.debug(f"Loaded field mappings from: {path}")
        else:
            logger.debug("Using default field mappings")

    def resolve(self, canonical_name: str, df: pd.DataFrame) -> Optional[str]:
        """
        Resolve canonical field name to actual column in DataFrame.

        Args:
            canonical_name: Canonical field name (e.g., "disease")
            df: DataFrame to check for columns

        Returns:
            Actual column name if found, None otherwise
        """
        # Check explicit mapping first
        mapped = self._mappings.get(canonical_name) or self.DEFAULT_MAPPINGS.get(canonical_name)

        if mapped and mapped in df.columns:
            return mapped

        # Try canonical name directly (case variations)
        for col in df.columns:
            if col.lower() == canonical_name.lower():
                return col

        # Try fallbacks from default mappings
        fallbacks = {
            "disease": ["dstype", "DISEASE", "DIAGNOSIS"],
            "registry": ["usndr", "REGISTRY", "DATA_SOURCE"],
            "gender": ["gender", "sex", "GENDER", "SEX"],
            "age": ["AGE", "age", "AGE_YEARS"],
        }

        for fallback in fallbacks.get(canonical_name, []):
            if fallback in df.columns:
                return fallback

        return None

    def is_derived(self, canonical_name: str) -> bool:
        """Check if field is derived (needs calculation)."""
        return canonical_name == "age"


class CohortManager:
    """Manage patient cohorts with filtering and validation."""

    def __init__(self, tables: Dict[str, pd.DataFrame]):
        """
        Initialize cohort manager.

        Args:
            tables: Dict mapping table names to DataFrames
        """
        self.tables = tables
        self._cohorts: Dict[str, pd.DataFrame] = {}
        self.validator = EnrollmentValidator(tables)
        self.field_resolver = FieldResolver()

        # Pre-calculate age if dob is available
        self._demographics_with_age = None
        self._prepare_demographics()

    def _prepare_demographics(self):
        """Prepare demographics table with derived fields like age."""
        if "demographics_maindata" not in self.tables:
            return

        df = self.tables["demographics_maindata"].copy()

        # Calculate age from dob if not present
        dob_col = self.field_resolver.resolve("birth_date", df)
        if dob_col and "AGE" not in df.columns:
            try:
                # Convert dob to datetime
                df[dob_col] = pd.to_datetime(df[dob_col], errors='coerce')
                today = datetime.now()
                df["AGE"] = ((today - df[dob_col]).dt.days / 365.25).round(1)
                logger.debug(f"Calculated AGE from {dob_col}")
            except Exception as e:
                logger.warning(f"Could not calculate age from {dob_col}: {e}")

        self._demographics_with_age = df

    def _get_demographics(self) -> pd.DataFrame:
        """Get demographics table with derived fields."""
        if self._demographics_with_age is not None:
            return self._demographics_with_age
        return self.tables.get("demographics_maindata", pd.DataFrame())

    def _resolve_filter_field(self, field: str, df: pd.DataFrame) -> Optional[str]:
        """Resolve a filter field name to actual column."""
        # Direct column match
        if field in df.columns:
            return field

        # Try field resolver
        resolved = self.field_resolver.resolve(field, df)
        if resolved:
            return resolved

        return None

    def _apply_registry_filter(self, df: pd.DataFrame, value: Any) -> pd.DataFrame:
        """
        Apply registry (USNDR/DataHub) filter.

        Args:
            df: DataFrame to filter
            value: True for USNDR, False for DataHub

        Returns:
            Filtered DataFrame
        """
        registry_col = self._resolve_filter_field("registry", df)
        if not registry_col:
            logger.warning("Registry field not found for filtering")
            return df

        if value is True or value == "usndr" or value == "USNDR":
            # USNDR: usndr == True
            return df[df[registry_col] == True]
        else:
            # DataHub: usndr is not True (None, NA, missing, False, etc.)
            return df[df[registry_col] != True]

    def create_base_cohort(
        self,
        name: str = "base",
        require_forms: Optional[List[str]] = None,
        validate_enrollment: bool = True
    ) -> pd.DataFrame:
        """
        Create base cohort with enrollment validation.

        Args:
            name: Cohort name
            require_forms: Required forms for enrollment
            validate_enrollment: Whether to validate enrollment

        Returns:
            DataFrame with FACPATID of enrolled participants
        """
        if require_forms is None:
            require_forms = [
                "demographics_maindata",
                "diagnosis_maindata",
                "encounter_maindata"
            ]

        if validate_enrollment:
            enrolled_patients = self.validator.get_enrolled_patients(
                required_forms=require_forms
            )
        else:
            # Just get unique patients from demographics
            if "demographics_maindata" in self.tables:
                enrolled_patients = list(
                    self.tables["demographics_maindata"]["FACPATID"].unique()
                )
            else:
                raise ValueError("demographics_maindata table not found")

        cohort = pd.DataFrame({"FACPATID": enrolled_patients})
        self._cohorts[name] = cohort

        logger.info(f"Created base cohort '{name}': {len(cohort)} patients")
        return cohort

    def filter_cohort(
        self,
        source_cohort: str,
        name: str,
        filters: Optional[Dict[str, Any]] = None,
        custom_filter: Optional[Callable] = None
    ) -> pd.DataFrame:
        """
        Create filtered cohort from existing cohort.

        Supports canonical field names that are resolved to actual columns:
        - disease -> dstype
        - registry -> usndr (True=USNDR, else=DataHub)
        - gender -> gender
        - age -> AGE (calculated from dob)

        Args:
            source_cohort: Name of source cohort
            name: New cohort name
            filters: Field-based filters using canonical names
                Examples:
                - {"disease": "DMD"} - exact match
                - {"disease": ["DMD", "BMD"]} - multiple values
                - {"age": {"min": 0, "max": 18}} - range filter
                - {"registry": True} - USNDR only
                - {"registry": False} - DataHub only
            custom_filter: Custom filter function

        Returns:
            Filtered cohort DataFrame
        """
        if source_cohort not in self._cohorts:
            raise ValueError(f"Source cohort not found: {source_cohort}")

        source = self._cohorts[source_cohort].copy()

        # Join with demographics (with age) for filtering
        demographics = self._get_demographics()
        if not demographics.empty:
            cohort = source.merge(demographics, on="FACPATID", how="left")
        else:
            cohort = source

        # Apply field filters
        if filters:
            for field, value in filters.items():
                # Special handling for registry filter
                if field == "registry":
                    cohort = self._apply_registry_filter(cohort, value)
                    continue

                # Resolve field name
                actual_field = self._resolve_filter_field(field, cohort)
                if not actual_field:
                    logger.warning(f"Filter field not found: {field}")
                    continue

                # Apply filter based on value type
                if isinstance(value, dict):
                    # Range filter: {"min": X, "max": Y}
                    if "min" in value:
                        cohort = cohort[cohort[actual_field] >= value["min"]]
                    if "max" in value:
                        cohort = cohort[cohort[actual_field] <= value["max"]]
                elif isinstance(value, tuple) and len(value) == 2:
                    # Legacy range filter: (min, max)
                    cohort = cohort[
                        (cohort[actual_field] >= value[0]) &
                        (cohort[actual_field] <= value[1])
                    ]
                elif isinstance(value, list):
                    # Multiple values
                    cohort = cohort[cohort[actual_field].isin(value)]
                else:
                    # Exact match
                    cohort = cohort[cohort[actual_field] == value]

        # Apply custom filter
        if custom_filter:
            cohort = cohort[custom_filter(cohort)]

        # Keep only FACPATID
        cohort = cohort[["FACPATID"]].drop_duplicates()
        self._cohorts[name] = cohort

        logger.info(
            f"Created cohort '{name}' from '{source_cohort}': "
            f"{len(cohort)} patients ({len(source) - len(cohort)} filtered out)"
        )

        return cohort

    def get_cohort(self, name: str) -> pd.DataFrame:
        """Get a cohort by name."""
        if name not in self._cohorts:
            raise ValueError(f"Cohort not found: {name}")
        return self._cohorts[name]

    def list_cohorts(self) -> List[str]:
        """List all cohort names."""
        return list(self._cohorts.keys())

    def get_cohort_data(
        self,
        name: str,
        include_demographics: bool = True
    ) -> pd.DataFrame:
        """
        Get cohort with demographic data.

        Args:
            name: Cohort name
            include_demographics: Include demographic columns

        Returns:
            DataFrame with FACPATID and optionally demographic data
        """
        cohort = self.get_cohort(name)

        if include_demographics:
            demographics = self._get_demographics()
            if not demographics.empty:
                return cohort.merge(demographics, on="FACPATID", how="left")

        return cohort

    def get_filtered_tables(
        self,
        name: str,
        tables: Optional[List[str]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Get all tables filtered to a cohort's FACPATIDs.

        This is the easiest way to get analysis-ready data for a cohort.
        Instead of manually filtering each table, this returns all tables
        with only the patients in your cohort.

        Args:
            name: Cohort name
            tables: Optional list of table names to filter. If None, filters all tables.

        Returns:
            Dict mapping table names to filtered DataFrames

        Example:
            >>> cohorts.filter_cohort('base', 'dmd', filters={'disease': 'DMD'})
            >>> filtered = cohorts.get_filtered_tables('dmd')
            >>> filtered['demographics_maindata']  # Only DMD patients
            >>> filtered['encounter_maindata']     # Only DMD encounters
        """
        cohort_ids = self.get_cohort(name)['FACPATID']
        tables_to_filter = tables or list(self.tables.keys())

        filtered = {}
        for table_name in tables_to_filter:
            if table_name not in self.tables:
                logger.warning(f"Table not found: {table_name}")
                continue

            df = self.tables[table_name]
            if 'FACPATID' in df.columns:
                filtered[table_name] = df[df['FACPATID'].isin(cohort_ids)].copy()
            else:
                # Table doesn't have FACPATID - include as-is with warning
                logger.debug(f"Table {table_name} has no FACPATID column, including unfiltered")
                filtered[table_name] = df.copy()

        logger.info(f"Filtered {len(filtered)} tables to cohort '{name}' ({len(cohort_ids)} patients)")
        return filtered

    def get_cohort_summary(self, name: str) -> dict:
        """
        Get summary statistics for cohort.

        Args:
            name: Cohort name

        Returns:
            Dict with summary statistics
        """
        cohort = self.get_cohort(name)
        demographics = self._get_demographics()

        if demographics.empty:
            return {"name": name, "n_patients": len(cohort)}

        # Merge with demographics
        merged = cohort.merge(demographics, on="FACPATID", how="left")

        # Resolve field names
        gender_col = self._resolve_filter_field("gender", merged)
        disease_col = self._resolve_filter_field("disease", merged)
        registry_col = self._resolve_filter_field("registry", merged)
        age_col = self._resolve_filter_field("age", merged)

        summary = {
            "name": name,
            "n_patients": len(cohort),
        }

        # Gender distribution
        if gender_col:
            summary["gender_distribution"] = merged[gender_col].value_counts().to_dict()

        # Age statistics
        if age_col and merged[age_col].notna().any():
            summary["age_stats"] = {
                "mean": round(merged[age_col].mean(), 1),
                "median": round(merged[age_col].median(), 1),
                "min": round(merged[age_col].min(), 1),
                "max": round(merged[age_col].max(), 1),
            }

        # Disease distribution
        if disease_col:
            summary["disease_distribution"] = merged[disease_col].value_counts().to_dict()

        # Registry distribution
        if registry_col:
            usndr_count = (merged[registry_col] == True).sum()
            datahub_count = len(merged) - usndr_count
            summary["registry_distribution"] = {
                "USNDR": int(usndr_count),
                "DataHub": int(datahub_count),
            }

        return summary

    def export_cohort(self, name: str, output_path: str):
        """
        Export cohort to file.

        Args:
            name: Cohort name
            output_path: Output file path (CSV, Excel, or Parquet)
        """
        cohort = self.get_cohort(name)

        if output_path.endswith('.csv'):
            cohort.to_csv(output_path, index=False)
        elif output_path.endswith('.xlsx'):
            cohort.to_excel(output_path, index=False)
        elif output_path.endswith('.parquet'):
            cohort.to_parquet(output_path, index=False)
        else:
            raise ValueError(f"Unsupported file format: {output_path}")

        logger.info(f"Exported cohort '{name}' to: {output_path}")
