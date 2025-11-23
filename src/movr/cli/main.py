"""
Main CLI entry point using Click.

Provides movr command-line tool.
"""

import click
from loguru import logger
import sys

# Configure loguru
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")


@click.group()
@click.version_option(version="0.1.0", prog_name="movr")
def cli():
    """MOVR DataHub Analytics - Clinical data analytics for neuromuscular registries."""
    pass


@cli.command()
@click.option('--source-dir', type=click.Path(exists=True), help='Directory containing Excel files')
@click.option('--config', type=click.Path(), help='Path to config file')
def setup(source_dir, config):
    """Interactive setup wizard for first-time configuration."""
    from movr.cli.commands.setup import run_setup
    run_setup(source_dir=source_dir, config_path=config)


@cli.command()
@click.option('--source-dir', type=click.Path(exists=True), help='Directory containing Excel files')
@click.option('--config', type=click.Path(), help='Path to config file')
@click.option('--force', is_flag=True, help='Force reconversion even if Parquet files exist')
@click.option('--clean', is_flag=True, help='Remove all existing Parquet files before conversion')
def convert(source_dir, config, force, clean):
    """Convert Excel files to Parquet format."""
    from movr.cli.commands.convert import run_convert
    run_convert(source_dir=source_dir, config_path=config, force=force, clean=clean)


@cli.command()
@click.option('--strictness', type=click.Choice(['strict', 'permissive', 'interactive']), default='permissive')
def validate(strictness):
    """Validate data quality and enrollment."""
    from movr.cli.commands.validate import run_validate
    run_validate(strictness=strictness)


@cli.group()
def cohorts():
    """Cohort management commands."""
    pass


@cohorts.command('list')
def list_cohorts():
    """List all defined cohorts."""
    click.echo("Cohort listing not yet implemented")


@cohorts.command('create')
@click.option('--name', required=True, help='Cohort name')
@click.option('--filter', 'filter_str', help='Filter string (e.g., "DISEASE=DMD,AGE=0-18")')
def create_cohort(name, filter_str):
    """Create a new cohort."""
    click.echo(f"Creating cohort: {name}")
    if filter_str:
        click.echo(f"Filters: {filter_str}")


@cli.command()
@click.option('--cohort', required=True, help='Cohort name')
@click.option('--type', 'analysis_type', default='descriptive', help='Analysis type')
@click.option('--output', required=True, help='Output file path')
def analyze(cohort, analysis_type, output):
    """Run analysis on a cohort."""
    click.echo(f"Analyzing cohort: {cohort}")
    click.echo(f"Analysis type: {analysis_type}")
    click.echo(f"Output: {output}")


@cli.group()
def fields():
    """Data dictionary field exploration."""
    pass


@fields.command('search')
@click.argument('keyword')
def search_fields(keyword):
    """Search for fields containing keyword."""
    click.echo(f"Searching for: {keyword}")


@fields.command('browse')
@click.argument('table_name')
def browse_fields(table_name):
    """Browse all fields in a table."""
    click.echo(f"Browsing fields in: {table_name}")


@cli.command()
def status():
    """Check data and configuration status."""
    from movr.cli.commands.status import run_status
    run_status()


@cli.command()
@click.option('--registry', type=click.Choice(['datahub', 'usndr', 'all']), default='datahub',
              help='Which registry to summarize')
@click.option('--metric', type=click.Choice(['enrollment', 'recruitment', 'encounters', 'rates', 'all']),
              default='all', help='Which metrics to display')
def summary(registry, metric):
    """Display summary statistics (enrollment, encounters, rates)."""
    from movr.cli.commands.summary import run_summary
    run_summary(registry=registry, metric=metric)


@cli.command('import-dictionary')
@click.argument('excel_path', type=click.Path(exists=True), required=False)
@click.option('--output', type=click.Path(), help='Output path for Parquet file')
def import_dictionary_cmd(excel_path, output):
    """Import data dictionary from Excel to Parquet.

    If no path provided, auto-detects dictionary file in ../source-movr-data/
    """
    from movr.cli.commands.dictionary import run_import_dictionary
    run_import_dictionary(excel_path, output)


@cli.group()
def dictionary():
    """Data dictionary exploration commands."""
    pass


@dictionary.command('search')
@click.argument('keyword')
@click.option('--diseases', help='Filter by disease(s): "all" or comma-separated (e.g., "DMD,SMA")')
@click.option('--form', help='Filter by form/table name')
def search_dictionary(keyword, diseases, form):
    """Search data dictionary for fields containing keyword.

    Examples:
        movr dictionary search "age"
        movr dictionary search "medication" --diseases "DMD,SMA"
        movr dictionary search "ambulation" --diseases "all"
        movr dictionary search "vital" --form "Encounter"
    """
    from movr.cli.commands.dictionary import run_search_dictionary
    run_search_dictionary(keyword, diseases, form)


@dictionary.command('list-fields')
@click.option('--table', help='Filter by table name')
def list_dictionary_fields(table):
    """List all fields in data dictionary."""
    from movr.cli.commands.dictionary import run_list_fields
    run_list_fields(table)


@dictionary.command('show-field')
@click.argument('field_name')
def show_dictionary_field(field_name):
    """Show detailed information about a specific field."""
    from movr.cli.commands.dictionary import run_show_field
    run_show_field(field_name)


if __name__ == "__main__":
    cli()
