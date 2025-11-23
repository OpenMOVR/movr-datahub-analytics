def test_make_all_disease_cohorts_import():
    import importlib.util
    from pathlib import Path

    script_path = Path(__file__).resolve().parents[1] / 'scripts' / 'make_all_disease_cohorts.py'
    spec = importlib.util.spec_from_file_location('make_all_disease_cohorts', str(script_path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    assert hasattr(m, 'create_all_disease_cohorts')
    assert hasattr(m, '_read_diseases_from_config')
    assert hasattr(m, 'main')
