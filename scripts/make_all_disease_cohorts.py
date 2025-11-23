#!/usr/bin/env python3
"""
Create all disease-specific exploratory cohorts (registry=False by default).

This script will:
 - load tables via movr.load_data
 - instantiate CohortManager
 - ensure `base` cohort exists
 - create one exploratory cohort per disease found in config/cohort_definitions.yaml

The default cohort naming convention used is: exploratory_<disease_lower>_datahub
(e.g. exploratory_dmd_datahub). You can pass --force to overwrite existing
in-memory cohort names.

Usage:
  python scripts/make_all_disease_cohorts.py --run
  from scripts.make_all_disease_cohorts import create_all_disease_cohorts
  tables, cohorts, created = create_all_disease_cohorts(force=True, registry=False)

This is intended to be light-weight and handy when writing exploratory notebooks —
import the module and call `create_all_disease_cohorts()` from the notebook to
have tables, cohorts and created cohort names available automatically.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple
import argparse
import yaml

from movr import load_data
from movr.cohorts.manager import CohortManager


def _read_diseases_from_config(path: Path) -> List[str]:
    """Parse config/cohort_definitions.yaml and return unique disease code list.

    We look for entries with a `filters.disease` key and collect values.
    """
    if not path.exists():
        raise FileNotFoundError(f"Cohort definitions file not found: {path}")

    with path.open('r', encoding='utf-8') as fh:
        # support multiple YAML documents in the file (some files include '---' separators)
        docs = list(yaml.safe_load_all(fh))

    diseases = set()
    # iterate each document to find 'cohorts' entries
    for doc in docs:
        if not isinstance(doc, dict):
            continue
        cohorts = doc.get('cohorts', [])
    for c in cohorts:
        filters = c.get('filters') if isinstance(c, dict) else None
        if not filters:
            continue
        d = filters.get('disease')
        if isinstance(d, str):
            diseases.add(d)
        elif isinstance(d, list):
            for v in d:
                diseases.add(v)

    # Normalize and return sorted list
    return sorted({str(x).upper() for x in diseases})


def create_all_disease_cohorts(tables=None, cohorts=None, force: bool = False, registry: bool = False, verbose: bool = True) -> Tuple:
    """Load environment if needed and create exploratory cohorts for all diseases.

    Returns tuple: (tables, cohorts, created_list)
    """
    if tables is None or cohorts is None:
        if verbose:
            print('Loading tables and initializing CohortManager...')
        tables = load_data(verbose=verbose)
        cohorts = CohortManager(tables)

    # ensure base exists
    if 'base' not in cohorts.list_cohorts():
        if verbose:
            print('Creating base cohort...')
        cohorts.create_base_cohort(name='base')

    # Read diseases from config
    config_path = Path(__file__).resolve().parents[1] / 'config' / 'cohort_definitions.yaml'
    diseases = _read_diseases_from_config(config_path)
    if verbose:
        print('Found diseases:', diseases)

    created = []
    for d in diseases:
        # create a safe name for the exploratory cohort
        dn = d.lower()
        name = f"exploratory_{dn}_{'datahub' if not registry else 'usndr'}"

        try:
            # Create from base and apply both disease + registry filter
            filters = {'disease': d, 'registry': registry}
            if name in cohorts.list_cohorts() and not force:
                if verbose:
                    print(f"Skipping existing cohort {name} (use force=True to overwrite)")
                continue
            # Work from base to be conservative
            cohorts.filter_cohort(source_cohort='base', name=name, filters=filters)
            created.append(name)
            if verbose:
                print('Created cohort:', name)
        except Exception as e:
            # don't stop on errors; log and continue
            print(f'Error creating cohort {name}: {e}')

    return tables, cohorts, created


def main():
    parser = argparse.ArgumentParser(description='Create all disease-specific exploratory cohorts (registry False by default)')
    parser.add_argument('--run', action='store_true', help='Run creation flow and exit')
    parser.add_argument('--force', action='store_true', help='Overwrite existing cohorts')
    parser.add_argument('--registry', action='store_true', help='Create cohorts for registry=True (USNDR) instead of DataHub')
    parser.add_argument('--quiet', action='store_true', help='Reduce verbosity')
    args = parser.parse_args()

    if args.run:
        tables, cohorts, created = create_all_disease_cohorts(force=args.force, registry=args.registry, verbose=not args.quiet)
        print('\nDone. Created cohorts:')
        for c in created:
            try:
                print(c, '->', cohorts.get_cohort_summary(c))
            except Exception:
                print(c, '-> <summary unavailable>')


if __name__ == '__main__':
    main()
