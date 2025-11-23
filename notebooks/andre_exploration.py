# ---
"""
Retrieves filtered data tables for a specific cohort.

This method returns cohort-specific filtered tables that have been processed
and filtered according to the cohort's criteria during the analysis run.

Parameters
----------
cohort : str
    The name of the cohort for which to retrieve filtered tables.
    Must be a valid cohort name from the available cohorts list.

Returns
-------
dict or object
    A collection of filtered data tables specific to the requested cohort.
    The exact structure depends on the cohort configuration and available data.

Examples
--------
>>> tables_dmd = andre.cohorts.get_filtered_tables('exploratory_dmd_datahub')
>>> # Returns filtered tables for the DMD cohort

Notes
-----
- Must call run_analysis() before using this method to ensure tables are loaded
- Use list_cohorts() to see available cohort names
- Each cohort may have different table structures and filtering criteria
"""
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
print('AndreQuick helper is ready:', getattr(andre, '__class__', None))  #######################################################################################################

# %% 
andre.run_analysis()
print('Analysis run completed. You can now inspect tables and cohorts.')
# %%  
andre.cohorts.list_cohorts()

# %% 
# - Use `cohorts.get_filtered_tables(<cohort>)` to inspect cohort-specific filtered tables.
# - Example: `tables_dmd = andre.cohorts.get_filtered_tables('dmd_datahub')` to get tables for DMD cohort.
tables_dmd = andre.cohorts.get_filtered_tables('exploratory_dmd_datahub')

# %% End