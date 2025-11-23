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
# # MOVR DataHub Analytics - Getting Started
#
# **First Analysis Notebook**
#
# This notebook demonstrates:
# 1. Loading MOVR data from Parquet files
# 2. Validating enrollment
# 3. Creating and filtering cohorts
# 4. Running descriptive analyses
# 5. Exporting results
#
# ---
#
# ## Setup

# %%
# Import required packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

# MOVR package imports
from movr import load_data, CohortManager, DescriptiveAnalyzer
from movr.config import get_config

# Configure plotting
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
# %matplotlib inline

# Display settings
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows', 100)

print("Imports complete")

# %% [markdown]
# ---
#
# ## 1. Load Data
#
# Load all Parquet files from `data/parquet/` directory.

# %%
# Load all available tables
tables = load_data(verbose=True)

print(f"\n{'='*60}")
print(f"Loaded {len(tables)} tables:")
for table_name in tables.keys():
    n_rows = len(tables[table_name])
    n_cols = len(tables[table_name].columns)
    print(f"  • {table_name}: {n_rows:,} rows × {n_cols} columns")
print(f"{'='*60}")

# %% [markdown]
# ### Quick Data Inspection

# %%
# Inspect Demographics table
if "demographics_maindata" in tables:
    demographics = tables["demographics_maindata"]
    
    print("Demographics Table - First 5 rows:")
    display(demographics.head())
    
    print(f"\nTotal Demographics records: {len(demographics):,}")
    
    print("\nColumn Data Types:")
    display(demographics.dtypes)
    
    print("\nBasic Statistics:")
    display(demographics.describe(include='all'))

# %%
# Inspect Encounter table
if "encounter_maindata" in tables:
    encounter = tables["encounter_maindata"]
    
    print("Encounter Table - First 5 rows:")
    display(encounter.head())
    
    print(f"\nTotal Encounters: {len(encounter):,}")
    print(f"Unique Patients: {encounter['FACPATID'].nunique():,}")

# %% [markdown]
# ---
#
# ## 2. Enrollment Validation
#
# Validate that patients have all 3 required forms:
# - Demographics_MainData
# - Diagnosis_MainData
# - Encounter_MainData

# %%
from movr.cohorts import EnrollmentValidator

# Create validator
validator = EnrollmentValidator(tables)

# Get validation report
report = validator.validate_enrollment()

print("="*60)
print("ENROLLMENT VALIDATION REPORT")
print("="*60)
print(f"\nTotal Unique Patients: {report['total_unique_patients']:,}")
print(f"Enrolled Patients (with all 3 forms): {report['enrolled_count']:,}")
print(f"Enrollment Rate: {report['enrolled_count']/report['total_unique_patients']*100:.1f}%")

print("\nPatients by Form:")
for form_name, count in report['form_counts'].items():
    print(f"  • {form_name}: {count:,} patients")

print("\nPatients Missing Each Form:")
for form_name, count in report['missing_by_form'].items():
    if count > 0:
        print(f"  • Missing {form_name}: {count:,} patients")

print("="*60)

# %% [markdown]
# ---
#
# ## 3. Create Base Cohort
#
# Create the base enrolled cohort with all required forms.

# %%
# Initialize cohort manager
# CohortManager now automatically:
# - Calculates AGE from 'dob' field
# - Resolves canonical field names (disease -> dstype, gender -> gender, etc.)
# - Supports registry filtering (USNDR vs DataHub)

cohorts = CohortManager(tables)

# Create base cohort (requires demographics, diagnosis, and encounter forms)
base_cohort = cohorts.create_base_cohort(name="base")

print(f"\nBase Cohort Created: {len(base_cohort):,} patients")

# Get summary - now includes registry distribution and properly resolved fields
summary = cohorts.get_cohort_summary("base")
print("\nBase Cohort Summary:")
print(f"  Total Patients: {summary['n_patients']:,}")

if summary.get('gender_distribution'):
    print("\n  Gender Distribution:")
    for gender, count in summary['gender_distribution'].items():
        print(f"    {gender}: {count:,} ({count/summary['n_patients']*100:.1f}%)")

if summary.get('disease_distribution'):
    print("\n  Disease Distribution:")
    for disease, count in summary['disease_distribution'].items():
        print(f"    {disease}: {count:,} ({count/summary['n_patients']*100:.1f}%)")

if summary.get('age_stats'):
    print("\n  Age Statistics (calculated from DOB):")
    age_stats = summary['age_stats']
    print(f"    Mean: {age_stats['mean']:.1f} years")
    print(f"    Median: {age_stats['median']:.1f} years")
    print(f"    Range: {age_stats['min']:.0f} - {age_stats['max']:.0f} years")

if summary.get('registry_distribution'):
    print("\n  Registry Distribution:")
    for registry, count in summary['registry_distribution'].items():
        print(f"    {registry}: {count:,} ({count/summary['n_patients']*100:.1f}%)")

# %%
## Key Methods of CohortManager

# create_base_cohort()     -> df['FACPATID']    Create initial cohort with enrollment validation
# filter_cohort()          Filter by field values or custom function
# get_cohort()             Retrieve cohort by name
# get_cohort_data()        Get cohort with demographics data (includes calculated AGE)
# list_cohorts()           List all created cohorts
# get_cohort_summary()     Get demographics summary (gender, age, disease, registry)
# export_cohort()          Export to CSV/Excel/Parquet

## Field Name Resolution
# CohortManager uses canonical field names that map to actual columns:
#   - disease  -> dstype (source: demographics_maindata)
#   - gender   -> gender (source: demographics_maindata)
#   - age      -> AGE (derived from dob, calculated automatically)
#   - registry -> usndr (True=USNDR, else=DataHub)

## Filter Examples
# filters={'disease': 'DMD'}                    # Single disease
# filters={'disease': ['DMD', 'BMD']}           # Multiple diseases
# filters={'age': {'min': 0, 'max': 18}}        # Age range
# filters={'registry': True}                    # USNDR only
# filters={'registry': False}                   # DataHub only

# Check the actual field values in demographics
dem = tables['demographics_maindata']
print("Actual field names and sample values:")
print(f"  dstype (disease): {dem['dstype'].unique().tolist()}")
print(f"  gender: {dem['gender'].unique().tolist()}")
print(f"  usndr (registry): {dem['usndr'].unique().tolist()}")

# %% [markdown]
# ### Visualize Base Cohort
#
# Use `get_cohort_data()` to get cohort with demographics including calculated AGE field.

# %%
# Get cohort data with demographics (includes calculated AGE)
base_demographics = cohorts.get_cohort_data("base", include_demographics=True)

print(f"Cohort data shape: {base_demographics.shape}")
print(f"Columns include AGE (calculated): {'AGE' in base_demographics.columns}")

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Base Cohort Overview', fontsize=16, fontweight='bold')

# Disease distribution (using actual 'dstype' field, resolved by CohortManager)
if 'dstype' in base_demographics.columns:
    disease_counts = base_demographics['dstype'].value_counts()
    axes[0, 0].pie(disease_counts.values, labels=disease_counts.index, autopct='%1.1f%%')
    axes[0, 0].set_title('Disease Distribution (dstype)')

# Gender distribution (actual field name is 'gender')
if 'gender' in base_demographics.columns:
    gender_counts = base_demographics['gender'].value_counts()
    axes[0, 1].bar(gender_counts.index, gender_counts.values, color=['steelblue', 'coral', 'gray', 'green', 'purple'])
    axes[0, 1].set_title('Gender Distribution')
    axes[0, 1].set_ylabel('Count')
    axes[0, 1].tick_params(axis='x', rotation=45)

# Age distribution (calculated from 'dob' by CohortManager)
if 'AGE' in base_demographics.columns:
    axes[1, 0].hist(base_demographics['AGE'].dropna(), bins=30, edgecolor='black', color='teal')
    axes[1, 0].set_title('Age Distribution (calculated from dob)')
    axes[1, 0].set_xlabel('Age (years)')
    axes[1, 0].set_ylabel('Count')
    axes[1, 0].axvline(base_demographics['AGE'].mean(), color='red', linestyle='--', 
                       label=f"Mean: {base_demographics['AGE'].mean():.1f}")
    axes[1, 0].legend()

# Registry distribution (usndr: True=USNDR, else=DataHub)
if 'usndr' in base_demographics.columns:
    usndr_true = (base_demographics['usndr'] == True).sum()
    datahub = len(base_demographics) - usndr_true
    axes[1, 1].bar(['DataHub', 'USNDR'], [datahub, usndr_true], color=['#3498db', '#e74c3c'])
    axes[1, 1].set_title('Registry Source (usndr field)')
    axes[1, 1].set_ylabel('Count')
    for i, (label, val) in enumerate(zip(['DataHub', 'USNDR'], [datahub, usndr_true])):
        axes[1, 1].annotate(f'{val:,}', xy=(i, val), ha='center', va='bottom')

plt.tight_layout()

# Create output directory if needed
Path('../output/figures').mkdir(parents=True, exist_ok=True)
plt.savefig('../output/figures/base_cohort_overview.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n✓ Visualization saved to: output/figures/base_cohort_overview.png")

# %% [markdown]
# ---
#
# ## 4. Create Registry and Disease-Specific Cohorts
#
# The CohortManager now supports canonical field names that automatically resolve to actual columns.
#
# **Priority 1: Registry Cohorts (USNDR vs DataHub)**
# - `{'registry': True}` - USNDR participants only
# - `{'registry': False}` - DataHub participants only
#
# **Priority 2: Disease Cohorts**
# - `{'disease': 'DMD'}` - Single disease
# - `{'disease': ['DMD', 'BMD']}` - Multiple diseases

# %% [markdown]
# ### Filter by Age Groups
#
# Age is automatically calculated from `dob` field by CohortManager.

# %% [markdown]
# - Age is calculated from 'dob' field automatically by CohortManager
# - Use the canonical 'age' field name with range filters
#
# ### Pediatric (0-18 years)
# ```python
# pediatric = cohorts.filter_cohort(
#     source_cohort="base",
#     name="pediatric",
#     filters={"age": {"min": 0, "max": 18}}  # Uses calculated AGE field
# )
# ```
# ### Adult (18+ years)
# ```python
# adult = cohorts.filter_cohort(
#     source_cohort="base",
#     name="adult",
#     filters={"age": {"min": 18}}  # No max = no upper limit
# )
#
# print(f"Age-Based Cohorts:")
# print(f"  Pediatric (0-18): {len(pediatric):,} patients")
# print(f"  Adult (18+): {len(adult):,} patients")
# ```
# ### DMD Pediatric (common use case) - combining disease and age
# ```python
# dmd_pediatric = cohorts.filter_cohort(
#     source_cohort="dmd",  # Start from DMD cohort
#     name="dmd_pediatric",
#     filters={"age": {"min": 0, "max": 18}}
# )
# print(f"\n  DMD Pediatric: {len(dmd_pediatric):,} patients")
# ```
# ### Get summary of DMD pediatric cohort
# ```python
# dmd_ped_summary = cohorts.get_cohort_summary("dmd_pediatric")
# print(f"\nDMD Pediatric Summary:")
# print(f"  Patients: {dmd_ped_summary['n_patients']:,}")
# if dmd_ped_summary.get('age_stats'):
#     print(f"  Age: {dmd_ped_summary['age_stats']['mean']:.1f} ± range {dmd_ped_summary['age_stats']['min']:.0f}-{dmd_ped_summary['age_stats']['max']:.0f}")
# if dmd_ped_summary.get('registry_distribution'):
#     print(f"  USNDR: {dmd_ped_summary['registry_distribution']['USNDR']:,}, DataHub: {dmd_ped_summary['registry_distribution']['DataHub']:,}")
# ```

# %%
# Create a custom cohort: DMD patients from DataHub only (not USNDR)
working_cohort = cohorts.filter_cohort(
    source_cohort='base',
    name = 'dmd_datahub_cohort',
    filters={ 
        'disease': 'DMD',
        'registry': False}  # USNDR only
)

dmd_pediatric = cohorts.filter_cohort(
    source_cohort="dmd_datahub_cohort",  # Start from DMD DataHub cohort
    name="dmd_pediatric",
    filters={"age": {"min": 0, "max": 18}}  # Uses calculated AGE field
)

# working_cohort.info() # reminder - working_cohort is a DataFrame for just FACPATIDs

# List all created cohorts with patient counts
print("All Created Cohorts:")
print("="*50)
all_cohorts = cohorts.list_cohorts()
for cohort_name in sorted(all_cohorts):
    cohort = cohorts.get_cohort(cohort_name)
    print(f"  {cohort_name:20s}: {len(cohort):>6,} patients")
print("="*50)
print(f"Total cohorts: {len(all_cohorts)}")

# %% [markdown]
# ---
#
# ## 4.1 Get Filtered Tables for a Cohort
#
# Use `get_filtered_tables()` to get ALL tables filtered to a cohort's patients.
#
# This is the easiest way to get analysis-ready data - instead of manually filtering each table by FACPATID, this returns all tables with only your cohort's patients.

# %%
# Get all tables filtered to DMD DataHub cohort
dmd_filtered = cohorts.get_filtered_tables('dmd_datahub_cohort')

print(f"Filtered {len(dmd_filtered)} tables to DMD DataHub cohort")
print(f"\nTable row counts (filtered vs original):")
for name, df in dmd_filtered.items():
    original_count = len(tables.get(name, []))
    print(f"  {name}: {len(df):,} rows (from {original_count:,})")

# Now you can explore any table - it only has DMD patients
print(f"\n--- Quick exploration of filtered data ---")
print(f"DMD demographics: {len(dmd_filtered['demographics_maindata'])} patients")
if 'encounter_maindata' in dmd_filtered:
    print(f"DMD encounters: {len(dmd_filtered['encounter_maindata']):,} records")

# %%
print(f'{type(dmd_filtered)}')
list(dmd_filtered.keys())

# %% [markdown]
# ---
#
# ## 5. Run Descriptive Analysis
#
# Compute descriptive statistics for a cohort.

# %%
# Analyze the base cohort
analyzer = DescriptiveAnalyzer(cohort=None, tables=tables, cohort_manager=cohorts, cohort_name='dmd_datahub_cohort')
results = analyzer.run_analysis()

print("="*60)
print("DESCRIPTIVE ANALYSIS RESULTS")
print("="*60)
print(f"\nCohort: Base (All Enrolled Patients)")
print(f"Total Patients: {results.summary['n_patients']:,}")

# Display summary
import json
print("\nSummary Statistics:")
print(json.dumps(results.summary, indent=2, default=str))


# %%
# If DMD pediatric cohort exists, analyze it
if 'dmd_pediatric' in cohorts.list_cohorts():
    # prefer CohortManager prepared cohort data
    analyzer_dmd = DescriptiveAnalyzer(cohort=None, tables=tables, cohort_manager=cohorts, cohort_name='dmd_pediatric')
    results_dmd = analyzer_dmd.run_analysis()

    print("="*60)
    print("DMD PEDIATRIC COHORT ANALYSIS")
    print("="*60)
    print(f"\nTotal Patients: {results_dmd.summary['n_patients']:,}")

    if 'age_stats' in results_dmd.summary:
        age_stats = results_dmd.summary['age_stats']
        print(f"\nAge Statistics:")
        print(f"  Mean: {age_stats['mean']:.1f} years")
        print(f"  Median: {age_stats['median']:.1f} years")
        print(f"  Range: {age_stats['min']:.0f} - {age_stats['max']:.0f} years")
        print(f"  Std Dev: {age_stats['std']:.1f} years")

    if 'gender_distribution' in results_dmd.summary:
        print(f"\nGender Distribution:")
        for gender, count in results_dmd.summary['gender_distribution'].items():
            pct = count / results_dmd.summary['n_patients'] * 100
            print(f"  {gender}: {count} ({pct:.1f}%)")


# %% [markdown]
# ---
#
# ## 6. Export Results
#
# Export analysis results to various formats.

# %%
# Create output directory if it doesn't exist
output_dir = Path("../output/reports")
output_dir.mkdir(parents=True, exist_ok=True)

# Export base cohort analysis
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Excel export
excel_path = output_dir / f"dmd_datahub_cohort_analysis_{timestamp}.xlsx"
results.to_excel(str(excel_path))
print(f"Excel report saved: {excel_path}")

# JSON export
json_path = output_dir / f"dmd_datahub_cohort_analysis_{timestamp}.json"
results.to_json(str(json_path))
print(f"JSON report saved: {json_path}")

# CSV export (data only)
csv_path = output_dir / f"dmd_datahub_cohort_data_{timestamp}.csv"
results.to_csv(str(csv_path))
print(f"CSV data saved: {csv_path}")

# %%
# Export DMD pediatric analysis if available
if 'dmd_pediatric' in cohorts.list_cohorts():
    excel_path_dmd = output_dir / f"dmd_pediatric_analysis_{timestamp}.xlsx"
    results_dmd.to_excel(str(excel_path_dmd))
    print(f"✓ DMD Pediatric Excel report saved: {excel_path_dmd}")

# %% [markdown]
# ---
#
# ## 7. Export Cohorts for Future Use

# %%
# Export cohorts as CSV files
cohort_output_dir = Path("../output/cohorts")
cohort_output_dir.mkdir(parents=True, exist_ok=True)

for cohort_name in cohorts.list_cohorts():
    cohort = cohorts.get_cohort(cohort_name)
    cohort_path = cohort_output_dir / f"{cohort_name}_{timestamp}.csv"
    cohort.to_csv(cohort_path, index=False)
    print(f"✓ Cohort '{cohort_name}' saved: {cohort_path}")

# %% [markdown]
# ---
#
# ## 8. Custom Analysis Example
#
# Example of custom analysis using the cohort data.

# %%
# Custom analysis moved → see dedicated notebook

#Custom analysis examples were moved to `notebooks/02_custom_analysis_example.ipynb`. This keeps the Getting Started notebook focused and concise — open the new notebook for quick, copyable examples for cohort-level analyses and plotting.


# %% [markdown]
# ---
#
# ## Next Steps
#
# 1. **Review the generated reports** in `output/reports/`
# 2. **Check the visualizations** in `output/figures/`
# 3. **Explore cohort files** in `output/cohorts/`
# 4. **Modify filters and create custom cohorts** for your specific research questions
# 5. **Add custom analysis code** in new cells below
#
# ### Useful Resources
#
# - **Data Wrangling Rules**: See `../DATA_WRANGLING_RULES.md`
# - **Architecture Details**: See `../ARCHITECTURE_PLAN.md`
# - **API Documentation**: Check docstrings with `help(function_name)`
# - **Getting Started Guide**: See `../GETTING_STARTED.md`
#
# ### Things to remember to do
#
# 1. **Save this notebook with outputs** for documentation
# 2. **Create copies** for different analyses (e.g., `02_dmd_analysis.ipynb`)
# 3. **Clear outputs before committing** to git
#
# ---
#
# **Cheers!**

# %% [markdown]
#
