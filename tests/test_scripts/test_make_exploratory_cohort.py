import sys
import pandas as pd
import importlib.util
from pathlib import Path

# Load the script module directly from its file path so tests don't depend on package layout
script_path = Path(__file__).parents[2] / 'scripts' / 'make_exploratory_cohort.py'
spec = importlib.util.spec_from_file_location('make_exploratory_cohort', script_path)
mec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mec)


def _fake_tables():
    # Small in-memory tables that satisfy EnrollmentValidator
    demographics = pd.DataFrame({
        'FACPATID': [1, 2, 3],
        'dstype': ['DMD', 'DMD', 'SMA'],
        'usndr': [False, False, False],
        'gender': ['M', 'M', 'F'],
        'dob': ['2000-01-01', '2010-01-01', '2015-01-01']
    })

    diagnosis = pd.DataFrame({'FACPATID': [1, 2, 3]})
    encounter = pd.DataFrame({'FACPATID': [1, 2, 3]})

    return {
        'demographics_maindata': demographics,
        'diagnosis_maindata': diagnosis,
        'encounter_maindata': encounter,
    }


def test_batch_creates_multiple_cohorts(monkeypatch):
    # Monkeypatch load_data to use our small fake tables
    monkeypatch.setattr(mec, 'load_data', lambda verbose=False: _fake_tables())

    # Avoid reading real config files during tests
    monkeypatch.setattr(mec, 'load_cohort_definitions', lambda path: {})

    # Wrap CohortManager so we can inspect the instance created inside main()
    OriginalCM = mec.CohortManager
    holder = {}

    def CM_wrapper(tables):
        inst = OriginalCM(tables)
        holder['inst'] = inst
        return inst

    monkeypatch.setattr(mec, 'CohortManager', CM_wrapper)

    # Simulate command-line invocation for two diseases
    monkeypatch.setattr(sys, 'argv', ['scripts/make_exploratory_cohort.py', '--diseases', 'DMD,SMA', '--registry', 'False', '--force'])

    # Run
    mec.main()

    inst = holder.get('inst')
    assert inst is not None

    # Check that both expected cohorts exist
    assert 'exploratory_dmd_datahub' in inst.list_cohorts()
    assert 'exploratory_sma_datahub' in inst.list_cohorts()

    # Ensure summaries are present and non-zero
    s1 = inst.get_cohort_summary('exploratory_dmd_datahub')
    s2 = inst.get_cohort_summary('exploratory_sma_datahub')
    assert s1['n_patients'] >= 1
    assert s2['n_patients'] >= 1
