"""Convert Excel to Parquet command."""

import click
from pathlib import Path
from rich.console import Console
from rich.progress import Progress
from loguru import logger

from movr.data import ExcelConverter
from movr.config import get_config

console = Console()


def run_convert(source_dir=None, config_path=None, force=False, clean=False):
    """Run Excel to Parquet conversion."""
    console.print("\n[bold blue]Converting Excel files to Parquet...[/bold blue]\n")

    # Load config
    if config_path:
        config = get_config(config_path=Path(config_path), reload=True)
    else:
        config = get_config()

    # Initialize converter
    converter = ExcelConverter()

    # Check for existing Parquet files and warn if not cleaning
    if not clean:
        output_dir = Path(config.paths.parquet_dir)
        if output_dir.exists():
            existing_files = list(output_dir.glob("*.parquet"))
            if existing_files:
                console.print(f"[yellow]Found {len(existing_files)} existing Parquet files[/yellow]")
                console.print("[dim]Tip: Use 'movr convert --clean' to remove old files first[/dim]\n")

    if source_dir:
        # Convert files from directory
        source_path = Path(source_dir)
        excel_files = list(source_path.glob("*.xlsx"))

        console.print(f"Found {len(excel_files)} Excel files in {source_dir}\n")

        for excel_file in excel_files:
            if "PHI" in excel_file.name:
                console.print(f"[yellow]Skipping PHI file: {excel_file.name}[/yellow]")
                continue

            console.print(f"[cyan]Converting: {excel_file.name}[/cyan]")

            # Infer sheet mappings from file name
            base_name = excel_file.stem
            sheet_mappings = {
                "MainData": f"{base_name.lower()}_maindata"
            }

            try:
                results = converter.convert_file(
                    excel_path=excel_file,
                    sheet_mappings=sheet_mappings,
                    skip_sheets=[]
                )
                console.print(f"[green]✓ Converted {len(results)} sheets[/green]\n")
            except Exception as e:
                console.print(f"[red]✗ Error: {e}[/red]\n")
    else:
        # Convert from config
        if not config.data_sources:
            console.print("[yellow]No data sources defined in config[/yellow]")
            console.print("Run 'movr setup' first or specify --source-dir")
            return

        results = converter.convert_all_sources(clean_existing=clean)
        console.print(f"\n[green]✓ Conversion complete: {len(results)} tables[/green]\n")
