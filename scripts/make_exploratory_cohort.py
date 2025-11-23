#!/usr/bin/env python3
"""
Quick utility to create a fast exploratory cohort using existing cohort_definitions.

Usage (examples):
    # create a DMD cohort restricted to DataHub participants (usndr = False)
    python scripts/make_exploratory_cohort.py --disease DMD --registry False --name exploratory_dmd_datahub

    # create a general exploratory cohort (default: DMD + DataHub)
    python scripts/make_exploratory_cohort.py

    # create multiple cohorts in one go (DMD and SMA)
    python scripts/make_exploratory_cohort.py --diseases DMD,SMA --registry False

    # create cohorts for all diseases defined in config/cohort_definitions.yaml
    python scripts/make_exploratory_cohort.py --all-diseases --registry False

This script is intentionally small and conservative: it updates the in-memory
CohortManager cohorts so you can immediately use them in notebooks or the
interactive session. It does not modify config files by default.
"""

import argparse
import yaml
from pathlib import Path
from movr import load_data
from movr.cohorts.manager import CohortManager


def load_cohort_definitions(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, 'rt') as fh:
        return yaml.safe_load(fh) or {}


def main():
    parser = argparse.ArgumentParser(description="Create an exploratory cohort quickly")
    parser.add_argument('--disease', '-d', help='Disease code (e.g., DMD, SMA). Defaults to DMD', default='DMD')
    parser.add_argument('--diseases', help='Comma separated list of disease codes to create (e.g. DMD,SMA)', default=None)
    parser.add_argument('--all-diseases', help='Create exploratory cohorts for ALL disease definitions found in config/cohort_definitions.yaml', action='store_true')
    parser.add_argument('--registry', '-r', help='Registry filter: True|False. Default False (DataHub only)', default='False')
    parser.add_argument('--name', '-n', help='Name for the new exploratory cohort', default=None)
    parser.add_argument('--force', help='Overwrite existing cohort of same name', action='store_true')
    args = parser.parse_args()

    disease = args.disease
    registry_flag = str(args.registry).lower() in ('1', 'true', 't', 'yes', 'y')

    # Load data and cohort manager
    print('Loading tables... (fast mode)')
    tables = load_data(verbose=False)
    cohorts = CohortManager(tables)

    # Ensure base cohort exists
    if 'base' not in cohorts.list_cohorts():
        print('Creating base cohort (enrollment validation)')
        cohorts.create_base_cohort(name='base')

    # Build the list of diseases to create
    if args.all_diseases:
        # Pull disease values from cohort_definitions.yaml templates
        defs_path = Path('config/cohort_definitions.yaml')
        defs = load_cohort_definitions(defs_path)
        disease_set = set()
        if defs and 'cohorts' in defs:
            for c in defs['cohorts']:
                f = c.get('filters', {})
                d = f.get('disease')
                if isinstance(d, str):
                    disease_set.add(d)
                elif isinstance(d, (list, tuple)):
                    disease_set.update(d)

        diseases_to_create = sorted(disease_set) if disease_set else [disease]
    elif args.diseases:
        diseases_to_create = [d.strip() for d in args.diseases.split(',') if d.strip()]
    else:
        diseases_to_create = [disease]

    # Use cohort_definitions.yaml for templates (if helpful) - load but don't require
    defs_path = Path('config/cohort_definitions.yaml')
    defs = load_cohort_definitions(defs_path)

    # Create cohort from source
    created = []
    for d in diseases_to_create:
        cohort_name_local = args.name or f"exploratory_{d.lower()}_{'usndr' if registry_flag else 'datahub'}"

        # determine source for this disease (respect templates when present)
        source_name_local = None
        if defs and 'cohorts' in defs:
            for c in defs['cohorts']:
                f = c.get('filters', {})
                fd = f.get('disease')
                if fd:
                    if (isinstance(fd, str) and fd == d) or (isinstance(fd, (list, tuple)) and d in fd):
                        source_name_local = c.get('name')
                        break
        if source_name_local is None:
            source_name_local = 'base'

        filters_local = {}
        if source_name_local == 'base':
            filters_local['disease'] = d
        filters_local['registry'] = registry_flag

        print(f"Creating cohort '{cohort_name_local}' from '{source_name_local}' with filters: {filters_local}")
        if cohort_name_local in cohorts.list_cohorts() and args.force:
            cohorts._cohorts.pop(cohort_name_local, None)

        cohorts.filter_cohort(source_cohort=source_name_local, name=cohort_name_local, filters=filters_local)
        created.append(cohort_name_local)

    # Print summary for all created
    print('\nCreated cohorts:')
    for name in created:
        try:
            s = cohorts.get_cohort_summary(name)
            print(f"  • {name}: {s.get('n_patients')} patients")
        except Exception:
            print(f"  • {name}: summary unavailable")

    print('\nNow you can open a notebook and use these cohorts via CohortManager (cohorts.get_cohort(<name>))')


if __name__ == '__main__':
    main()
