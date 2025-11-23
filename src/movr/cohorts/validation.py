"""
Enrollment validation for MOVR cohorts.

Validates that participants have required forms for enrollment.
"""

import pandas as pd
from typing import Dict, List, Set
from loguru import logger


class EnrollmentValidator:
    """Validate participant enrollment based on required forms."""

    def __init__(self, tables: Dict[str, pd.DataFrame]):
        """
        Initialize enrollment validator.

        Args:
            tables: Dict mapping table names to DataFrames
        """
        self.tables = tables

    def get_enrolled_patients(
        self,
        required_forms: List[str] = None
    ) -> List[str]:
        """
        Get list of enrolled patients with all required forms.

        Args:
            required_forms: List of required table names

        Returns:
            List of FACPATID values for enrolled patients
        """
        if required_forms is None:
            required_forms = [
                "demographics_maindata",
                "diagnosis_maindata",
                "encounter_maindata"
            ]

        patient_sets = []

        for form_name in required_forms:
            if form_name not in self.tables:
                logger.warning(f"Required form not found: {form_name}")
                continue

            patients = set(self.tables[form_name]["FACPATID"].unique())
            patient_sets.append(patients)

        if not patient_sets:
            raise ValueError("No required forms found in tables")

        # Get intersection (patients with ALL required forms)
        enrolled = set.intersection(*patient_sets)

        logger.info(
            f"Enrollment validation: {len(enrolled)} patients with all {len(required_forms)} required forms"
        )

        return list(enrolled)

    def validate_enrollment(
        self,
        required_forms: List[str] = None
    ) -> Dict[str, any]:
        """
        Get detailed enrollment validation report.

        Args:
            required_forms: List of required table names

        Returns:
            Dict with enrollment statistics
        """
        if required_forms is None:
            required_forms = [
                "demographics_maindata",
                "diagnosis_maindata",
                "encounter_maindata"
            ]

        form_patients: Dict[str, Set[str]] = {}

        for form_name in required_forms:
            if form_name in self.tables:
                form_patients[form_name] = set(
                    self.tables[form_name]["FACPATID"].unique()
                )
            else:
                logger.warning(f"Form not found: {form_name}")
                form_patients[form_name] = set()

        # Get enrolled patients
        if form_patients:
            enrolled = set.intersection(*form_patients.values())
        else:
            enrolled = set()

        # Get patients missing each form
        all_patients = set.union(*form_patients.values()) if form_patients else set()
        missing_by_form = {}

        for form_name, patients in form_patients.items():
            missing_by_form[form_name] = list(all_patients - patients)

        report = {
            "enrolled_count": len(enrolled),
            "total_unique_patients": len(all_patients),
            "enrolled_patients": list(enrolled),
            "form_counts": {
                name: len(patients)
                for name, patients in form_patients.items()
            },
            "missing_by_form": {
                name: len(missing)
                for name, missing in missing_by_form.items()
            },
        }

        # Log summary
        logger.info(f"Enrollment Validation Report:")
        logger.info(f"  Total unique patients: {report['total_unique_patients']}")
        logger.info(f"  Enrolled patients: {report['enrolled_count']}")
        for form_name, count in report['form_counts'].items():
            logger.info(f"  {form_name}: {count} patients")

        return report
