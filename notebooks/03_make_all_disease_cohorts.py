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
# ## 1) Import the module (robust to whether `scripts/` is a package or not)

# %%
# Attempt to import the helper module in a way that always works inside VS Code notebooks
try:
    # If `scripts` is a package on your PYTHONPATH this will be easiest
    from scripts.make_all_disease_cohorts import create_all_disease_cohorts, _read_diseases_from_config
    print('Imported from scripts package')
except Exception:
    # Fallback: search up the directory tree for scripts/<module>.py and load by path
    import importlib.util
    from pathlib import Path

    def _find_script(name='make_all_disease_cohorts.py'):
        p = Path.cwd().resolve()
        for parent in [p] + list(p.parents):
            candidate = parent / 'scripts' / name
            if candidate.exists():
                return candidate
        raise FileNotFoundError(f"Script not found: {name} -- searched from {p}")

    script_path = _find_script('make_all_disease_cohorts.py')
    spec = importlib.util.spec_from_file_location('make_all_disease_cohorts', str(script_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    create_all_disease_cohorts = module.create_all_disease_cohorts
    _read_diseases_from_config = module._read_diseases_from_config
    print('Loaded module from', script_path)

# %% [markdown]
# ## 2) Dry-run: inspect which disease codes will be created (no dataset load)

# %%
# _read_diseases_from_config reads `config/cohort_definitions.yaml` and returns the unique disease codes.
from pathlib import Path

# search upward for the config file so this works when notebook CWD is /notebooks
def _find_config(name='cohort_definitions.yaml'):
    p = Path.cwd().resolve()
    for parent in [p] + list(p.parents):
        candidate = parent / 'config' / name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f'Config not found: {name} -- searched from {p}')

cfg_path = _find_config('cohort_definitions.yaml')
print('Config path:', cfg_path)
diseases = _read_diseases_from_config(cfg_path)
print('Discovered disease codes:', diseases)

# %% [markdown]
# ## 3) Full run — create all disease exploratory cohorts (in-memory)
#
# Run the cell below to load tables and create the cohorts. This is the operation that replicates the script's `--run` behavior. If you'd prefer not to load data now, skip this cell and use the dry-run cell above.

# %%
# WARNING: this will load the dataset (Parquet) into memory — it may take a while depending on your environment.
# If you want a quiet create, pass verbose=False or set force=False to avoid overwriting named cohorts.

# Run the creation flow (force=True will overwrite in-memory names; registry=False -> DataHub)
tables, cohorts, created = create_all_disease_cohorts(force=True, registry=False, verbose=True)

print('\nCreated cohorts:')
for c in created:
    print('-', c)

# %% [markdown]
# ## 4) Inspect created cohorts (examples)
# After running the creation step the `cohorts` variable contains a `CohortManager` instance with the created exploratory cohorts. You can use its methods to explore cohort data, prepare summaries, or export cohorts.

# %%
# example: list cohorts and print concise summaries for created cohorts
print('All cohorts available (sample):', cohorts.list_cohorts()[:30])
for name in created:
    try:
        print('---', name)
        print(cohorts.get_cohort_summary(name))
    except Exception as e:
        print('Could not get summary for', name, '-', e)

# print all available cohorts
print('\nAll available cohorts:')
cohorts.list_cohorts()
