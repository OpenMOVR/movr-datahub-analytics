"""Data validation command."""

from rich.console import Console
from movr.data import load_data
from movr.cohorts import EnrollmentValidator

console = Console()


def run_validate(strictness='permissive'):
    """Run data validation."""
    console.print("\n[bold blue]Validating MOVR data...[/bold blue]\n")

    try:
        # Load data
        console.print("Loading data...")
        tables = load_data(verbose=False)
        console.print(f"[green]✓ Loaded {len(tables)} tables[/green]\n")

        # Validate enrollment
        console.print("Validating enrollment...")
        validator = EnrollmentValidator(tables)
        report = validator.validate_enrollment()

        console.print(f"\n[bold]Enrollment Summary:[/bold]")
        console.print(f"  Total patients: {report['total_unique_patients']}")
        console.print(f"  Enrolled: {report['enrolled_count']}")

        console.print(f"\n[bold]Form Coverage:[/bold]")
        for form_name, count in report['form_counts'].items():
            console.print(f"  {form_name}: {count} patients")

        console.print(f"\n[bold]Missing Forms:[/bold]")
        for form_name, count in report['missing_by_form'].items():
            if count > 0:
                console.print(f"  {form_name}: [yellow]{count} patients missing[/yellow]")

        console.print("\n[green]✓ Validation complete[/green]\n")

    except Exception as e:
        console.print(f"\n[red]✗ Validation failed: {e}[/red]\n")
