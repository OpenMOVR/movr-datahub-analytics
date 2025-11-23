"""Status check command."""

from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()


def run_status():
    """Check and display project status."""
    console.print("\n[bold blue]MOVR DataHub Analytics - Status[/bold blue]\n")

    # Check config
    config_path = Path("config/config.yaml")
    config_status = "✓ Found" if config_path.exists() else "✗ Not found"
    console.print(f"Configuration: [{('green' if config_path.exists() else 'red')}]{config_status}[/]")

    # Check data directory
    data_dir = Path("data/parquet")
    if data_dir.exists():
        parquet_files = list(data_dir.glob("*.parquet"))
        console.print(f"Parquet files: [green]✓ {len(parquet_files)} files found[/green]")
    else:
        console.print(f"Parquet files: [yellow]✗ No data directory[/yellow]")

    # Check output directory
    output_dir = Path("output")
    output_status = "✓ Exists" if output_dir.exists() else "✗ Not created"
    console.print(f"Output directory: [{('green' if output_dir.exists() else 'yellow')}]{output_status}[/]")

    console.print()
