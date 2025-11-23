#!/usr/bin/env python3
"""
Small interactive helper for exploratory cohort creation.

Run this file to drop into a minimal interactive session with preloaded
`tables` and `cohorts` (CohortManager).

Usage:
  python scripts/exploratory_interpreter.py

Once started you get a local prompt where the following helpers are available:

  create_cohort(disease='DMD', registry=False, name=None, force=False)
  create_cohorts(diseases=['DMD','SMA'], registry=False, name_template=None, force=False)
  list_cohorts()
  show_summary(name)

This aims to be a tiny convenience wrapper so you can explore cohorts without
re-writing the same boilerplate in notebooks.
"""

import argparse
import code
from typing import List

from movr import load_data
from movr.cohorts.manager import CohortManager
from pprint import pprint


def _init_env(verbose=False):
    print('Loading tables (fast mode)...')
    tables = load_data(verbose=verbose)
    cohorts = CohortManager(tables)
    if 'base' not in cohorts.list_cohorts():
        cohorts.create_base_cohort(name='base')
    return tables, cohorts


def create_cohort(cohorts: CohortManager, disease: str = 'DMD', registry: bool = False, name: str | None = None, force: bool = False):
    """Create a single exploratory cohort using the CohortManager instance.

    Returns the created cohort name.
    """
    cohort_name = name or f"exploratory_{disease.lower()}_{'usndr' if registry else 'datahub'}"
    if cohort_name in cohorts.list_cohorts() and not force:
        raise RuntimeError(f"Cohort '{cohort_name}' already exists. Use force=True to overwrite.")

    filters = {'disease': disease, 'registry': registry}
    # Create from 'base' to be conservative
    cohorts.filter_cohort(source_cohort='base', name=cohort_name, filters=filters)
    return cohort_name


def create_cohorts(cohorts: CohortManager, diseases: List[str], registry: bool = False, name_template: str | None = None, force: bool = False):
    """Create multiple exploratory cohorts in one call.

    diseases: list of disease codes (e.g., ['DMD','SMA'])
    name_template: optional format string with '{disease}' placeholder
    """
    created = []
    for d in diseases:
        name = name_template.format(disease=d) if name_template else None
        name_local = create_cohort(cohorts, disease=d, registry=registry, name=name, force=force)
        created.append(name_local)
    return created


def list_cohorts(cohorts: CohortManager):
    return cohorts.list_cohorts()


def show_summary(cohorts: CohortManager, name: str):
    return cohorts.get_cohort_summary(name)


def compare_cohorts(cohorts: CohortManager, tables, cohort_names):
    """Run DescriptiveAnalyzer for a list of cohort names and return results + a small summary table.

    Returns (results_dict, summary_rows)
    """
    from movr.analytics.descriptive import DescriptiveAnalyzer

    results = {}
    for name in cohort_names:
        analyzer = DescriptiveAnalyzer(cohort=None, tables=tables, cohort_manager=cohorts, cohort_name=name)
        res = analyzer.run_analysis()
        results[name] = res

    summary_rows = []
    for name, res in results.items():
        s = res.summary
        summary_rows.append({
            'name': name,
            'n_patients': s.get('n_patients'),
            'age_mean': s.get('age_stats', {}).get('mean'),
            'gender_counts': s.get('gender_counts')
        })

    return results, summary_rows


def run_notebook_flow(tables, cohorts, diseases=None, registry=False):
    """Run a small notebook-like flow: create example cohorts (if provided) and compare them.

    This mirrors the notebook `03_exploratory_interpreter_example.ipynb` behaviour for quick demos.
    """
    diseases = diseases or ['DMD', 'SMA']
    print('\nCreating exploratory cohorts:', diseases)
    created = create_cohorts(cohorts, diseases=diseases, registry=registry, force=True)
    print('Created cohorts:', created)
    for c in created:
        print(c, '->', cohorts.get_cohort_summary(c))

    print('\nRunning DescriptiveAnalyzer for created cohorts...')
    results, summary = compare_cohorts(cohorts, tables, created)
    print('\nSummary rows:')
    pprint(summary)
    return created, results, summary


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--quiet', action='store_true', help='Reduce verbosity')
    parser.add_argument('--disease', '-d', default=None, help='Create a first cohort once started')
    parser.add_argument('--registry', '-r', default='False', help='Registry filter for the initial cohort')
    parser.add_argument('--create', action='store_true', help='Create an initial cohort with provided --disease')
    parser.add_argument('--run', action='store_true', help='Run the notebook-like demo flow and exit')
    parser.add_argument('--diseases', default='DMD,SMA', help="Comma-separated diseases for the demo flow (default: 'DMD,SMA')")
    args = parser.parse_args()

    tables, cohorts = _init_env(verbose=not args.quiet)

    # Provide a convenient locals dict for interactive session
    local_vars = {
        'tables': tables,
        'cohorts': cohorts,
        'create_cohort': lambda disease='DMD', registry=False, name=None, force=False: create_cohort(cohorts, disease, registry, name, force),
        'create_cohorts': lambda diseases, registry=False, name_template=None, force=False: create_cohorts(cohorts, diseases, registry, name_template, force),
        'list_cohorts': lambda: list_cohorts(cohorts),
        'show_summary': lambda name: show_summary(cohorts, name),
    }

    if args.create and args.disease:
        registry_flag = str(args.registry).lower() in ('1', 'true', 't', 'yes', 'y')
        name = create_cohort(local_vars['cohorts'], disease=args.disease, registry=registry_flag, force=True)
        print(f"Created cohort: {name}")

    if args.run:
        registry_flag = str(args.registry).lower() in ('1', 'true', 't', 'yes', 'y')
        diseases = [d.strip() for d in str(args.diseases).split(',') if d.strip()]
        run_notebook_flow(tables, cohorts, diseases=diseases, registry=registry_flag)
        return

    banner = (
        "Interactive exploratory session\n"
        "- helpers: create_cohort, create_cohorts, list_cohorts, show_summary\n"
        "- preloaded: tables, cohorts (CohortManager)\n"
        "- type 'exit()' or CTRL-D to quit\n"
    )

    code.interact(banner=banner, local=local_vars)


if __name__ == '__main__':
    main()
