"""
Example custom transformation plugin.

This demonstrates how to write a custom wrangling plugin.
"""

import pandas as pd
from movr.wrangling.plugins import register_plugin


@register_plugin("example_uppercase_column")
def uppercase_column(df: pd.DataFrame, column: str, **kwargs) -> pd.DataFrame:
    """
    Example plugin: Convert a column to uppercase.

    Args:
        df: Input DataFrame
        column: Column name to convert
        **kwargs: Additional arguments

    Returns:
        DataFrame with modified column
    """
    if column in df.columns:
        df[column] = df[column].astype(str).str.upper()

    return df


@register_plugin("example_age_groups")
def create_age_groups(df: pd.DataFrame, age_column: str = "AGE", **kwargs) -> pd.DataFrame:
    """
    Example plugin: Create age group categories.

    Args:
        df: Input DataFrame
        age_column: Name of age column
        **kwargs: Additional arguments

    Returns:
        DataFrame with new AGE_GROUP column
    """
    if age_column not in df.columns:
        return df

    bins = [0, 12, 18, 30, 45, 60, 120]
    labels = ["0-11", "12-17", "18-29", "30-44", "45-59", "60+"]

    df["AGE_GROUP"] = pd.cut(
        df[age_column],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    return df
