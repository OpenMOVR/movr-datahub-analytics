"""
Filter expressions for cohort building.

Provides a simple DSL for building complex filters.
"""

from typing import Any, Callable
import pandas as pd


class FilterExpression:
    """Build filter expressions for cohort filtering."""

    def __init__(self, column: str):
        """
        Initialize filter expression.

        Args:
            column: Column name to filter on
        """
        self.column = column
        self._condition: Callable = None

    def equals(self, value: Any) -> 'FilterExpression':
        """Filter where column equals value."""
        self._condition = lambda df: df[self.column] == value
        return self

    def in_list(self, values: list) -> 'FilterExpression':
        """Filter where column is in list of values."""
        self._condition = lambda df: df[self.column].isin(values)
        return self

    def between(self, min_val: Any, max_val: Any) -> 'FilterExpression':
        """Filter where column is between min and max (inclusive)."""
        self._condition = lambda df: (df[self.column] >= min_val) & (df[self.column] <= max_val)
        return self

    def greater_than(self, value: Any) -> 'FilterExpression':
        """Filter where column is greater than value."""
        self._condition = lambda df: df[self.column] > value
        return self

    def less_than(self, value: Any) -> 'FilterExpression':
        """Filter where column is less than value."""
        self._condition = lambda df: df[self.column] < value
        return self

    def contains(self, substring: str, case_sensitive: bool = False) -> 'FilterExpression':
        """Filter where column contains substring."""
        if case_sensitive:
            self._condition = lambda df: df[self.column].str.contains(substring, na=False)
        else:
            self._condition = lambda df: df[self.column].str.contains(substring, case=False, na=False)
        return self

    def apply(self, df: pd.DataFrame) -> pd.Series:
        """
        Apply filter expression to DataFrame.

        Args:
            df: DataFrame to filter

        Returns:
            Boolean Series indicating which rows match
        """
        if self._condition is None:
            raise ValueError("No filter condition defined")
        return self._condition(df)
