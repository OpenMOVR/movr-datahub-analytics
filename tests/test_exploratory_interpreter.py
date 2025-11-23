def test_explorer_helpers_exposed():
    import importlib.util
    from pathlib import Path

    script_path = Path(__file__).resolve().parents[1] / 'scripts' / 'exploratory_interpreter.py'
    spec = importlib.util.spec_from_file_location('exploratory_interpreter', str(script_path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    assert hasattr(m, '_init_env')
    assert hasattr(m, 'create_cohort')
    assert hasattr(m, 'create_cohorts')
    assert hasattr(m, 'list_cohorts')
    assert hasattr(m, 'show_summary')
    assert hasattr(m, 'compare_cohorts')
    assert hasattr(m, 'run_notebook_flow')
    assert hasattr(m, 'main')
