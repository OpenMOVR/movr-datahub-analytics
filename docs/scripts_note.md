# Scripts - Personal Notes

These scripts exist because **notebooks require too many steps before you can actually explore data**.

---

## The Problem

In a typical notebook, before you can do anything useful:

```python
from movr import load_data, CohortManager
tables = load_data()                           # Step 1
cohorts = CohortManager(tables)                # Step 2
cohorts.create_base_cohort(name='base')        # Step 3
cohorts.filter_cohort(                         # Step 4
    source_cohort='base',
    name='dmd_datahub',
    filters={'disease': 'DMD', 'registry': False}
)
# NOW you can finally start exploring...
```

I wanted something where I just import and go:

```python
from scripts.quick_start_exploratory_cohorts import quick_CohortAnalyzer
analyzer = quick_CohortAnalyzer()
tables, cohorts, created = analyzer.run_analysis()
# Ready to explore
```

---

## What Each Script Does

### `quick_start_exploratory_cohorts.py`

**My favorite.** One-liner to get everything ready:

```python
from scripts.quick_start_exploratory_cohorts import quick_CohortAnalyzer

analyzer = quick_CohortAnalyzer()
tables, cohorts, created = analyzer.run_analysis()

# Now you have:
# - tables: all loaded Parquet tables
# - cohorts: CohortManager with base + all disease cohorts created
# - created: list of cohort names that were created
```

### `make_all_disease_cohorts.py`

Creates exploratory cohorts for every disease in `config/cohort_definitions.yaml`:

```bash
python scripts/make_all_disease_cohorts.py --run --force
```

Or import it:

```python
from scripts.make_all_disease_cohorts import create_all_disease_cohorts
tables, cohorts, created = create_all_disease_cohorts(force=True, registry=False)
```

### `make_exploratory_cohort.py`

Create specific cohorts from CLI:

```bash
# Single disease
python scripts/make_exploratory_cohort.py --disease DMD --registry False

# Multiple diseases
python scripts/make_exploratory_cohort.py --diseases DMD,SMA --registry False

# All diseases from config
python scripts/make_exploratory_cohort.py --all-diseases --registry False
```

### `exploratory_interpreter.py`

Interactive REPL with helpers preloaded:

```bash
python scripts/exploratory_interpreter.py

# Inside the REPL:
create_cohort('DMD', registry=False, force=True)
list_cohorts()
show_summary('exploratory_dmd_datahub')
```

Or run a demo flow:

```bash
python scripts/exploratory_interpreter.py --run --diseases DMD,SMA
```

---

## Getting Filtered Tables

**Now available in the library:** `cohorts.get_filtered_tables(name)`

This was the missing piece. Now you can get all tables filtered to a cohort's patients in one line:

```python
from scripts.quick_start_exploratory_cohorts import quick_CohortAnalyzer

# Setup
analyzer = quick_CohortAnalyzer()
tables, cohorts, created = analyzer.run_analysis()

# Get ALL tables filtered to DMD patients only
dmd_tables = cohorts.get_filtered_tables('exploratory_dmd_datahub')

# Now explore:
dmd_tables['demographics_maindata']   # Only DMD patients
dmd_tables['encounter_maindata']      # Only DMD encounters
dmd_tables['diagnosis_maindata']      # Only DMD diagnoses
```

You can also filter specific tables:

```python
# Only get demographics and encounters
filtered = cohorts.get_filtered_tables('dmd', tables=['demographics_maindata', 'encounter_maindata'])
```

---

## The Complete Quick Start

Here's the fastest way to go from zero to exploring DMD data:

```python
from scripts.quick_start_exploratory_cohorts import quick_CohortAnalyzer

# One-liner setup
analyzer = quick_CohortAnalyzer()
tables, cohorts, created = analyzer.run_analysis()

# Get filtered tables for DMD
dmd = cohorts.get_filtered_tables('exploratory_dmd_datahub')

# Now you're ready to explore
dmd['demographics_maindata'].head()
dmd['encounter_maindata']['encntdt'].describe()
```

---

## Future Improvements

Still on the wishlist:

1. **Presets for common filters** - `load_dmd_datahub()` convenience function
2. **Lazy evaluation** - Don't filter until you need it

These scripts remain convenience tools for this repo's notebooks, not part of the PyPI package.

---

## Quick Reference

| I want to... | Use this |
|--------------|----------|
| Get everything ready in one line | `quick_CohortAnalyzer().run_analysis()` |
| Create all disease cohorts | `create_all_disease_cohorts(force=True)` |
| Create a specific cohort from CLI | `python make_exploratory_cohort.py --disease DMD` |
| Interactive session with helpers | `python exploratory_interpreter.py` |

---

## Typical Filters I Always Use

Almost every analysis starts with:

```python
filters = {
    'registry': False,  # DataHub only (not USNDR)
    'disease': 'DMD'    # or 'SMA'
}
```

The `registry` filter maps to `usndr` column:
- `registry=False` → `usndr != True` (DataHub participants)
- `registry=True` → `usndr == True` (USNDR participants)

---

*These scripts are personal tools, not part of the installable library. They live here for convenience.*
