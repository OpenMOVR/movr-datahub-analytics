import pandas as pd
from movr.analytics.descriptive import DescriptiveAnalyzer


def make_demo_table():
    return pd.DataFrame({
        'FACPATID': ['P1', 'P2', 'P3', 'P4'],
        'GENDER': ['Male', 'Female', 'Female', 'Male'],
        'dob': ['2010-01-01', '1980-06-15', None, '2005-03-20'],
        'DISEASE': ['DMD', 'DMD', 'BMD', 'ALS'],
        'REGISTRY': ['USNDR', None, 'MOVR', 'USNDR']
    })


def test_descriptive_resolves_columns_and_age(tmp_path):
    # cohort contains the patient ids
    cohort = pd.DataFrame({'FACPATID': ['P1', 'P2', 'P3', 'P4']})

    demo = make_demo_table()
    tables = {'demographics_maindata': demo}

    analyzer = DescriptiveAnalyzer(cohort=cohort, tables=tables)
    result = analyzer.run_analysis()

    # basic expectations
    assert result.summary['n_patients'] == 4
    # gender mapping should be resolved to GENDER -> counts
    assert 'gender_distribution' in result.summary
    assert result.summary['gender_counts']['Male'] == 2

    # age_stats should exist and be computed (one missing DOB)
    assert 'age_stats' in result.summary

    # disease distribution resolved from DISEASE
    assert 'disease_distribution' in result.summary
    assert result.summary['disease_distribution']['DMD'] == 2

    # registry resolved from REGISTRY
    assert 'usndr_distribution' in result.summary

    # columns used should show resolved keys
    cols = result.metadata.get('columns_used', {})
    assert cols.get('gender') in ('GENDER', 'gender')
    assert cols.get('disease') in ('DISEASE', 'dstype')
    assert cols.get('registry') in ('REGISTRY', 'usndr')


def test_descriptive_uses_cohort_manager_prepared(tmp_path):
    # Create demo tables and cohort manager
    from movr.cohorts.manager import CohortManager

    demo = make_demo_table()
    tables = {'demographics_maindata': demo}

    # create cohort manager and a base cohort (we'll create cohort manually)
    cm = CohortManager(tables)
    cm._cohorts['base'] = pd.DataFrame({'FACPATID': ['P1', 'P2', 'P3', 'P4']})

    # analyzer should use CohortManager.get_cohort_data
    analyzer = DescriptiveAnalyzer(cohort=None, tables=tables, cohort_manager=cm, cohort_name='base')
    result = analyzer.run_analysis()

    assert result.summary['n_patients'] == 4
    # columns_used should reflect resolved names
    cols = result.metadata.get('columns_used', {})
    assert cols.get('gender') in ('GENDER', 'gender')
