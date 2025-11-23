"""Data dictionary import and management commands."""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
import pandas as pd
from loguru import logger
import yaml

from movr.config import get_config

console = Console()


def auto_detect_dictionary():
    """Auto-detect data dictionary file in source directory."""
    # Try to find in ../source-movr-data/
    source_dir = Path("../source-movr-data")

    if not source_dir.exists():
        return None

    # Look for files with "Data Dictionary" or "Dictionary" in name
    patterns = ["*Data*Dictionary*.xlsx", "*Dictionary*.xlsx", "*DICTIONARY*.xlsx"]

    for pattern in patterns:
        files = list(source_dir.glob(pattern))
        if files:
            # Return the most recent one if multiple found
            return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]

    return None


def import_dictionary(excel_path: str = None, output_path: str = None):
    """
    Import data dictionary from Excel to Parquet.

    Args:
        excel_path: Path to data dictionary Excel file (auto-detects if None)
        output_path: Optional output path (defaults to config location)
    """
    console.print(f"\n[bold blue]Importing Data Dictionary[/bold blue]\n")

    # Auto-detect if no path provided
    if excel_path is None:
        console.print("[cyan]Auto-detecting data dictionary file...[/cyan]")
        excel_path = auto_detect_dictionary()

        if excel_path is None:
            console.print("[red]Could not auto-detect data dictionary file[/red]")
            console.print("[yellow]Expected pattern: 'MDA MOVR_Data Dictionary_*.xlsx' in ../source-movr-data/[/yellow]")
            console.print("\nPlease specify path manually:")
            console.print("  [cyan]movr import-dictionary path/to/dictionary.xlsx[/cyan]")
            return False

        console.print(f"[green]✓ Found: {excel_path.name}[/green]")

    console.print(f"Source: {excel_path}")

    excel_path = Path(excel_path)
    if not excel_path.exists():
        console.print(f"[red]Error: File not found: {excel_path}[/red]")
        return False

    config = get_config()

    # Determine output path
    if output_path:
        output_path = Path(output_path)
    else:
        output_path = Path(config.paths.data_dictionary)

    # Create metadata directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Read Excel file
        console.print("[cyan]Reading Excel file...[/cyan]")
        excel_file = pd.ExcelFile(excel_path)

        console.print(f"Found {len(excel_file.sheet_names)} sheets")
        console.print(f"Sheets: {', '.join(excel_file.sheet_names)}")

        # Typically dictionary is in first sheet or sheet named "Dictionary"/"Data Dictionary"
        sheet_name = None
        for name in excel_file.sheet_names:
            if 'dictionary' in name.lower() or 'dict' in name.lower():
                sheet_name = name
                break

        if sheet_name is None:
            # Use first sheet
            sheet_name = excel_file.sheet_names[0]
            console.print(f"[yellow]No 'dictionary' sheet found, using: {sheet_name}[/yellow]")
        else:
            console.print(f"[cyan]Using sheet: {sheet_name}[/cyan]")

        # Read the dictionary
        df = pd.read_excel(excel_file, sheet_name=sheet_name)

        console.print(f"\n[cyan]Dictionary contains:[/cyan]")
        console.print(f"  Rows: {len(df):,}")
        console.print(f"  Columns: {len(df.columns)}")
        console.print(f"  Column names: {', '.join(df.columns.tolist()[:10])}{'...' if len(df.columns) > 10 else ''}")

        # Clean data for Parquet compatibility
        # Convert all object (mixed type) columns to strings to avoid Parquet schema issues
        console.print(f"\n[cyan]Cleaning data for Parquet...[/cyan]")
        for col in df.columns:
            if df[col].dtype == 'object':
                # Convert to string, handling NaN values
                df[col] = df[col].astype(str).replace('nan', pd.NA)

        # Save to Parquet
        console.print(f"\n[cyan]Saving to Parquet...[/cyan]")
        df.to_parquet(output_path, index=False, compression='snappy')

        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        console.print(f"[green]✓ Saved to: {output_path} ({file_size_mb:.2f} MB)[/green]")

        # Update config to indicate dictionary is available
        config_file = Path("config/config.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)

            # Create metadata section if it doesn't exist
            if 'metadata' not in config_data:
                config_data['metadata'] = {
                    'data_dictionary_available': False,
                    'field_mappings_file': 'config/field_mappings.yaml'
                }

            config_data['metadata']['data_dictionary_available'] = True

            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

            console.print("[green]✓ Updated config: data_dictionary_available = true[/green]")

        # Show preview
        console.print("\n[bold]Preview (first 5 rows):[/bold]")
        preview_table = Table(show_header=True, header_style="bold magenta")

        # Add first few columns
        for col in df.columns[:5]:
            preview_table.add_column(str(col)[:20], overflow="fold")

        for idx, row in df.head().iterrows():
            preview_table.add_row(*[str(row[col])[:30] for col in df.columns[:5]])

        console.print(preview_table)

        console.print("\n[green]✓ Data dictionary import complete[/green]")
        console.print("\n[dim]You can now use dictionary-based commands:[/dim]")
        console.print("  [cyan]movr dictionary search 'keyword'[/cyan]")
        console.print("  [cyan]movr dictionary list-fields --table demographics[/cyan]")
        console.print("  [cyan]movr dictionary show-field FACPATID[/cyan]\n")

        return True

    except Exception as e:
        console.print(f"[red]Error importing dictionary: {e}[/red]")
        logger.exception("Dictionary import failed")
        return False


def search_dictionary(keyword: str, diseases: str = None, form: str = None):
    """
    Search data dictionary for fields matching keyword.

    Args:
        keyword: Search term
        diseases: Comma-separated list of diseases (e.g., "DMD,SMA")
        form: Filter by form/table name
    """
    config = get_config()
    dict_path = Path(config.paths.data_dictionary)

    if not dict_path.exists():
        console.print("[yellow]Data dictionary not found[/yellow]")
        console.print("Run: [cyan]movr import-dictionary <path-to-excel>[/cyan]")
        return

    console.print(f"\n[bold blue]Searching Data Dictionary[/bold blue]")
    console.print(f"Keyword: [cyan]{keyword}[/cyan]")
    if diseases:
        console.print(f"Diseases: [cyan]{diseases}[/cyan]")
    if form:
        console.print(f"Form: [cyan]{form}[/cyan]")
    console.print("")

    try:
        df = pd.read_parquet(dict_path)

        # Search across all string columns
        mask = df.astype(str).apply(lambda x: x.str.contains(keyword, case=False, na=False)).any(axis=1)
        results = df[mask]

        # Filter by disease(s)
        available_diseases = []
        if diseases:
            # Check if user wants all diseases
            if diseases.strip().lower() == 'all':
                # Known disease codes to look for
                known_diseases = ['ALS', 'DMD', 'BMD', 'SMA', 'LGMD', 'FSHD', 'POMPE', 'CMD', 'DM1', 'DM2', 'EDMD', 'OPMD']

                # Columns to exclude (non-disease uppercase columns)
                exclude_cols = ['ID', 'NA', 'UK', 'US', 'FORM', 'FILE', 'TABLE', 'CRF', 'FIELD', 'TYPE', 'CODE', 'DATE', 'NAME']

                # Find all disease columns
                # Method 1: Check for known diseases (case-insensitive)
                available_diseases = [
                    col for col in df.columns
                    if col.upper() in known_diseases
                ]

                # Method 2: Also find other uppercase columns that might be diseases
                # (uppercase, 2-6 chars, not in exclusion list)
                other_diseases = [
                    col for col in df.columns
                    if (col.isupper() and
                        2 <= len(col) <= 6 and
                        col not in exclude_cols and
                        col not in available_diseases)
                ]

                available_diseases.extend(other_diseases)
                console.print(f"[dim]Filtering by all diseases: {', '.join(sorted(available_diseases))}[/dim]\n")
            else:
                disease_list = [d.strip().upper() for d in diseases.split(',')]
                # Check which disease columns exist (case-insensitive)
                available_diseases = [col for col in df.columns if col.upper() in disease_list]

            if available_diseases:
                if diseases.strip().lower() != 'all':
                    console.print(f"[dim]Filtering by diseases: {', '.join(available_diseases)}[/dim]\n")

                # Filter rows where at least one disease column has a non-null/non-empty value
                disease_mask = pd.Series([False] * len(results), index=results.index)
                for disease_col in available_diseases:
                    # Check for non-null, non-empty, not "nan" string
                    disease_mask |= (
                        results[disease_col].notna() &
                        (results[disease_col].astype(str).str.strip() != '') &
                        (results[disease_col].astype(str).str.lower() != 'nan')
                    )

                results = results[disease_mask]
            else:
                console.print(f"[yellow]Warning: No disease columns found for: {diseases}[/yellow]")
                console.print(f"[dim]Available disease columns: {', '.join([c for c in df.columns if c.isupper() and len(c) <= 6])}[/dim]\n")

        # Filter by form/table
        if form:
            # Try to find form column (common names)
            form_col = None
            for col in ['File/Form', 'Form', 'TABLE', 'Table', 'CRF', 'file_form', 'form_name']:
                if col in df.columns:
                    form_col = col
                    break

            if form_col:
                results = results[results[form_col].str.contains(form, case=False, na=False)]
                console.print(f"[dim]Filtering by form: {form}[/dim]\n")
            else:
                console.print(f"[yellow]Warning: Could not find form column in dictionary[/yellow]\n")

        if len(results) == 0:
            console.print(f"[yellow]No results found for '{keyword}' with specified filters[/yellow]")
            return

        console.print(f"[green]Found {len(results)} matches[/green]\n")

        # Show results in table
        table = Table(show_header=True, header_style="bold magenta", show_lines=False)

        # Determine which columns to show
        display_cols = []

        # Always try to show these columns first (but only if they exist)
        priority_cols = ['File/Form', 'Field Name', 'Description', 'Display Label']
        for col in priority_cols:
            if col in df.columns:
                display_cols.append(col)

        # Add ALL disease columns if filtering by disease (no limit)
        if diseases and available_diseases:
            display_cols.extend(available_diseases)

        # If not showing diseases, add a few more useful columns (up to 8 total)
        if not diseases:
            for col in df.columns:
                if col not in display_cols and len(display_cols) < 8:
                    display_cols.append(col)

        # Create table columns - no artificial limit
        for col in display_cols:
            # Adjust column width based on column name length
            col_width = min(max(len(str(col)), 15), 40)
            table.add_column(str(col), overflow="fold", max_width=col_width)

        # Add rows
        for _, row in results.head(20).iterrows():
            table.add_row(*[str(row[col])[:100] if col in row.index else "" for col in display_cols])

        console.print(table)

        if len(results) > 20:
            console.print(f"\n[dim]Showing first 20 of {len(results)} results[/dim]")

    except Exception as e:
        console.print(f"[red]Error searching dictionary: {e}[/red]")
        logger.exception("Dictionary search failed")


def list_fields(table: str = None):
    """List all fields, optionally filtered by table."""
    config = get_config()
    dict_path = Path(config.paths.data_dictionary)

    if not dict_path.exists():
        console.print("[yellow]Data dictionary not found[/yellow]")
        console.print("Run: [cyan]movr import-dictionary <path-to-excel>[/cyan]")
        return

    console.print(f"\n[bold blue]Data Dictionary Fields[/bold blue]\n")

    try:
        df = pd.read_parquet(dict_path)

        # Try to identify table column (common names)
        table_col = None
        for col in ['Table', 'TABLE', 'Form', 'FORM', 'CRF', 'table_name', 'form_name']:
            if col in df.columns:
                table_col = col
                break

        if table and table_col:
            df = df[df[table_col].str.contains(table, case=False, na=False)]
            console.print(f"Filtering by table: [cyan]{table}[/cyan]\n")

        console.print(f"Total fields: {len(df)}\n")

        # Show fields in table
        table_display = Table(show_header=True, header_style="bold magenta")

        for col in df.columns[:5]:
            table_display.add_column(str(col)[:25], overflow="fold")

        for _, row in df.head(50).iterrows():
            table_display.add_row(*[str(row[col])[:40] for col in df.columns[:5]])

        console.print(table_display)

        if len(df) > 50:
            console.print(f"\n[dim]Showing first 50 of {len(df)} fields[/dim]")

    except Exception as e:
        console.print(f"[red]Error listing fields: {e}[/red]")


def show_field(field_name: str):
    """Show detailed information about a specific field."""
    config = get_config()
    dict_path = Path(config.paths.data_dictionary)

    if not dict_path.exists():
        console.print("[yellow]Data dictionary not found[/yellow]")
        console.print("Run: [cyan]movr import-dictionary <path-to-excel>[/cyan]")
        return

    console.print(f"\n[bold blue]Field Details: {field_name}[/bold blue]\n")

    try:
        df = pd.read_parquet(dict_path)

        # Find field (search across columns that might contain field name)
        field_col = None
        for col in ['Field', 'FIELD', 'Variable', 'VARIABLE', 'field_name', 'variable_name']:
            if col in df.columns:
                field_col = col
                break

        if field_col:
            result = df[df[field_col].str.upper() == field_name.upper()]
        else:
            # Search all columns
            mask = df.astype(str).apply(lambda x: x.str.upper() == field_name.upper()).any(axis=1)
            result = df[mask]

        if len(result) == 0:
            console.print(f"[yellow]Field '{field_name}' not found[/yellow]")
            return

        # Display field details
        field_data = result.iloc[0]

        for col, value in field_data.items():
            if pd.notna(value):
                console.print(f"[cyan]{col}:[/cyan] {value}")

    except Exception as e:
        console.print(f"[red]Error showing field: {e}[/red]")


def run_import_dictionary(excel_path: str, output: str = None):
    """Run dictionary import command."""
    import_dictionary(excel_path, output)


def run_search_dictionary(keyword: str, diseases: str = None, form: str = None):
    """Run dictionary search command."""
    search_dictionary(keyword, diseases, form)


def run_list_fields(table: str = None):
    """Run list fields command."""
    list_fields(table)


def run_show_field(field_name: str):
    """Run show field command."""
    show_field(field_name)
