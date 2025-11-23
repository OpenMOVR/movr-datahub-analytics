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
# make sure project root and scripts are on sys.path when running inside /notebooks
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))
print('Paths prepared; you can import helpers from scripts/')

# %%
# Import a convenience helper from scripts for quick exploration
from scripts.quick_start_exploratory_cohorts import andrequick_CohortAnalyzer as AndreQuick
# instantiate (loads dataset/cohorts when you call run_analysis())
andre = AndreQuick()
print('AndreQuick helper is ready:', getattr(andre, '__class__', None))

# %% [markdown]
# ## Next steps
# - Call `andre.run_analysis()` to load tables, create cohorts and return (tables, cohorts, created).
# - Use `cohorts.get_filtered_tables(<cohort>)` to inspect cohort-specific filtered tables.
