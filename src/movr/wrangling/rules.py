"""
YAML rule interpreter for data wrangling.

Loads and interprets transformation rules from YAML files.
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger


class RuleInterpreter:
    """Interpret YAML-based wrangling rules."""

    def __init__(self, rules_file: Path):
        """
        Initialize rule interpreter.

        Args:
            rules_file: Path to YAML rules file
        """
        self.rules_file = Path(rules_file)
        self.rules: List[Dict[str, Any]] = []

        if self.rules_file.exists():
            self._load_rules()
        else:
            logger.warning(f"Rules file not found: {rules_file}, using empty rules")

    def _load_rules(self):
        """Load rules from YAML file."""
        with open(self.rules_file, 'r') as f:
            config = yaml.safe_load(f)

        if config and 'rules' in config:
            self.rules = config['rules']
            logger.info(f"Loaded {len(self.rules)} wrangling rules")
        else:
            logger.warning(f"No rules found in {self.rules_file}")

    def get_rules(self) -> List[Dict[str, Any]]:
        """Get all rules."""
        return self.rules

    def get_rule_by_name(self, name: str) -> Dict[str, Any]:
        """Get a specific rule by name."""
        for rule in self.rules:
            if rule.get('name') == name:
                return rule

        raise ValueError(f"Rule not found: {name}")
