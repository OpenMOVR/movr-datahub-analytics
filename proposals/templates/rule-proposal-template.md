# Data Wrangling Rule Proposal: [Rule Name]

- **Author**: [Your Name]
- **Date**: YYYY-MM-DD
- **Category**: [Deduplication | Type Conversion | Validation | Normalization | Business Rule]
- **Priority**: [High | Medium | Low]
- **Status**: Proposed
- **Rule ID**: [Will be assigned after acceptance, e.g., DT-010, VN-009]

---

## Summary

One paragraph describing the rule. What does it do and why is it needed?

---

## Motivation

### Problem Statement
What data quality issue does this rule address?

### Current State
How is this problem currently manifesting in the data?

### Examples of the Problem
```
# Real examples of bad data this rule would fix
FACPATID | FIELD_NAME | ISSUE
P001     | 01/15/2025 | Inconsistent date format
P002     | NULL       | Non-standard missing value
```

### Impact
- How many records are affected?
- What analyses does this impact?
- Is this a blocker for any research?

---

## Rule Specification

### Scope

**Tables Affected**:
- `demographics_maindata`
- `encounter_maindata`
- Other tables...

**Fields Affected**:
- `FIELD_NAME1`
- `FIELD_NAME2`

**When to Apply**:
- During initial data load
- After specific transformations
- Always / Conditionally

### Input Requirements

What conditions must be true before this rule can be applied?
- Required fields must exist
- Data types must be X
- Dependencies on other rules

### Rule Logic

#### Step-by-Step Logic
1. **Step 1**: Check if field exists
2. **Step 2**: Validate current values
3. **Step 3**: Apply transformation
4. **Step 4**: Validate output

#### Pseudocode
```python
if condition:
    # Apply transformation
    df['FIELD'] = df['FIELD'].apply(transformation_function)
else:
    # Handle edge case
    pass
```

#### Formal Specification
Precise, unambiguous description of the rule logic.

### Output

**Transformed Data**:
```
# Example of output after rule application
FACPATID | FIELD_NAME | RESULT
P001     | 2025-01-15 | Standardized date format
P002     | NaN        | Standardized missing value
```

**Metadata Generated**:
- Audit log entries
- Validation flags
- Statistics (e.g., "100 records transformed")

### Edge Cases

| Edge Case | Handling |
|-----------|----------|
| Null/missing values | Skip or flag warning |
| Unexpected data type | Raise error (strict) / Log warning (permissive) |
| Out-of-range values | Cap to min/max or flag |
| Conflicting data | Apply precedence rule |

### Strictness Mode Behavior

**Strict Mode**:
- Raise error if validation fails
- Stop processing

**Permissive Mode**:
- Log warning
- Continue with best-effort transformation
- Flag records for review

**Interactive Mode**:
- Prompt user for decision
- Remember choice for similar cases

---

## Implementation Approach

### Option 1: YAML Configuration

If rule can be implemented with existing actions:

```yaml
# config/wrangling_rules.yaml
rules:
  - name: "your_rule_name"
    tables: ["demographics_maindata"]
    action: "existing_action_type"
    parameters:
      field: "FIELD_NAME"
      from_format: "%m/%d/%Y"
      to_format: "%Y-%m-%d"
```

### Option 2: Custom Plugin

If rule requires custom logic:

```python
# plugins/custom_rules.py
from movr.wrangling.plugins import register_plugin
import pandas as pd
from typing import Dict, Any

@register_plugin("your_rule_name")
def your_rule(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Apply your custom wrangling rule.

    Args:
        df: Input DataFrame
        **kwargs: Additional parameters from YAML config

    Returns:
        Transformed DataFrame

    Raises:
        ValueError: If validation fails in strict mode
    """
    # Validation
    required_fields = ['FIELD_NAME']
    missing = [f for f in required_fields if f not in df.columns]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    # Transformation logic
    df = df.copy()
    df['FIELD_NAME'] = df['FIELD_NAME'].apply(transformation_function)

    # Validation of output
    invalid = df[df['FIELD_NAME'].isnull()]
    if len(invalid) > 0:
        # Handle based on strictness mode
        pass

    return df

def transformation_function(value):
    """Helper function for transformation."""
    # Implementation
    return transformed_value
```

**YAML Configuration for Plugin**:
```yaml
rules:
  - name: "apply_custom_rule"
    tables: ["demographics_maindata"]
    action: "plugin"
    plugin: "plugins.custom_rules.your_rule_name"
    parameters:
      param1: value1
```

### Dependencies on Other Rules

**Must run after**:
- Rule ID: Rule Name (reason)

**Must run before**:
- Rule ID: Rule Name (reason)

**Conflicts with**:
- Rule ID: Rule Name (resolution strategy)

---

## Examples

### Example 1: Successful Transformation

**Input Data**:
```python
df = pd.DataFrame({
    'FACPATID': ['P001', 'P002', 'P003'],
    'FIELD_NAME': ['01/15/2025', '02/20/2025', '03/30/2025']
})
```

**Applying Rule**:
```python
from movr.wrangling import WranglingPipeline

pipeline = WranglingPipeline(rules_file="config/wrangling_rules.yaml")
result = pipeline.execute({'demographics': df})
```

**Expected Output**:
```python
   FACPATID  FIELD_NAME
0      P001  2025-01-15
1      P002  2025-02-20
2      P003  2025-03-30
```

### Example 2: Handling Invalid Data

**Input Data**:
```python
df = pd.DataFrame({
    'FACPATID': ['P001', 'P002', 'P003'],
    'FIELD_NAME': ['01/15/2025', 'INVALID', '03/30/2025']
})
```

**Strict Mode**:
```python
# Raises ValueError
ValueError: Invalid date format in row 1: 'INVALID'
```

**Permissive Mode**:
```python
# Output with NaN for invalid value
   FACPATID  FIELD_NAME
0      P001  2025-01-15
1      P002         NaN  # Flagged in audit log
2      P003  2025-03-30

# Audit log entry:
# WARNING: Invalid date format in demographics_maindata row 1: 'INVALID'
```

### Example 3: Edge Case Handling

**Input Data**:
```python
df = pd.DataFrame({
    'FACPATID': ['P001', 'P002', 'P003'],
    'FIELD_NAME': ['01/15/2025', None, '']
})
```

**Output**:
```python
   FACPATID  FIELD_NAME
0      P001  2025-01-15
1      P002         NaN  # Null preserved as NaN
2      P003         NaN  # Empty string converted to NaN
```

---

## Testing Strategy

### Unit Tests

```python
import pytest
import pandas as pd
from plugins.custom_rules import your_rule

def test_valid_transformation():
    """Test rule on valid data."""
    df = pd.DataFrame({
        'FIELD_NAME': ['value1', 'value2']
    })
    result = your_rule(df)
    assert result['FIELD_NAME'].tolist() == ['expected1', 'expected2']

def test_missing_field():
    """Test rule raises error when required field missing."""
    df = pd.DataFrame({'OTHER_FIELD': [1, 2]})
    with pytest.raises(ValueError):
        your_rule(df)

def test_null_handling():
    """Test rule handles null values correctly."""
    df = pd.DataFrame({
        'FIELD_NAME': ['value1', None, 'value3']
    })
    result = your_rule(df)
    assert pd.isnull(result.loc[1, 'FIELD_NAME'])

def test_edge_case():
    """Test specific edge case."""
    # Test implementation
    pass
```

### Integration Tests

Test rule in combination with other rules in the pipeline.

### Manual Testing Checklist

- [ ] Run on sample demographics data
- [ ] Run on full dataset (if available)
- [ ] Check audit logs for warnings
- [ ] Verify output data quality
- [ ] Test in strict mode
- [ ] Test in permissive mode

---

## Documentation Requirements

### User Documentation
- [ ] Add to DATA_WRANGLING_RULES.md with full specification
- [ ] Add to DATA_WRANGLING_TRACKER.md with status
- [ ] Update GETTING_STARTED.md if user-facing impact

### Developer Documentation
- [ ] Inline code comments
- [ ] Docstrings for functions
- [ ] Update plugin development guide

### Examples
- [ ] Add example to documentation
- [ ] Include in example notebook if relevant

---

## Performance Considerations

**Expected Performance**:
- Time complexity: O(n) / O(n log n) / O(n²)
- Memory usage: Small / Moderate / Large
- Estimated time for 10,000 rows: X seconds

**Optimization Opportunities**:
- Vectorized operations where possible
- Batch processing for large datasets
- Caching strategies

**Benchmarks** (if available):
```
Dataset size: 10,000 rows
Execution time: 0.5 seconds
Memory usage: 50 MB
```

---

## Related Rules

**Similar Rules**:
- RU-001: Similar deduplication logic
- DT-003: Related date handling

**Dependent Rules**:
- This rule depends on: [Rule ID]
- These rules depend on this: [Rule ID]

**Conflicting Rules**:
- None / [Rule ID] - How to resolve

---

## Open Questions

1. **Question**: How should we handle X scenario?
   - Option A: Description
   - Option B: Description
   - Recommendation: ?

2. **Question**: Should this apply to all tables or specific ones?
   - Discussion needed

---

## Alternatives Considered

### Alternative 1: Manual Correction
**Why not**: Not scalable, error-prone

### Alternative 2: Different Algorithm
**Pros**: Simpler implementation
**Cons**: Less accurate
**Decision**: Chose current approach because...

---

## Success Criteria

How will we know this rule is working correctly?
- [ ] All test cases pass
- [ ] No unexpected errors in production
- [ ] Data quality metrics improve (specify)
- [ ] No valid data is incorrectly flagged

---

## References

- [Related GitHub Issue #123](link)
- [Data Dictionary Entry](link)
- [Clinical Domain Knowledge Source](link)
- [Similar Rule in Other System](link)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| YYYY-MM-DD | Initial proposal | Your Name |
| YYYY-MM-DD | Updated based on feedback | Your Name |

---

## Reviewers

- [ ] @domain-expert (clinical validation)
- [ ] @data-engineer (technical review)
- [ ] @team-lead (approval)

---

**Status**: Proposed

**Last Updated**: YYYY-MM-DD
