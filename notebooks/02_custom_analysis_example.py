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

# %% [markdown]
# # 02 ----- Custom Analysis

# %% [markdown]
# **Quick CLI:** the helper script `scripts/make_exploratory_cohort.py` builds an exploratory cohort quickly from `config/cohort_definitions.yaml`. By default it creates a DMD + DataHub cohort (usndr=False).
#
# Example:
# ```bash
# python scripts/make_exploratory_cohort.py --disease DMD --registry False --name exploratory_dmd_datahub
# ```
#

# %%
# Setup: imports and convenient helpers
import pandas as pd
import matplotlib.pyplot as plt
from movr import load_data
from movr.cohorts.manager import CohortManager
from movr.analytics.descriptive import DescriptiveAnalyzer

# Short display settings (optional)
pd.set_option('display.max_columns', 40)

print('Ready')

# %%
# 1. Load only what you need (use load_data())
tables = load_data(verbose=False)  # already loads Parquet into DataFrames
cohorts = CohortManager(tables)
# Create base cohort (if not already created)
if 'base' not in cohorts.list_cohorts():
    cohorts.create_base_cohort(name='base')

print('Tables loaded:', len(tables))
print('Cohorts:', cohorts.list_cohorts())

# %% [markdown]
# ## Get Filtered Tables
#
# The easiest way to explore cohort data: `cohorts.get_filtered_tables(name)`
#
# Returns ALL tables filtered to your cohort's patients - no manual FACPATID filtering needed.

# %%
# Create a DMD DataHub cohort
if 'dmd_datahub' not in cohorts.list_cohorts():
    cohorts.filter_cohort(
        source_cohort='base',
        name='dmd_datahub',
        filters={'disease': 'DMD', 'registry': False}
    )

# Get ALL tables filtered to this cohort
dmd = cohorts.get_filtered_tables('dmd_datahub')

print(f"Got {len(dmd)} tables filtered to DMD DataHub cohort")
print(f"\nFiltered table sizes:")
for name, df in list(dmd.items())[:5]:  # Show first 5
    print(f"  {name}: {len(df):,} rows")

# Now explore any table - only DMD patients
print(f"\n--- DMD Data Ready to Explore ---")
print(f"Demographics: {len(dmd['demographics_maindata'])} patients")
print(f"Gender distribution:\n{dmd['demographics_maindata']['gender'].value_counts()}")

# %% [markdown]
# ## Quick example: DMD pediatric cohort and summary
# Create a DMD pediatric cohort (0–18 years) then run a short descriptive analysis using the centrally-prepared cohort data.

# %%
# Create or update disease/age cohort (non-destructive)
if 'dmd_pediatric' not in cohorts.list_cohorts():
    cohorts.filter_cohort(source_cohort='base', name='dmd_pediatric', filters={'disease': 'DMD', 'age': {'min': 0, 'max': 18}})

# Use CohortManager-prepared cohort data for analysis
analyzer = DescriptiveAnalyzer(cohort=None, tables=tables, cohort_manager=cohorts, cohort_name='dmd_pediatric')
results = analyzer.run_analysis()
print('DMD pediatric n =', results.summary['n_patients'])
# concise disease + gender counts
print('Disease distribution (sample):', results.summary.get('disease_distribution'))
print('Gender distribution (sample):', results.summary.get('gender_distribution'))

# %% [markdown]
# ## Quick visualization (subsample for speed)
# Plot age distribution for the cohort (sample if large). Keep visuals small and reproducible.

# %%
df = cohorts.get_cohort_data('dmd_pediatric', include_demographics=True)
if df is None or df.empty:
    print('No cohort data available; run the cells above')
else:
    # sample if big
    plot_df = df.sample(min(5000, len(df))) if len(df) > 5000 else df
    if 'AGE' in plot_df.columns:
        plt.hist(plot_df['AGE'].dropna(), bins=20, color='teal')
        plt.title('DMD pediatric — age distribution (sample)')
        plt.xlabel('Age (years)')
        plt.show()
    else:
        print('AGE not present in cohort data')
