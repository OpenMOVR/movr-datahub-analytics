# Contributing to MOVR DataHub Analytics

**Thank you for your interest in contributing!**

This document provides guidelines for contributing to MOVR DataHub Analytics, including how to propose features, report issues, submit code, and collaborate with the team.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Types of Contributions](#types-of-contributions)
4. [Proposing Features (RFC Process)](#proposing-features-rfc-process)
5. [Reporting Issues](#reporting-issues)
6. [Contributing Code](#contributing-code)
7. [Proposing Data Wrangling Rules](#proposing-data-wrangling-rules)
8. [Documentation Contributions](#documentation-contributions)
9. [Review Process](#review-process)
10. [Community and Communication](#community-and-communication)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. All contributors are expected to:

- Be respectful and professional
- Welcome diverse perspectives
- Focus on what is best for the community
- Show empathy towards other community members

By participating, you agree to abide by these principles.

---

## Getting Started

### 1. Set Up Your Development Environment

> **First time?** See **[Development Environment Guide](docs/DEVELOPMENT_ENVIRONMENT.md)** for details on why we use venv, editable mode, and how the project is structured.

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/movr-datahub-analytics.git
cd movr-datahub-analytics

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable/development mode
pip install -e ".[dev,viz,notebooks]"

# Install pre-commit hooks
pre-commit install
```

### 2. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/your-bug-fix
```

### 3. Make Changes

- Write code following our style guidelines (see below)
- Add tests for new functionality
- Update documentation as needed

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=movr

# Run specific test file
pytest tests/test_specific.py
```

### 5. Submit Pull Request

```bash
# Commit your changes
git add .
git commit -m "Add feature: description"

# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

---

## Types of Contributions

We welcome various types of contributions:

### 🐛 Bug Reports
Found a bug? Please report it! See [Reporting Issues](#reporting-issues).

### 💡 Feature Proposals
Have an idea? Submit a feature proposal (RFC). See [Proposing Features](#proposing-features-rfc-process).

### 📝 Documentation
Improve docs, add examples, fix typos. See [Documentation Contributions](#documentation-contributions).

### 🧪 Code Contributions
Implement features, fix bugs, optimize performance. See [Contributing Code](#contributing-code).

### 🧹 Data Wrangling Rules
Propose new data cleaning rules. See [Proposing Data Wrangling Rules](#proposing-data-wrangling-rules).

### 📊 Analysis Examples
Share Jupyter notebooks with example analyses.

### 🎨 Plugins
Create custom transformation plugins for community use.

---

## Proposing Features (RFC Process)

We use an **RFC (Request for Comments)** process for significant features and changes.

### What Requires an RFC?

- New major features or modules
- Changes to existing APIs
- New data wrangling rule categories
- Architectural changes
- Breaking changes

### RFC Process

#### Step 1: Check Existing Proposals

Search [proposals/](proposals/) and [GitHub Issues](https://github.com/openmovr/movr-datahub-analytics/issues) to avoid duplicates.

#### Step 2: Create RFC Document

Create a new file in `proposals/` directory:

```
proposals/YYYY-MM-DD-feature-name.md
```

**RFC Template:**

```markdown
# RFC: [Feature Name]

- **Author**: Your Name
- **Date**: YYYY-MM-DD
- **Status**: Proposed
- **Related Issues**: #123, #456

## Summary

Brief 1-2 paragraph overview of the proposed feature.

## Motivation

Why is this feature needed? What problem does it solve?

## Detailed Design

### Overview
High-level description of how it will work.

### Implementation Details
- Technical approach
- Key components
- Data structures
- Algorithms

### API Design
```python
# Example code showing proposed API
cohorts.advanced_filter(...)
```

### Configuration Changes
```yaml
# Example configuration if applicable
```

## Examples

### Example 1: Basic Usage
```python
# Show how users will use this feature
```

### Example 2: Advanced Usage
```python
# Show advanced use case
```

## Alternatives Considered

What other approaches were considered and why were they not chosen?

## Backwards Compatibility

Will this break existing code? If so, how do we handle migration?

## Testing Strategy

How will this feature be tested?
- Unit tests
- Integration tests
- Manual testing procedures

## Documentation Requirements

What documentation needs to be created/updated?
- User guides
- API reference
- Example notebooks

## Open Questions

What aspects need further discussion?

## References

Links to related issues, discussions, papers, or external resources.
```

#### Step 3: Submit RFC

1. Create a pull request with your RFC document
2. Title PR: `[RFC] Your Feature Name`
3. Add label: `rfc`

#### Step 4: Community Discussion

- Team and community provide feedback on the PR
- Author addresses comments and updates RFC
- Discussion continues until consensus is reached

#### Step 5: Decision

RFC will be:
- **Accepted**: Moved to `proposals/accepted/`, added to [FEATURES.md](docs/FEATURES.md) as "Planned"
- **Rejected**: Moved to `proposals/rejected/` with reasoning
- **Deferred**: Moved to `proposals/deferred/` for future consideration

#### Step 6: Implementation

Once accepted:
1. RFC author or assignee implements the feature
2. Implementation PR references the RFC
3. Feature is documented and tested
4. Status updated in docs/FEATURES.md to "Completed"

---

## Reporting Issues

### Bug Reports

Use the **Bug Report** template on GitHub Issues.

**Good bug report includes:**
- **Description**: What happened vs. what you expected
- **Steps to Reproduce**: Minimal example to reproduce the bug
- **Environment**: OS, Python version, package version
- **Error Messages**: Full traceback if applicable
- **Screenshots**: If relevant (e.g., for visualization bugs)

**Example:**

```markdown
## Description
`movr convert` crashes when Excel file has empty sheet.

## Steps to Reproduce
1. Create Excel file with one empty sheet
2. Run `movr setup`
3. Run `movr convert`

## Expected Behavior
Should skip empty sheets or handle gracefully.

## Actual Behavior
Crashes with KeyError.

## Environment
- OS: Ubuntu 22.04 (WSL)
- Python: 3.10.5
- movr-datahub-analytics: 0.1.0

## Error Message
```
KeyError: 'MainData'
  File "src/movr/data/excel_converter.py", line 42
```
```

### Feature Requests

For small features, create a **Feature Request** issue.

For significant features, create an RFC (see above).

**Good feature request includes:**
- **Description**: What do you want to add?
- **Use Case**: Why is this useful?
- **Example**: How would it be used?
- **Alternatives**: Other ways to achieve this?

---

## Contributing Code

### Code Style

We follow **PEP 8** with these tools:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

**Pre-commit hooks** automatically run these checks.

### Code Guidelines

#### 1. Naming Conventions

```python
# Classes: PascalCase
class CohortManager:
    pass

# Functions/methods: snake_case
def create_base_cohort():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_AGE = 120

# Private methods: leading underscore
def _internal_helper():
    pass
```

#### 2. Type Hints

Always use type hints:

```python
from typing import List, Dict, Optional
import pandas as pd

def filter_cohort(
    df: pd.DataFrame,
    filters: Dict[str, any],
    strict: bool = False
) -> pd.DataFrame:
    """Apply filters to cohort."""
    pass
```

#### 3. Docstrings

Use **Google-style** docstrings:

```python
def create_cohort(
    tables: Dict[str, pd.DataFrame],
    filters: Optional[Dict[str, any]] = None
) -> pd.DataFrame:
    """Create a patient cohort from tables.

    Args:
        tables: Dictionary of table name to DataFrame.
        filters: Optional filtering criteria.

    Returns:
        DataFrame with FACPATID and cohort metadata.

    Raises:
        ValueError: If required tables are missing.

    Example:
        >>> tables = load_data()
        >>> cohort = create_cohort(tables, filters={"DISEASE": "DMD"})
    """
    pass
```

#### 4. Testing

- Write tests for all new features
- Aim for >80% code coverage
- Use pytest fixtures for common setup

```python
import pytest
from movr import CohortManager

@pytest.fixture
def sample_tables():
    """Fixture providing sample data."""
    return {
        "demographics": pd.DataFrame({
            "FACPATID": ["P001", "P002"],
            "AGE": [10, 15]
        })
    }

def test_create_base_cohort(sample_tables):
    """Test base cohort creation."""
    cohorts = CohortManager(sample_tables)
    base = cohorts.create_base_cohort()
    assert len(base) == 2
    assert "FACPATID" in base.columns
```

### Pull Request Guidelines

#### PR Title Format

```
<type>: <description>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes (formatting)
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance tasks
```

**Examples:**
- `feat: Add survival analysis module`
- `fix: Handle empty Excel sheets in converter`
- `docs: Update getting started guide`

#### PR Description Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Changes Made
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Documentation
- [ ] Updated relevant documentation
- [ ] Added example code
- [ ] Updated CHANGELOG.md

## Screenshots (if applicable)
![Description](url)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No breaking changes (or migration guide provided)
```

---

## Proposing Data Wrangling Rules

### When to Propose a Rule

- Found a data quality issue not covered by existing rules
- Need a domain-specific validation
- Want to add a new transformation type

### Rule Proposal Process

#### Step 1: Check Existing Rules

Review:
- [DATA_WRANGLING_RULES.md](docs/DATA_WRANGLING_RULES.md) - Full specifications
- [DATA_WRANGLING_TRACKER.md](docs/DATA_WRANGLING_TRACKER.md) - Implementation status

#### Step 2: Create Rule Proposal

Create file: `proposals/rules/YYYY-MM-DD-rule-name.md`

**Rule Proposal Template:**

```markdown
# Data Wrangling Rule Proposal: [Rule Name]

- **Author**: Your Name
- **Date**: YYYY-MM-DD
- **Category**: [Deduplication | Type Conversion | Validation | etc.]
- **Priority**: [High | Medium | Low]
- **Status**: Proposed

## Rule ID
Suggest an ID (e.g., DT-010, VN-009)

## Summary
One paragraph describing the rule.

## Motivation
Why is this rule needed? What problem does it solve?

## Rule Specification

### Input
What data does this rule apply to?

### Logic
Detailed description of the transformation/validation logic.

### Output
What is the expected output?

### Edge Cases
How should edge cases be handled?

## Implementation Approach

### YAML Configuration
```yaml
rules:
  - name: "your_rule_name"
    tables: ["table_name"]
    action: "action_type"
    parameters:
      param1: value1
```

### Plugin Implementation (if needed)
```python
@register_plugin("your_rule_name")
def your_rule(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    # Implementation
    return df
```

## Examples

### Example 1: Valid Case
Input:
```
FACPATID | FIELD1
P001     | value
```

Output:
```
FACPATID | FIELD1
P001     | transformed_value
```

### Example 2: Invalid Case
Input:
```
FACPATID | FIELD1
P002     | bad_value
```

Behavior:
- Strict mode: Raise error
- Permissive mode: Flag warning, set to NaN

## Testing Strategy
How will this rule be tested?

## Related Rules
List any related or dependent rules.

## References
Links to relevant documentation, papers, or discussions.
```

#### Step 3: Submit Proposal

1. Create PR with rule proposal
2. Title: `[Rule Proposal] Your Rule Name`
3. Add label: `rule-proposal`

#### Step 4: Review & Approval

Team reviews and either:
- **Accepts**: Added to docs/DATA_WRANGLING_TRACKER.md as "Proposed"
- **Requests Changes**: Author updates proposal
- **Rejects**: Moved to rejected proposals with reasoning

#### Step 5: Implementation

Once accepted:
1. Implement rule in code
2. Add tests
3. Update docs/DATA_WRANGLING_RULES.md
4. Update docs/DATA_WRANGLING_TRACKER.md status to "Implemented"

---

## Documentation Contributions

### Types of Documentation

1. **User Guides**: How to use features
2. **API Reference**: Function/class documentation
3. **Example Notebooks**: Jupyter notebook tutorials
4. **README Updates**: Keep README current
5. **Architecture Docs**: System design documentation

### Documentation Standards

- **Clear and Concise**: Get to the point
- **Examples**: Include code examples
- **Complete**: Cover edge cases and errors
- **Accurate**: Test all code examples
- **Consistent**: Follow existing style

### Documentation PRs

- Title: `docs: Description of change`
- Test all code examples
- Check spelling and grammar
- Ensure links work

---

## Review Process

### Review Timeline

- **Initial Response**: Within 3 business days
- **RFC Review**: 1-2 weeks for feedback period
- **Code Review**: 1 week for standard PRs
- **Bug Fixes**: Prioritized, faster review

### Review Criteria

Reviewers check:
- ✅ Code quality and style
- ✅ Test coverage
- ✅ Documentation completeness
- ✅ Backwards compatibility
- ✅ Performance impact
- ✅ Security considerations

### Addressing Review Comments

- Be open to feedback
- Ask questions if unclear
- Make requested changes
- Re-request review when done

---

## Community and Communication

### GitHub

- **Issues**: Bug reports, feature requests
- **Discussions**: Questions, ideas, general discussion
- **Pull Requests**: Code contributions

### Channels (Future)

- Slack/Discord (TBD)
- Mailing list (TBD)
- Monthly community calls (TBD)

### Response Times

- We aim to respond to issues/PRs within 3 business days
- RFCs have a 1-2 week discussion period
- Bug fixes are prioritized

---

## Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md**: All contributors listed
- **CHANGELOG.md**: Credited for specific changes
- **Release Notes**: Major contributions highlighted

---

## Questions?

- **General Questions**: Open a GitHub Discussion
- **Bug Reports**: Open a GitHub Issue
- **Feature Ideas**: Start with a Discussion or submit an RFC
- **Security Issues**: Email [security contact - TBD]

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to MOVR DataHub Analytics!**

Together, we're building better tools for neuromuscular disease research.

---

**Last Updated**: 2025-11-20
**Created By**: Andre Daniel Paredes
**Maintained By**: Andre Daniel Paredes
