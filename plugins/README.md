# Custom Plugins

This directory is for custom data wrangling plugins.

## Writing a Plugin

Create a Python file with your custom transformation functions:

```python
# plugins/my_transform.py
import pandas as pd
from movr.wrangling.plugins import register_plugin

@register_plugin("my_custom_transform")
def my_transform(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Your custom transformation logic.

    Args:
        df: Input DataFrame
        **kwargs: Additional arguments from YAML config

    Returns:
        Transformed DataFrame
    """
    # Your logic here
    df["NEW_FIELD"] = df["OLD_FIELD"].apply(some_function)
    return df
```

## Using a Plugin

Reference the plugin in `config/wrangling_rules.yaml`:

```yaml
rules:
  - name: "apply_my_transform"
    tables: ["demographics_maindata"]
    action: "plugin"
    plugin: "plugins.my_transform.my_custom_transform"
    # Additional kwargs are passed to your function
    custom_param: "value"
```

## Best Practices

1. **Always return a DataFrame** - Even if unchanged
2. **Handle missing columns gracefully** - Check if columns exist
3. **Document your functions** - Clear docstrings
4. **Log operations** - Use `logger.info()` for important steps
5. **Avoid side effects** - Don't modify global state
6. **Test with sample data** - Validate before full dataset

## Examples

See `example_transform.py` for working examples.
