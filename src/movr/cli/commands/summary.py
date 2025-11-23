"""Summary statistics command."""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import pandas as pd
from loguru import logger
from datetime import datetime
from typing import Optional, Dict, List
import warnings

from movr.data import load_data
from movr.config import get_config

console = Console()


class SummaryReporter:
    """Generate summary statistics reports."""

    def __init__(self, registry: str = "datahub"):
        """
        Initialize summary reporter.

        Args:
            registry: Which registry to report on (datahub, usndr, all)
        """
        self.registry = registry
        self.tables = None
        self.demographics = None
        self.encounter = None
        self.diagnosis = None

    def load_data(self):
        """Load required tables."""
        try:
            self.tables = load_data()
            self.demographics = self.tables.get("demographics_maindata")
            self.encounter = self.tables.get("encounter_maindata")
            self.diagnosis = self.tables.get("diagnosis_maindata")

            if self.demographics is None:
                raise ValueError("Demographics table not found")
            if self.encounter is None:
                raise ValueError("Encounter table not found")

            return True
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return False

    def filter_by_registry(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter data by registry if registry column exists."""
        # Check for actual field name first, then fallbacks
        registry_col = None
        for col in ["usndr", "REGISTRY", "DATA_SOURCE", "SOURCE"]:
            if col in df.columns:
                registry_col = col
                break

        if registry_col is None:
            return df

        if self.registry == "datahub":
            # For usndr field: assume empty/null/0 = DataHub, 1/Yes = USNDR
            if registry_col == "usndr":
                return df[(df[registry_col].isna()) | (df[registry_col] == 0) | (df[registry_col] == "")]
            else:
                return df[df[registry_col].astype(str).str.upper().str.contains("MOVR|DATAHUB", na=False)]
        elif self.registry == "usndr":
            if registry_col == "usndr":
                return df[(df[registry_col].notna()) & (df[registry_col] != 0) & (df[registry_col] != "")]
            else:
                return df[df[registry_col].astype(str).str.upper().str.contains("USNDR", na=False)]
        else:  # all
            return df

    def get_enrollment_by_disease(self) -> Dict[str, int]:
        """Get participant enrollment counts by disease."""
        df = self.filter_by_registry(self.demographics)

        # Check for disease column (actual field name first)
        disease_col = None
        for col in ["dstype", "DISEASE", "DIAGNOSIS", "PRIMARY_DIAGNOSIS"]:
            if col in df.columns:
                disease_col = col
                break

        if disease_col is None:
            return {}

        # Count unique participants per disease
        disease_counts = df.groupby(disease_col)["FACPATID"].nunique().to_dict()
        return disease_counts

    def get_annual_recruitment(self) -> pd.DataFrame:
        """Get annual recruitment by disease."""
        df = self.filter_by_registry(self.demographics)

        # Check for disease column
        disease_col = None
        for col in ["dstype", "DISEASE", "DIAGNOSIS"]:
            if col in df.columns:
                disease_col = col
                break

        # Check for enrollment date column (actual field name first)
        date_col = None
        for col in ["enroldt", "ENROLLMENT_DATE", "ENROLL_DATE", "CONSENT_DATE", "FIRST_VISIT_DATE"]:
            if col in df.columns:
                date_col = col
                break

        if disease_col is None or date_col is None:
            return pd.DataFrame()

        df = df.copy()
        # Suppress UserWarning about date format inference
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            df["ENROLLMENT_DATE"] = pd.to_datetime(df[date_col], errors="coerce")
        df["ENROLLMENT_YEAR"] = df["ENROLLMENT_DATE"].dt.year

        # Count enrollments by year and disease
        recruitment = df.groupby(["ENROLLMENT_YEAR", disease_col])["FACPATID"].nunique().reset_index()
        recruitment.columns = ["Year", "Disease", "Participants"]

        return recruitment

    def get_encounter_summary(self) -> Dict[str, any]:
        """Get total encounter counts overall and by year."""
        df = self.filter_by_registry(self.encounter)

        # Check for encounter date column (actual field name first)
        date_col = None
        for col in ["encntdt", "ENCOUNTER_DATE", "VISIT_DATE", "CASE_DATE", "DATE"]:
            if col in df.columns:
                date_col = col
                break

        if date_col is None:
            return {}

        df = df.copy()
        # Suppress UserWarning about date format inference
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            df["ENCOUNTER_DATE"] = pd.to_datetime(df[date_col], errors="coerce")
        df["ENCOUNTER_YEAR"] = df["ENCOUNTER_DATE"].dt.year

        total_encounters = len(df)
        encounters_by_year = df.groupby("ENCOUNTER_YEAR").size().to_dict()

        return {
            "total": total_encounters,
            "by_year": encounters_by_year
        }

    def get_encounters_by_disease_year(self) -> pd.DataFrame:
        """Get encounter counts by disease and year."""
        # Merge demographics (for disease) with encounters
        demographics_df = self.filter_by_registry(self.demographics)
        encounter_df = self.filter_by_registry(self.encounter)

        # Check for disease column
        disease_col = None
        for col in ["dstype", "DISEASE", "DIAGNOSIS"]:
            if col in demographics_df.columns:
                disease_col = col
                break

        if disease_col is None:
            return pd.DataFrame()

        # Drop disease column from encounter if it exists (we want demographics version)
        encounter_cols_to_merge = encounter_df.columns.tolist()
        if disease_col in encounter_cols_to_merge:
            encounter_df = encounter_df.drop(columns=[disease_col])

        merged = encounter_df.merge(
            demographics_df[["FACPATID", disease_col]],
            on="FACPATID",
            how="left"
        )

        # Check for encounter date column
        date_col = None
        for col in ["encntdt", "ENCOUNTER_DATE", "VISIT_DATE", "CASE_DATE", "DATE"]:
            if col in merged.columns:
                date_col = col
                break

        if date_col is None:
            return pd.DataFrame()

        merged = merged.copy()
        # Suppress UserWarning about date format inference
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            merged["ENCOUNTER_DATE"] = pd.to_datetime(merged[date_col], errors="coerce")
        merged["ENCOUNTER_YEAR"] = merged["ENCOUNTER_DATE"].dt.year

        # Count encounters by disease and year
        summary = merged.groupby([disease_col, "ENCOUNTER_YEAR"]).size().reset_index()
        summary.columns = ["Disease", "Year", "Encounters"]

        return summary

    def get_avg_encounters_per_participant_disease(self) -> pd.DataFrame:
        """Get average encounters per participant by disease (overall)."""
        demographics_df = self.filter_by_registry(self.demographics)
        encounter_df = self.filter_by_registry(self.encounter)

        # Check for disease column
        disease_col = None
        for col in ["dstype", "DISEASE", "DIAGNOSIS"]:
            if col in demographics_df.columns:
                disease_col = col
                break

        if disease_col is None:
            return pd.DataFrame()

        # Drop disease column from encounter if it exists (we want demographics version)
        if disease_col in encounter_df.columns:
            encounter_df = encounter_df.drop(columns=[disease_col])

        merged = encounter_df.merge(
            demographics_df[["FACPATID", disease_col]],
            on="FACPATID",
            how="left"
        )

        # Count encounters per participant
        encounters_per_patient = merged.groupby(["FACPATID", disease_col]).size().reset_index()
        encounters_per_patient.columns = ["FACPATID", "Disease", "Encounters"]

        # Average by disease
        avg_by_disease = encounters_per_patient.groupby("Disease")["Encounters"].mean().reset_index()
        avg_by_disease.columns = ["Disease", "Avg Encounters/Participant"]
        avg_by_disease["Avg Encounters/Participant"] = avg_by_disease["Avg Encounters/Participant"].round(2)

        return avg_by_disease

    def get_avg_encounters_per_participant_disease_year(self) -> pd.DataFrame:
        """Get average encounters per participant by disease and year."""
        demographics_df = self.filter_by_registry(self.demographics)
        encounter_df = self.filter_by_registry(self.encounter)

        # Check for disease column
        disease_col = None
        for col in ["dstype", "DISEASE", "DIAGNOSIS"]:
            if col in demographics_df.columns:
                disease_col = col
                break

        if disease_col is None:
            return pd.DataFrame()

        # Drop disease column from encounter if it exists (we want demographics version)
        if disease_col in encounter_df.columns:
            encounter_df = encounter_df.drop(columns=[disease_col])

        merged = encounter_df.merge(
            demographics_df[["FACPATID", disease_col]],
            on="FACPATID",
            how="left"
        )

        # Check for encounter date column
        date_col = None
        for col in ["encntdt", "ENCOUNTER_DATE", "VISIT_DATE", "CASE_DATE", "DATE"]:
            if col in merged.columns:
                date_col = col
                break

        if date_col is None:
            return pd.DataFrame()

        merged = merged.copy()
        # Suppress UserWarning about date format inference
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            merged["ENCOUNTER_DATE"] = pd.to_datetime(merged[date_col], errors="coerce")
        merged["ENCOUNTER_YEAR"] = merged["ENCOUNTER_DATE"].dt.year

        # Count encounters per participant per year
        encounters_per_patient_year = merged.groupby(["FACPATID", disease_col, "ENCOUNTER_YEAR"]).size().reset_index()
        encounters_per_patient_year.columns = ["FACPATID", "Disease", "Year", "Encounters"]

        # Average by disease and year
        avg_by_disease_year = encounters_per_patient_year.groupby(["Disease", "Year"])["Encounters"].mean().reset_index()
        avg_by_disease_year.columns = ["Disease", "Year", "Avg Encounters/Participant"]
        avg_by_disease_year["Avg Encounters/Participant"] = avg_by_disease_year["Avg Encounters/Participant"].round(2)

        return avg_by_disease_year


def run_summary(registry: str = "datahub", metric: str = "all"):
    """
    Run summary statistics report.

    Args:
        registry: Which registry (datahub, usndr, all)
        metric: Which metric to show (enrollment, recruitment, encounters, rates, all)
    """
    console.print(f"\n[bold blue]MOVR Summary Statistics[/bold blue]")

    registry_name = {
        "datahub": "MOVR DataHub",
        "usndr": "USNDR",
        "all": "All Registries"
    }.get(registry, registry)

    console.print(f"[dim]Registry: {registry_name}[/dim]")
    console.print(f"[dim]Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n")

    # Initialize reporter
    reporter = SummaryReporter(registry=registry)

    # Load data
    console.print("[cyan]Loading data...[/cyan]")
    if not reporter.load_data():
        console.print("[red]Failed to load data. Run 'movr convert' first.[/red]")
        return

    # Show enrollment by disease
    if metric in ["enrollment", "all"]:
        console.print("\n[bold] Enrollment by Disease[/bold]")
        enrollment = reporter.get_enrollment_by_disease()

        if enrollment:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Disease", style="cyan")
            table.add_column("Participants", justify="right", style="green")

            total = 0
            for disease, count in sorted(enrollment.items()):
                table.add_row(disease, f"{count:,}")
                total += count

            table.add_row("", "", style="dim")
            table.add_row("[bold]TOTAL[/bold]", f"[bold]{total:,}[/bold]")

            console.print(table)
        else:
            console.print("[yellow]No enrollment data available[/yellow]")

    # Show annual recruitment
    if metric in ["recruitment", "all"]:
        console.print("\n[bold] Annual Recruitment by Disease[/bold]")
        recruitment = reporter.get_annual_recruitment()

        if not recruitment.empty:
            # Pivot for better display
            pivot = recruitment.pivot(index="Disease", columns="Year", values="Participants").fillna(0).astype(int)

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Disease", style="cyan")

            for year in sorted(pivot.columns):
                table.add_column(str(int(year)), justify="right")

            for disease in pivot.index:
                row_data = [disease] + [f"{int(pivot.loc[disease, year]):,}" for year in sorted(pivot.columns)]
                table.add_row(*row_data)

            console.print(table)
        else:
            console.print("[yellow]No recruitment data available[/yellow]")

    # Show encounter summary
    if metric in ["encounters", "all"]:
        console.print("\n[bold] Encounter Summary[/bold]")
        encounter_summary = reporter.get_encounter_summary()

        if encounter_summary:
            console.print(f"[cyan]Total Encounters:[/cyan] {encounter_summary.get('total', 0):,}")

            if encounter_summary.get("by_year"):
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Year", style="cyan")
                table.add_column("Encounters", justify="right", style="green")

                for year, count in sorted(encounter_summary["by_year"].items()):
                    if pd.notna(year):
                        table.add_row(str(int(year)), f"{count:,}")

                console.print("\n[dim]Encounters by Year:[/dim]")
                console.print(table)

        # Encounters by disease and year
        console.print("\n[dim]Encounters by Disease and Year:[/dim]")
        encounters_by_disease = reporter.get_encounters_by_disease_year()

        if not encounters_by_disease.empty:
            pivot = encounters_by_disease.pivot(index="Disease", columns="Year", values="Encounters").fillna(0).astype(int)

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Disease", style="cyan")

            for year in sorted(pivot.columns):
                if pd.notna(year):
                    table.add_column(str(int(year)), justify="right")

            for disease in pivot.index:
                row_data = [disease] + [f"{int(pivot.loc[disease, year]):,}" for year in sorted(pivot.columns) if pd.notna(year)]
                table.add_row(*row_data)

            console.print(table)
        else:
            console.print("[yellow]No encounter data by disease available[/yellow]")

    # Show average encounters per participant
    if metric in ["rates", "all"]:
        console.print("\n[bold] Average Encounters per Participant by Disease[/bold]")
        avg_encounters = reporter.get_avg_encounters_per_participant_disease()

        if not avg_encounters.empty:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Disease", style="cyan")
            table.add_column("Avg Encounters/Participant", justify="right", style="green")

            for _, row in avg_encounters.iterrows():
                table.add_row(row["Disease"], f"{row['Avg Encounters/Participant']:.2f}")

            console.print(table)
        else:
            console.print("[yellow]No data available[/yellow]")

        # By year
        console.print("\n[dim]Average Encounters per Participant by Disease and Year:[/dim]")
        avg_by_year = reporter.get_avg_encounters_per_participant_disease_year()

        if not avg_by_year.empty:
            pivot = avg_by_year.pivot(index="Disease", columns="Year", values="Avg Encounters/Participant").fillna(0)

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Disease", style="cyan")

            for year in sorted(pivot.columns):
                if pd.notna(year):
                    table.add_column(str(int(year)), justify="right")

            for disease in pivot.index:
                row_data = [disease] + [f"{pivot.loc[disease, year]:.2f}" for year in sorted(pivot.columns) if pd.notna(year)]
                table.add_row(*row_data)

            console.print(table)
        else:
            console.print("[yellow]No data available[/yellow]")

    console.print("\n[green]✓ Summary complete[/green]\n")
