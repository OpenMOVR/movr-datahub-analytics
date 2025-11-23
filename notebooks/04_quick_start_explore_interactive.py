# ---
# jupyter:
#   jupytext:
#     notebook_metadata_filter: -kernelspec,-language_info
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
# ---

# %%
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.quick_start_exploratory_cohorts import quick_CohortAnalyzer

# This one line:
# - Loads all Parquet tables
# - Creates CohortManager with base cohort
# - Creates exploratory cohorts for all diseases in config
analyzer = quick_CohortAnalyzer()
tables, cohorts, created = analyzer.run_analysis()

print(f'\nCreated cohorts: {created}')
print(f'Available cohorts: {cohorts.list_cohorts()}')

# %% [markdown]
# ## Get Filtered Tables
#
# The key method: `cohorts.get_filtered_tables(name)`
#
# Instead of manually filtering each table by `FACPATID`, this returns ALL tables with only the patients in your cohort.

# %%
# Get DMD DataHub filtered tables
dmd_tables = cohorts.get_filtered_tables('exploratory_dmd_datahub')

print('\nFiltered tables for DMD DataHub:')
for name, df in dmd_tables.items():
    print(f'  {name}: {len(df):,} rows')

# %%
# Explore DMD demographics
dmd_demo = dmd_tables.get('demographics_maindata')
if dmd_demo is None or dmd_demo.empty:
    print('No DMD demographics available')
else:
    print(f'\nDMD Demographics: {len(dmd_demo):,} patients')
    print('\nGender distribution:')
    print(dmd_demo.get('gender', dmd_demo.columns).value_counts())
    if 'AGE' in dmd_demo.columns:
        print('\nAge statistics:')
        print(dmd_demo['AGE'].describe())

# %%
# Explore DMD encounters
if 'encounter_maindata' in dmd_tables:
    dmd_enc = dmd_tables['encounter_maindata']
    print(f'\nDMD Encounters: {len(dmd_enc):,} total encounters')
    print(f'Unique patients with encounters: {dmd_enc[
].nunique()}')
else:
    print('No encounter table available for DMD cohort')

# %% [markdown]
# ## Compare DMD vs SMA
# Get filtered tables for both cohorts and compare.

# %%
# Compare with SMA if available
if 'exploratory_sma_datahub' in cohorts.list_cohorts():
    sma_tables = cohorts.get_filtered_tables('exploratory_sma_datahub')
    dmd_n = len(dmd_tables.get('demographics_maindata', []))
    sma_n = len(sma_tables.get('demographics_maindata', []))
    print(f'\nCohort Comparison:
  DMD: {dmd_n} patients
  SMA: {sma_n} patients')
    if 'AGE' in dmd_tables.get('demographics_maindata', []):
        print('\nMean Age:')
        print(f'  DMD: {dmd_tables[
][
].mean():.1f} years')
        print(f'  SMA: {sma_tables[
][
].mean():.1f} years')
else:
    print('SMA exploratory cohort not present')

# %% [markdown]
# ## Filter specific tables only
# Get a small subset of tables for a cohort when you don't need everything.

# %%
filtered_subset = cohorts.get_filtered_tables('exploratory_dmd_datahub', tables=['demographics_maindata','encounter_maindata'])
print(f'\nFiltered subset: {list(filtered_subset.keys())}')

# %% [markdown]
# ## Quick Reference
# Use these commands in any notebook cell to quickly follow the flow above.
