def test_interactive_03_helpers_exposed():
    import importlib.util
    from pathlib import Path

    script_path = Path(__file__).resolve().parents[1] / 'scripts' / 'interactive_03_exploratory.py'
    spec = importlib.util.spec_from_file_location('interactive_03_exploratory', str(script_path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    assert hasattr(m, 'cell_1_load_env')
    assert hasattr(m, 'cell_2_create_cohorts')
    assert hasattr(m, 'cell_3_compare_cohorts')
    assert hasattr(m, 'run_all')
    assert hasattr(m, 'start_repl')
    assert hasattr(m, 'main')
