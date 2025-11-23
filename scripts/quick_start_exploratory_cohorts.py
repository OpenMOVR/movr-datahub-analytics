from make_all_disease_cohorts import create_all_disease_cohorts, _read_diseases_from_config
from pathlib import Path

class andrequick_CohortAnalyzer:   #This is my temporary custom class for quick exploratory cohort analysis
    def __init__(self):
        self.cfg_path = None
        self.diseases = None
        self.tables = None
        self.cohorts = None
        self.created = None
        
    def _find_config(self, name='cohort_definitions.yaml'):
        p = Path.cwd().resolve()
        for parent in [p] + list(p.parents):
            candidate = parent / 'config' / name
            if candidate.exists():
                return candidate
        raise FileNotFoundError(f'Config not found: {name} -- searched from {p}')
    
    def load_config(self):
        """Load configuration and discover diseases"""
        self.cfg_path = self._find_config('cohort_definitions.yaml')
        print('Config path:', self.cfg_path)
        self.diseases = _read_diseases_from_config(self.cfg_path)
        print('Discovered disease codes:', self.diseases)
        return self.diseases
    
    def create_cohorts(self, force=True, registry=False, verbose=True):
        """Create all disease cohorts"""
        if self.diseases is None:
            self.load_config()
        
        self.tables, self.cohorts, self.created = create_all_disease_cohorts(
            self.cfg_path, force=force, registry=registry, verbose=verbose
        )
        return self.tables, self.cohorts, self.created
    
    def run_analysis(self, force=True, registry=False, verbose=True):
        """Run complete analysis pipeline"""
        self.load_config()
        return self.create_cohorts(force=force, registry=registry, verbose=verbose)

# For backward compatibility when run as script
if __name__ == "__main__":
    analyzer = andrequick_CohortAnalyzer()
    analyzer.run_analysis()

