"""Setup wizard command."""

import click
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
import yaml
import pandas as pd

console = Console()


def setup_wizard(excel_files=None, config_path=None):
    """Interactive setup wizard."""
    console.print("\n[bold blue]MOVR DataHub Analytics - Setup Wizard[/bold blue]\n")

    # Get source directory
    if excel_files is None:
        source_dir = Prompt.ask(
            "Where are your Excel files located?",
            default="../source-movr-data"
        )
        source_dir = Path(source_dir)
    else:
        source_dir = Path(excel_files[0]).parent

    # Check if directory exists
    if not source_dir.exists():
        console.print(f"[yellow]Warning: Directory not found: {source_dir}[/yellow]")
        create_dir = Confirm.ask("Create directory?")
        if create_dir:
            source_dir.mkdir(parents=True)
        else:
            console.print("[red]Setup aborted[/red]")
            return

    # Get output directory
    output_dir = Prompt.ask(
        "Where should output files be saved?",
        default="output"
    )

    # Get strictness mode
    strictness = Prompt.ask(
        "Choose data wrangling strictness mode",
        choices=["strict", "permissive", "interactive"],
        default="permissive"
    )

    # Discover Excel files in source directory
    data_sources = []
    dictionary_file = None

    if source_dir.exists():
        excel_files = list(source_dir.glob("*.xlsx"))
        console.print(f"\n[cyan]Found {len(excel_files)} Excel files in {source_dir}[/cyan]")

        for excel_file in excel_files:
            # Skip PHI files (but not noPHI files)
            if "_PHI" in excel_file.name and "noPHI" not in excel_file.name:
                console.print(f"  [yellow]Skipping PHI file: {excel_file.name}[/yellow]")
                continue

            # Skip data dictionary files (but remember location)
            if "Dictionary" in excel_file.name or "dictionary" in excel_file.name:
                console.print(f"  [yellow]Skipping dictionary file: {excel_file.name}[/yellow]")
                dictionary_file = excel_file
                continue

            # Create data source entry
            base_name = excel_file.stem  # e.g., "Demographics_noPHI" or "Encounter"
            # Clean name for table (remove _noPHI suffix if present)
            clean_name = base_name.replace("_noPHI", "").replace("_nophi", "")

            # Keep the path as provided (relative or absolute)
            # If source_dir is already relative, keep it relative
            try:
                # Try to make it relative to current directory
                relative_path = excel_file.relative_to(Path.cwd())
                excel_path_str = str(relative_path)
            except ValueError:
                # If that fails, use the path as-is (it's already relative or absolute)
                excel_path_str = str(excel_file)

            # Read Excel file to detect all sheet names
            try:
                excel_obj = pd.ExcelFile(excel_file)
                sheet_names = excel_obj.sheet_names

                # Sheets to skip (common metadata/instruction sheets)
                skip_patterns = ['instructions', 'readme', 'notes', 'metadata', 'changelog']

                # Create mappings for all sheets
                sheet_mappings = {}
                skipped_sheets = []

                for sheet in sheet_names:
                    # Check if sheet should be skipped
                    sheet_lower = sheet.lower()
                    if any(pattern in sheet_lower for pattern in skip_patterns):
                        skipped_sheets.append(sheet)
                        continue

                    # Check if this is a repeat group sheet
                    # Look for "repeat" or "group" (including truncated versions)
                    has_repeat_group = False
                    base_name_only = sheet_lower
                    split_position = -1

                    # Look for full words first
                    if ' repeat' in sheet_lower or sheet_lower.startswith('repeat'):
                        split_position = sheet_lower.find('repeat')
                        has_repeat_group = True
                    elif ' group' in sheet_lower or sheet_lower.startswith('group'):
                        split_position = sheet_lower.find('group')
                        has_repeat_group = True
                    # Check for truncated versions (these typically appear at end due to Excel 31-char limit)
                    elif sheet_lower.endswith((' repeat g', ' repeat gr', ' repeat gro', ' repeat grou')):
                        split_position = sheet_lower.rfind(' repeat')
                        has_repeat_group = True
                    elif sheet_lower.endswith((' rep', ' repe', ' repea', ' repeat')):
                        split_position = sheet_lower.rfind(' rep')
                        has_repeat_group = True
                    elif sheet_lower.endswith((' gro', ' grou', ' group')):
                        split_position = sheet_lower.rfind(' gro')
                        has_repeat_group = True

                    if has_repeat_group and split_position != -1:
                        # Extract everything BEFORE the repeat/group text
                        base_name_only = sheet_lower[:split_position].strip()

                    if has_repeat_group:
                        # Clean the base name and add _rg suffix
                        # "Tracheostomy Repeat Group" -> "tracheostomy_rg"
                        # "GAA Enzyme Activity Repeat" -> "gaaenzymeactivity_rg"
                        cleaned_base = base_name_only.replace(" ", "").replace("-", "").replace("_", "")
                        table_name = f"{clean_name.lower()}_{cleaned_base}_rg"
                    else:
                        # Regular sheet: Convert "Main Data" -> "maindata"
                        # No repeat/group, so just clean the whole name
                        cleaned = sheet_lower.replace(" ", "").replace("-", "").replace("_", "")
                        table_name = f"{clean_name.lower()}_{cleaned}"

                    sheet_mappings[sheet] = table_name

                if sheet_mappings:
                    data_source = {
                        "name": clean_name.lower(),
                        "excel_path": excel_path_str,
                        "sheet_mappings": sheet_mappings,
                        "skip_sheets": skipped_sheets
                    }
                    data_sources.append(data_source)
                    console.print(f"  [green]✓ Added: {excel_file.name}[/green]")
                    console.print(f"    Sheets: {', '.join(sheet_mappings.keys())}")
                    if skipped_sheets:
                        console.print(f"    [dim]Skipped: {', '.join(skipped_sheets)}[/dim]")
                else:
                    console.print(f"  [yellow]Skipping: {excel_file.name} (no data sheets found)[/yellow]")
            except Exception as e:
                console.print(f"  [yellow]Warning: Could not read {excel_file.name}: {e}[/yellow]")

    # Create configuration
    config = {
        "data_sources": data_sources,
        "wrangling": {
            "strictness": strictness,
            "date_formats": ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"],
            "missing_values": ["", "NA", "N/A", "NULL", "Unknown"],
        },
        "paths": {
            "data_dir": "data",
            "output_dir": output_dir,
            "parquet_dir": "data/parquet",
        },
        "audit": {
            "enabled": True,
            "log_dir": "data/.audit",
        }
    }

    # Save configuration
    config_file = Path("config/config.yaml")
    config_file.parent.mkdir(parents=True, exist_ok=True)

    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    console.print(f"\n[green]✓ Configuration saved to: {config_file}[/green]")
    console.print(f"[green]✓ Configured {len(data_sources)} data sources[/green]")

    # Prompt to import data dictionary if found
    if dictionary_file:
        console.print(f"\n[cyan]Found data dictionary:[/cyan] {dictionary_file.name}")
        import_dict = Confirm.ask(
            "Import data dictionary now?",
            default=True
        )

        if import_dict:
            console.print("")  # Add spacing
            # Import the dictionary
            from movr.cli.commands.dictionary import import_dictionary
            success = import_dictionary(str(dictionary_file))

            if not success:
                console.print("\n[yellow]Dictionary import failed, but you can try again later:[/yellow]")
                console.print("  [cyan]movr import-dictionary[/cyan]\n")
        else:
            console.print("\n[yellow]Skipped dictionary import[/yellow]")
            console.print("You can import it later with: [cyan]movr import-dictionary[/cyan]\n")

    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Run: [cyan]movr convert[/cyan] to convert Excel files to Parquet")
    console.print("  2. Run: [cyan]movr validate[/cyan] to check data quality")
    console.print("  3. Run: [cyan]movr summary[/cyan] to see enrollment and encounter stats")
    console.print("  4. Start analyzing with Python or Jupyter notebooks\n")


def run_setup(source_dir=None, config_path=None):
    """Run setup wizard."""
    excel_files = None
    if source_dir:
        excel_files = list(Path(source_dir).glob("*.xlsx"))

    return setup_wizard(excel_files=excel_files, config_path=config_path)
