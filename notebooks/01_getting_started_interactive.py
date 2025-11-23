# %% [markdown]
# MOVR DataHub Analytics - Getting Started
#
# First Analysis Notebook (interactive script)
#
# This script is the interactive (.py) version of notebooks/01_getting_started.ipynb.
# Use VS Code Run Cell (Interactive Window) on each section (cells are separated with # %%)
#
# Updated: 2025-11-21 - Now uses field resolution (disease, gender, age, registry)

# %%
# NOTE: minimal, focused cells for step-by-step interactive use

# %% [markdown]
# Setup

# %%
# Imports and plotting config
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

# MOVR package imports
from movr import load_data, CohortManager, DescriptiveAnalyzer
from movr.config import get_config

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')

pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows', 100)

print('✓ Imports complete')

# %% [markdown]
## 1. Load data

# %%
# Load all available tables from data/parquet using movr.load_data()
tables = load_data(verbose=True)

print('\n' + '='*60)
print(f'Loaded {len(tables)} tables:')
for table_name in tables.keys():
    df = tables[table_name]
    print(f"  • {table_name}: {len(df):,} rows × {len(df.columns)} columns")
print('='*60)

# %% [markdown]
### Quick data inspection

# %%
# Demographics
if 'demographics_maindata' in tables:
    demographics = tables['demographics_maindata']
    print('Demographics — first 5 rows:')
    display(demographics.head())
    print(f"\nTotal Demographics records: {len(demographics):,}")

    # Show key fields for cohort filtering
    print('\nKey fields for filtering:')
    print(f"  dstype (disease): {demographics['dstype'].unique().tolist()}")
    print(f"  gender: {demographics['gender'].unique().tolist()}")
    print(f"  usndr (registry): {demographics['usndr'].unique().tolist()}")
    print(f"  dob (for age calc): present = {'dob' in demographics.columns}")

# %%
# Encounters
if 'encounter_maindata' in tables:
    encounter = tables['encounter_maindata']
    print('Encounter — first 5 rows:')
    display(encounter.head())
    print(f"\nTotal Encounters: {len(encounter):,}")
    if 'FACPATID' in encounter.columns:
        print(f"Unique Patients: {encounter['FACPATID'].nunique():,}")

# %% [markdown]
## 2. Enrollment validation

# %%
from movr.cohorts import EnrollmentValidator

validator = EnrollmentValidator(tables)
report = validator.validate_enrollment()

print('='*60)
print('ENROLLMENT VALIDATION REPORT')
print('='*60)
print(f"\nTotal Unique Patients: {report['total_unique_patients']:,}")
print(f"Enrolled Patients (with all 3 forms): {report['enrolled_count']:,}")
print(f"Enrollment Rate: {report['enrolled_count']/report['total_unique_patients']*100:.1f}%")

print('\nPatients by Form:')
for form_name, count in report['form_counts'].items():
    print(f"  • {form_name}: {count:,} patients")

print('\nMissing forms:')
for form_name, count in report['missing_by_form'].items():
    if count > 0:
        print(f"  • Missing {form_name}: {count:,} patients")

print('='*60)

# %% [markdown]
## 3. Create base cohort
#
# CohortManager now automatically:
# - Calculates AGE from 'dob' field
# - Resolves canonical field names (disease -> dstype, gender -> gender, etc.)
# - Supports registry filtering (USNDR vs DataHub)

# %%
cohorts = CohortManager(tables)
base_cohort = cohorts.create_base_cohort(name='base')
print(f"Base cohort created: {len(base_cohort):,} patients")

# Get full summary with registry distribution
summary = cohorts.get_cohort_summary('base')
print('\nBase cohort summary:')
print(f"  Total Patients: {summary['n_patients']:,}")

if summary.get('gender_distribution'):
    print('\n  Gender distribution:')
    for gender, count in summary['gender_distribution'].items():
        print(f"    {gender}: {count:,} ({count/summary['n_patients']*100:.1f}%)")

if summary.get('disease_distribution'):
    print('\n  Disease distribution:')
    for disease, count in summary['disease_distribution'].items():
        print(f"    {disease}: {count:,} ({count/summary['n_patients']*100:.1f}%)")

if summary.get('age_stats'):
    print('\n  Age statistics (calculated from dob):')
    age = summary['age_stats']
    print(f"    Mean: {age['mean']:.1f}, Median: {age['median']:.1f}, Range: {age['min']:.0f}-{age['max']:.0f}")

if summary.get('registry_distribution'):
    print('\n  Registry distribution:')
    for reg, count in summary['registry_distribution'].items():
        print(f"    {reg}: {count:,} ({count/summary['n_patients']*100:.1f}%)")

# %% [markdown]
### Visualize base cohort (using actual field names)

# %%
# Use get_cohort_data() to get cohort with demographics (includes calculated AGE)
base_demographics = cohorts.get_cohort_data('base', include_demographics=True)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Base Cohort Overview')

# Disease distribution (dstype field)
if 'dstype' in base_demographics.columns:
    disease_counts = base_demographics['dstype'].value_counts()
    axes[0, 0].pie(disease_counts.values, labels=disease_counts.index, autopct='%1.1f%%')
    axes[0, 0].set_title('Disease distribution (dstype)')

# Gender distribution (gender field)
if 'gender' in base_demographics.columns:
    gender_counts = base_demographics['gender'].value_counts()
    axes[0, 1].bar(gender_counts.index, gender_counts.values)
    axes[0, 1].set_title('Gender distribution')
    axes[0, 1].tick_params(axis='x', rotation=45)

# Age distribution (calculated AGE field)
if 'AGE' in base_demographics.columns:
    axes[1, 0].hist(base_demographics['AGE'].dropna(), bins=30, edgecolor='black')
    axes[1, 0].set_title('Age distribution (from dob)')
    axes[1, 0].set_xlabel('Age (years)')

# Registry distribution (usndr field)
if 'usndr' in base_demographics.columns:
    usndr_count = (base_demographics['usndr'] == True).sum()
    datahub_count = len(base_demographics) - usndr_count
    axes[1, 1].bar(['DataHub', 'USNDR'], [datahub_count, usndr_count])
    axes[1, 1].set_title('Registry (usndr field)')

plt.tight_layout()
plt.show()

# %% [markdown]
## 4. Create Registry and Disease Cohorts
#
# Field Resolution (canonical -> actual):
# - disease -> dstype
# - gender -> gender
# - age -> AGE (calculated from dob)
# - registry -> usndr (True=USNDR, else=DataHub)

# %%
# REGISTRY COHORTS (Priority 1)
usndr_cohort = cohorts.filter_cohort(
    source_cohort='base',
    name='usndr',
    filters={'registry': True}  # usndr == True
)
datahub_cohort = cohorts.filter_cohort(
    source_cohort='base',
    name='datahub',
    filters={'registry': False}  # usndr != True
)

print('Registry Cohorts:')
print(f"  USNDR: {len(usndr_cohort):,} patients")
print(f"  DataHub: {len(datahub_cohort):,} patients")

# %%
# DISEASE COHORTS (Priority 2)
diseases = base_demographics['dstype'].dropna().unique()
print('Diseases:', list(diseases))

disease_cohorts = {}
for disease in sorted(diseases):
    cohort = cohorts.filter_cohort(
        source_cohort='base',
        name=disease.lower(),
        filters={'disease': disease}  # dstype == disease
    )
    disease_cohorts[disease] = cohort
    print(f"  {disease}: {len(cohort):,} patients")

# %%
# Age-based cohorts (AGE calculated from dob)
pediatric = cohorts.filter_cohort(
    source_cohort='base',
    name='pediatric',
    filters={'age': {'min': 0, 'max': 18}}
)
adult = cohorts.filter_cohort(
    source_cohort='base',
    name='adult',
    filters={'age': {'min': 18}}
)
print(f"Pediatric (0-18): {len(pediatric):,}")
print(f"Adult (18+): {len(adult):,}")

# DMD Pediatric - combining disease + age filters
dmd_pediatric = cohorts.filter_cohort(
    source_cohort='dmd',
    name='dmd_pediatric',
    filters={'age': {'min': 0, 'max': 18}}
)
print(f"DMD Pediatric: {len(dmd_pediatric):,}")

# %%
# List all cohorts
print('\nAll cohorts created:')
for name in sorted(cohorts.list_cohorts()):
    df = cohorts.get_cohort(name)
    print(f"  {name:20s}: {len(df):>6,} patients")

# %% [markdown]
## 5. Descriptive analysis (example)

# %%
analyzer = DescriptiveAnalyzer(cohort=None, tables=tables, cohort_manager=cohorts, cohort_name='base')
results = analyzer.run_analysis()
print('Descriptive analysis complete — summary:')
import json
print(json.dumps(results.summary, indent=2, default=str))

# %% [markdown]
## 6. Export results

# %%
output_dir = Path('../output/reports')
output_dir.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
excel_path = output_dir / f'base_cohort_analysis_{timestamp}.xlsx'
results.to_excel(str(excel_path))
print('Saved:', excel_path)

# %% [markdown]
## 7. Export cohorts

# %%
cohort_output_dir = Path('../output/cohorts')
cohort_output_dir.mkdir(parents=True, exist_ok=True)
for name in cohorts.list_cohorts():
    df = cohorts.get_cohort(name)
    path = cohort_output_dir / f"{name}_{timestamp}.csv"
    df.to_csv(path, index=False)
    print('Saved cohort:', path)

# %% [markdown]
## 8. Custom analysis examples

# See `notebooks/02_custom_analysis_example.ipynb` for concise custom analysis patterns (cohort filtering, quick analysis, and small plots).

# %% [markdown]
## 9. End — Summary

# %%
print('='*70)
print('ANALYSIS SESSION SUMMARY')
print('='*70)
print('Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print('Tables loaded:', len(tables))
print('Cohorts created:', len(cohorts.list_cohorts()))
for name in sorted(cohorts.list_cohorts()):
    print(f"  - {name}: {len(cohorts.get_cohort(name)):,} patients")
print('Done')
