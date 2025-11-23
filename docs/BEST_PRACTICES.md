# Best Practices Guide

**Standards and recommendations for working with MOVR DataHub Analytics**

This document provides best practices for data handling, analysis workflows, code quality, and team collaboration when using or contributing to MOVR DataHub Analytics.

---

## Table of Contents

1. [Data Handling](#1-data-handling)
2. [Analysis Workflow](#2-analysis-workflow)
3. [Code Quality](#3-code-quality)
4. [Documentation](#4-documentation)
5. [Testing](#5-testing)
6. [Collaboration](#6-collaboration)
7. [Security & Privacy](#7-security--privacy)
8. [Performance](#8-performance)

---

## 1. Data Handling

### 1.1 Source Data Management

✅ **DO:**
- **Treat Excel files as read-only source of truth**
  ```bash
  # Keep source data separate from analysis code
  ~/MDA/
  ├── movr-datahub-analytics/  # Code repository
  └── source-movr-data/        # Data (not in git)
  ```
- **Back up original data regularly** (external drive, secure cloud storage)
- **Document data provenance** (where it came from, when received)
- **Version control your configuration**, not your data files

❌ **DON'T:**
- Never edit original Excel files directly
- Never commit data files to git (Excel, Parquet, CSV)
- Never store data in the code repository
- Never share data via git or public repositories

### 1.2 Data Conversions

✅ **DO:**
- **Always use the conversion pipeline**
  ```bash
  movr convert  # Use the official tool
  ```
- **Check audit logs after conversion**
  ```bash
  ls data/.audit/
  cat data/.audit/conversion_YYYYMMDD_HHMMSS.json
  ```
- **Validate data after conversion**
  ```bash
  movr validate
  ```
- **Keep Parquet files in sync with source Excel**
  - Re-run `movr convert` when Excel files are updated

❌ **DON'T:**
- Don't manually create Parquet files
- Don't modify Parquet files directly
- Don't skip validation
- Don't mix data from different conversion runs

### 1.3 Data Wrangling

✅ **DO:**
- **Use YAML-configured rules** for reproducibility
  ```yaml
  # config/wrangling_rules.yaml
  rules:
    - name: "descriptive_name"
      tables: ["specific_table"]
      action: "specific_action"
  ```
- **Document custom transformations** as plugins
  ```python
  # plugins/my_transform.py
  @register_plugin("my_custom_rule")
  def my_transform(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
      """Clear documentation of what this does."""
      # Implementation with comments
      return df
  ```
- **Log all transformations** in audit trail
- **Use appropriate strictness mode**
  - `strict`: For production, critical analyses
  - `permissive`: For exploratory analysis
  - `interactive`: For initial data exploration

❌ **DON'T:**
- Don't apply transformations without documenting them
- Don't modify data "just to see what happens"
- Don't skip wrangling rules in production
- Don't hardcode data fixes (make them rules)

### 1.4 Missing Data

✅ **DO:**
- **Standardize missing values** using wrangling rules
  ```yaml
  rules:
    - name: "standardize_missing"
      action: "standardize_na"
      values: ["", "NA", "N/A", "NULL", "Unknown"]
  ```
- **Document why data is missing** when known
- **Report missingness patterns**
  ```python
  missing_summary = df.isnull().sum()
  print(f"Missing data report:\n{missing_summary}")
  ```
- **Be explicit about imputation** if used
  ```python
  # Document imputation strategy
  df['AGE_IMPUTED'] = df['AGE'].fillna(df['AGE'].median())
  df['AGE_WAS_MISSING'] = df['AGE'].isnull()  # Flag
  ```

❌ **DON'T:**
- Don't assume missing = zero
- Don't impute without documenting
- Don't drop records with missing data without justification
- Don't hide missing data in analyses

---

## 2. Analysis Workflow

### 2.1 Reproducible Analyses

✅ **DO:**
- **Use consistent project structure**
  ```python
  from movr import load_data, CohortManager, DescriptiveAnalyzer

  # 1. Load data
  tables = load_data()

  # 2. Create cohort
  cohorts = CohortManager(tables)
  base = cohorts.create_base_cohort()

  # 3. Filter
  my_cohort = cohorts.filter_cohort("base", "my_cohort", filters={...})

  # 4. Analyze
  # Prefer using CohortManager-prepared cohort data when available (includes derived fields like AGE)
  analyzer = DescriptiveAnalyzer(cohort=None, tables=tables, cohort_manager=cohorts, cohort_name='my_cohort')
  results = analyzer.run_analysis()

  # 5. Export
  results.to_excel("output/my_analysis.xlsx")
  ```

- **Set random seeds** for reproducibility
  ```python
  import numpy as np
  np.random.seed(42)
  ```

- **Document analysis parameters**
  ```python
  config = {
      'cohort': 'dmd_pediatric',
      'date_range': ('2020-01-01', '2023-12-31'),
      'min_encounters': 3,
      'exclusions': ['missing_primary_dx']
  }
  ```

- **Version your analysis notebooks**
  ```bash
  # Clear output before committing
  jupyter nbconvert --clear-output --inplace my_analysis.ipynb
  git add my_analysis.ipynb
  git commit -m "Add DMD pediatric analysis"
  ```

❌ **DON'T:**
- Don't hardcode file paths
- Don't use random operations without seeds
- Don't commit notebooks with output/data
- Don't skip documentation of analysis choices

### 2.2 Cohort Building

✅ **DO:**
- **Start with base enrollment cohort**
  ```python
  cohorts = CohortManager(tables)
  base = cohorts.create_base_cohort()  # Validates enrollment
  ```

- **Build cohorts incrementally**
  ```python
  # Start broad
  dmd_all = cohorts.filter_cohort("base", "dmd_all",
                                   filters={"DISEASE": "DMD"})

  # Then narrow down
  dmd_peds = cohorts.filter_cohort("dmd_all", "dmd_peds",
                                    filters={"AGE": (0, 18)})

  dmd_ambulatory = cohorts.filter_cohort("dmd_peds", "dmd_ambulatory",
                                          filters={"AMBULATORY": True})
  ```

- **Document cohort definitions**
  ```yaml
  # config/cohort_definitions.yaml
  cohorts:
    - name: "dmd_pediatric"
      description: "DMD patients under 18 years old"
      source: "base"
      filters:
        DISEASE: "DMD"
        AGE: {min: 0, max: 18}
  ```

- **Report cohort sizes at each step**
  ```python
  print(f"Base cohort: {len(base)} patients")
  print(f"DMD: {len(dmd_all)} patients")
  print(f"DMD pediatric: {len(dmd_peds)} patients")
  ```

❌ **DON'T:**
- Don't skip enrollment validation
- Don't create overly complex filters in one step
- Don't forget to document exclusion criteria
- Don't lose track of cohort hierarchies

### 2.3 Statistical Analysis

✅ **DO:**
- **Report sample sizes**
  ```python
  print(f"n = {len(cohort)} patients")
  print(f"n = {len(encounters)} encounters")
  ```

- **Check assumptions**
  ```python
  # Check normality before parametric tests
  from scipy import stats
  statistic, p_value = stats.shapiro(data)
  ```

- **Use appropriate tests**
  ```python
  # Categorical: Chi-square
  # Continuous + normal: t-test
  # Continuous + non-normal: Mann-Whitney U
  ```

- **Report effect sizes**, not just p-values
  ```python
  # Calculate and report Cohen's d, odds ratios, etc.
  ```

- **Adjust for multiple comparisons** when needed
  ```python
  from statsmodels.stats.multitest import multipletests
  _, p_adjusted, _, _ = multipletests(p_values, method='bonferroni')
  ```

❌ **DON'T:**
- Don't report only p-values without context
- Don't use parametric tests without checking assumptions
- Don't ignore multiple comparison issues
- Don't claim causation from observational data

---

## 3. Code Quality

### 3.1 Style Guidelines

✅ **DO:**
- **Follow PEP 8**
  ```bash
  # Format code
  black src/ tests/

  # Sort imports
  isort src/ tests/

  # Check linting
  flake8 src/ tests/
  ```

- **Use meaningful names**
  ```python
  # Good
  def calculate_age_at_diagnosis(birth_date, diagnosis_date):
      ...

  # Bad
  def calc(d1, d2):
      ...
  ```

- **Write self-documenting code**
  ```python
  # Good: Clear intent
  dmd_patients = cohort[cohort['DISEASE'] == 'DMD']

  # Bad: Cryptic
  df2 = df[df['d'] == 'DMD']
  ```

- **Use type hints**
  ```python
  from typing import List, Dict, Optional
  import pandas as pd

  def filter_cohort(
      df: pd.DataFrame,
      filters: Dict[str, any]
  ) -> pd.DataFrame:
      ...
  ```

❌ **DON'T:**
- Don't use single-letter variable names (except loops)
- Don't write overly complex one-liners
- Don't ignore linting warnings
- Don't commit code with `# TODO` without an issue

### 3.2 Functions and Classes

✅ **DO:**
- **Keep functions focused** (do one thing well)
  ```python
  # Good: Single responsibility
  def calculate_age(birth_date: str, reference_date: str) -> int:
      """Calculate age in years."""
      # Implementation
      return age

  def filter_by_age(df: pd.DataFrame, min_age: int, max_age: int) -> pd.DataFrame:
      """Filter DataFrame by age range."""
      # Implementation
      return filtered_df
  ```

- **Write pure functions** when possible
  ```python
  # Good: No side effects
  def add_age_column(df: pd.DataFrame) -> pd.DataFrame:
      df = df.copy()  # Don't modify input
      df['AGE'] = calculate_age(df['BIRTH_DATE'])
      return df
  ```

- **Use docstrings**
  ```python
  def create_cohort(tables: Dict[str, pd.DataFrame]) -> pd.DataFrame:
      """Create base enrollment cohort.

      Args:
          tables: Dictionary mapping table names to DataFrames.

      Returns:
          DataFrame with FACPATID and enrollment metadata.

      Raises:
          ValueError: If required tables are missing.

      Example:
          >>> tables = load_data()
          >>> cohort = create_cohort(tables)
          >>> print(len(cohort))
      """
      ...
  ```

❌ **DON'T:**
- Don't create functions longer than ~50 lines
- Don't modify input parameters (use copies)
- Don't create classes with only one method (use function)
- Don't skip docstrings for public functions

### 3.3 Error Handling

✅ **DO:**
- **Validate inputs**
  ```python
  def filter_cohort(df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
      if df is None or df.empty:
          raise ValueError("DataFrame cannot be empty")

      required_cols = ['FACPATID']
      missing = [c for c in required_cols if c not in df.columns]
      if missing:
          raise ValueError(f"Missing required columns: {missing}")

      # Process...
  ```

- **Use specific exceptions**
  ```python
  # Good
  raise ValueError("Age must be between 0 and 120")

  # Bad
  raise Exception("Invalid input")
  ```

- **Provide helpful error messages**
  ```python
  if not config_file.exists():
      raise FileNotFoundError(
          f"Configuration file not found: {config_file}\n"
          f"Run 'movr setup' to create configuration."
      )
  ```

- **Log errors appropriately**
  ```python
  import logging
  logger = logging.getLogger(__name__)

  try:
      result = risky_operation()
  except SpecificError as e:
      logger.error(f"Operation failed: {e}")
      # Handle or re-raise
  ```

❌ **DON'T:**
- Don't use bare `except:` clauses
- Don't silently swallow exceptions
- Don't provide cryptic error messages
- Don't catch exceptions you can't handle

---

## 4. Documentation

### 4.1 Code Documentation

✅ **DO:**
- **Document the "why", not just the "what"**
  ```python
  # Good
  # Use median instead of mean because data is skewed
  imputed_value = df['AGE'].median()

  # Bad
  # Set x to median
  x = df['AGE'].median()
  ```

- **Update docs when code changes**
- **Include examples in docstrings**
- **Document assumptions**
  ```python
  def calculate_followup_time(encounters: pd.DataFrame) -> pd.Series:
      """Calculate follow-up time in days.

      Assumptions:
      - Encounters are sorted by date
      - First encounter is baseline
      - Last encounter is end of follow-up
      """
      ...
  ```

❌ **DON'T:**
- Don't write obvious comments
  ```python
  # Bad: Obvious
  i = i + 1  # Increment i

  # Good: Adds context
  i += 1  # Move to next patient in cohort
  ```
- Don't leave outdated comments
- Don't comment out large blocks of code (delete it)

### 4.2 Analysis Documentation

✅ **DO:**
- **Document analysis decisions**
  ```markdown
  ## Exclusion Criteria

  We excluded patients with:
  1. Missing primary diagnosis (n=45)
  2. Less than 2 follow-up visits (n=23)
  3. Age > 80 at enrollment (n=8)

  **Rationale**: These criteria ensure sufficient data for longitudinal analysis.
  ```

- **Include methodology**
  ```markdown
  ## Statistical Methods

  - Continuous variables: Median (IQR), Mann-Whitney U test
  - Categorical variables: n (%), Chi-square test
  - Significance level: α = 0.05 (Bonferroni correction applied)
  ```

- **Describe data sources**
  ```markdown
  ## Data Sources

  - Demographics: Demographics_noPHI.xlsx (received 2025-01-15)
  - Encounters: Encounter.xlsx (received 2025-01-15)
  - Diagnosis: Diagnosis.xlsx (received 2025-01-15)
  ```

❌ **DON'T:**
- Don't skip documenting data cleaning steps
- Don't forget to document software versions
- Don't omit null findings (report them too)

---

## 5. Testing

### 5.1 Test Coverage

✅ **DO:**
- **Write tests for new features**
  ```python
  def test_cohort_creation():
      """Test base cohort creation."""
      tables = create_sample_tables()
      cohorts = CohortManager(tables)
      base = cohorts.create_base_cohort()

      assert len(base) > 0
      assert 'FACPATID' in base.columns
  ```

- **Test edge cases**
  ```python
  def test_filter_empty_cohort():
      """Test filtering an empty cohort."""
      empty_df = pd.DataFrame(columns=['FACPATID'])
      result = filter_cohort(empty_df, {})
      assert len(result) == 0
  ```

- **Use fixtures for test data**
  ```python
  @pytest.fixture
  def sample_demographics():
      return pd.DataFrame({
          'FACPATID': ['P001', 'P002', 'P003'],
          'AGE': [10, 15, 12],
          'DISEASE': ['DMD', 'DMD', 'SMA']
      })
  ```

- **Run tests before committing**
  ```bash
  pytest
  ```

❌ **DON'T:**
- Don't skip writing tests
- Don't only test the "happy path"
- Don't commit broken tests
- Don't ignore failing tests

### 5.2 Test Best Practices

✅ **DO:**
- **Test one thing per test**
- **Use descriptive test names**
  ```python
  def test_age_filter_excludes_patients_outside_range():
      ...
  ```
- **Arrange-Act-Assert pattern**
  ```python
  def test_example():
      # Arrange: Set up test data
      df = create_test_data()

      # Act: Perform operation
      result = perform_operation(df)

      # Assert: Check results
      assert result == expected_value
  ```

❌ **DON'T:**
- Don't write tests that depend on each other
- Don't test implementation details
- Don't skip assertions

---

## 6. Collaboration

### 6.1 Version Control

✅ **DO:**
- **Commit often with clear messages**
  ```bash
  git commit -m "feat: Add DMD pediatric cohort filter"
  ```

- **Use branches for features**
  ```bash
  git checkout -b feature/survival-analysis
  ```

- **Keep commits atomic** (one logical change per commit)

- **Write descriptive commit messages**
  ```
  feat: Add survival analysis module

  - Implement Kaplan-Meier estimator
  - Add log-rank test for group comparison
  - Include example notebook

  Closes #45
  ```

❌ **DON'T:**
- Don't commit large changes without explanation
- Don't use vague messages like "fixed stuff"
- Don't commit unrelated changes together
- Don't commit directly to main/master

### 6.2 Code Review

✅ **DO:**
- **Review code for:**
  - Correctness
  - Clarity
  - Test coverage
  - Documentation
  - Performance

- **Provide constructive feedback**
  ```
  Good: "Consider using a vectorized operation here for better performance"
  Bad: "This code is slow"
  ```

- **Ask questions**
  ```
  "Why did you choose approach X over Y?"
  "Have you considered edge case Z?"
  ```

- **Approve when satisfied**

❌ **DON'T:**
- Don't be overly critical without suggestions
- Don't approve without actually reviewing
- Don't let reviews stall (respond within 2-3 days)

---

## 7. Security & Privacy

### 7.1 PHI Protection

✅ **DO:**
- **Never commit PHI files**
  - Already in `.gitignore`: `*_PHI.xlsx`, `*.parquet`

- **Use PHI file skipping**
  ```bash
  movr setup  # Automatically skips *_PHI.xlsx files
  ```

- **Remove PHI before sharing**
  ```python
  # Export without PHI columns
  public_df = results_df.drop(columns=['ZIP_CODE', 'SSN'])
  public_df.to_excel("public_report.xlsx")
  ```

- **Document PHI usage**
  ```python
  # Audit log when PHI is accessed
  logger.info("Loaded PHI data for geographic analysis", extra={
      'user': current_user,
      'justification': 'IRB-approved geographic study'
  })
  ```

❌ **DON'T:**
- Don't email data files (use secure transfer)
- Don't store PHI in cloud without encryption
- Don't print PHI to console/logs
- Don't create unnecessary copies of PHI data

### 7.2 Access Control

✅ **DO:**
- **Keep source data secure**
  ```bash
  # Restrict file permissions
  chmod 600 source-movr-data/*.xlsx
  ```

- **Use environment variables for secrets**
  ```python
  # .env file (gitignored)
  API_KEY=secret_key_here

  # In code
  import os
  api_key = os.getenv('API_KEY')
  ```

- **Document access requirements**

❌ **DON'T:**
- Don't hardcode passwords/keys
- Don't share credentials
- Don't commit `.env` files

---

## 8. Performance

### 8.1 Data Operations

✅ **DO:**
- **Use vectorized operations**
  ```python
  # Good: Vectorized
  df['AGE_YEARS'] = (pd.to_datetime('today') - df['BIRTH_DATE']).dt.days / 365.25

  # Bad: Row-by-row
  for idx, row in df.iterrows():
      df.at[idx, 'AGE_YEARS'] = calculate_age(row['BIRTH_DATE'])
  ```

- **Use appropriate data types**
  ```python
  # Reduce memory usage
  df['FACPATID'] = df['FACPATID'].astype('category')
  df['AGE'] = df['AGE'].astype('int8')  # If age < 128
  ```

- **Filter early in pipeline**
  ```python
  # Good: Filter first
  dmd = df[df['DISEASE'] == 'DMD']
  result = dmd.groupby('AGE').size()

  # Bad: Filter after expensive operation
  grouped = df.groupby('AGE').size()
  result = grouped[grouped.index.isin(dmd['AGE'])]
  ```

- **Use Parquet for storage**
  ```python
  # Much faster than Excel/CSV
  df.to_parquet("data.parquet")
  df = pd.read_parquet("data.parquet")
  ```

❌ **DON'T:**
- Don't use `.iterrows()` or `.apply()` when vectorization is possible
- Don't load entire dataset if you only need a subset
- Don't perform unnecessary operations
- Don't chain many small operations (combine when possible)

### 8.2 Profiling

✅ **DO:**
- **Profile before optimizing**
  ```python
  import cProfile
  cProfile.run('my_analysis()', 'profile_stats')
  ```

- **Measure memory usage**
  ```python
  df.memory_usage(deep=True).sum() / 1024**2  # MB
  ```

- **Benchmark critical operations**
  ```python
  import timeit
  time = timeit.timeit(lambda: my_function(), number=100)
  print(f"Average time: {time/100:.4f} seconds")
  ```

❌ **DON'T:**
- Don't optimize prematurely
- Don't guess at bottlenecks (measure them)

---

## Quick Reference Checklist

### Before Committing Code

- [ ] Code follows style guidelines (black, isort, flake8)
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] Commit message is descriptive
- [ ] No debugging code left in
- [ ] No PHI or sensitive data included

### Before Starting Analysis

- [ ] Data converted to Parquet (`movr convert`)
- [ ] Data validated (`movr validate`)
- [ ] Analysis plan documented
- [ ] Random seeds set
- [ ] Output directory created

### Before Sharing Results

- [ ] Results reproducible
- [ ] PHI removed from exports
- [ ] Sample sizes reported
- [ ] Methods documented
- [ ] Code available for review
- [ ] Limitations acknowledged

---

## Related Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md) - System design
- [DATA_WRANGLING_RULES.md](DATA_WRANGLING_RULES.md) - Data processing rules
- [FEATURES.md](FEATURES.md) - Feature roadmap

---

**Questions?** Open a GitHub Discussion or Issue.

**Last Updated**: 2025-11-20
**Created By**: Andre Daniel Paredes
**Maintained By**: Andre Daniel Paredes
