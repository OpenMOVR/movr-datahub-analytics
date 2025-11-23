import importlib.util
import sys
from pathlib import Path


def _fake_tables():
    import pandas as pd
    demographics = pd.DataFrame({
        'FACPATID': [1, 2],
        'dstype': ['DMD', 'SMA'],
        'usndr': [False, False],
        'dob': ['2000-01-01', '2010-01-01']
    })
    diagnosis = pd.DataFrame({'FACPATID': [1, 2]})
    encounter = pd.DataFrame({'FACPATID': [1, 2]})
    return {
        'demographics_maindata': demographics,
        'diagnosis_maindata': diagnosis,
        'encounter_maindata': encounter,
    }


# Load the module by path
script_path = Path(__file__).parents[2] / 'scripts' / 'exploratory_interpreter.py'
spec = importlib.util.spec_from_file_location('exploratory_interpreter', script_path)
ei = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ei)


def test_create_cohorts_programmatic(monkeypatch):
    # Monkeypatch data loader used by the interpreter
    monkeypatch.setattr(ei, 'load_data', lambda verbose=False: _fake_tables())

    # init env
    tables, cohorts = ei._init_env(verbose=False)

    # create a single cohort
    name = ei.create_cohort(cohorts, disease='DMD', registry=False, name=None, force=True)
    assert name == 'exploratory_dmd_datahub'
    assert 'exploratory_dmd_datahub' in cohorts.list_cohorts()

    # create multiple cohorts
    created = ei.create_cohorts(cohorts, ['DMD', 'SMA'], registry=False, force=True)
    assert 'exploratory_dmd_datahub' in created
    assert 'exploratory_sma_datahub' in created

    # ensure summary works
    s = ei.show_summary(cohorts, 'exploratory_sma_datahub')
    assert s['n_patients'] >= 1
