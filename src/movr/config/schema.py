"""
Configuration schema definitions using Pydantic.

Provides type-safe configuration with validation.
"""

from typing import Dict, List, Optional, Literal
from pathlib import Path
from pydantic import BaseModel, Field, validator


class DataSourceConfig(BaseModel):
    """Configuration for a data source."""

    name: str
    excel_path: str
    sheet_mappings: Dict[str, str] = Field(default_factory=dict)
    skip_sheets: List[str] = Field(default_factory=list)

    @validator('excel_path')
    def validate_path(cls, v):
        """Ensure path exists or will exist."""
        return v


class WranglingConfig(BaseModel):
    """Data wrangling configuration."""

    strictness: Literal["strict", "permissive", "interactive"] = "permissive"
    date_formats: List[str] = Field(
        default_factory=lambda: ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]
    )
    missing_values: List[str] = Field(
        default_factory=lambda: ["", "NA", "N/A", "NULL", "Unknown"]
    )
    drop_duplicates: bool = True
    drop_missing_keys: bool = False
    flag_future_dates: bool = True


class PathConfig(BaseModel):
    """File path configuration."""

    data_dir: Path = Field(default=Path("data"))
    parquet_dir: Path = Field(default=Path("data/parquet"))
    raw_dir: Path = Field(default=Path("data/raw"))
    output_dir: Path = Field(default=Path("output"))
    cache_dir: Path = Field(default=Path(".cache"))
    audit_dir: Path = Field(default=Path("data/.audit"))
    metadata_dir: Path = Field(default=Path("data/metadata"))
    data_dictionary: Path = Field(default=Path("data/metadata/data_dictionary.parquet"))

    @validator('*', pre=True)
    def convert_to_path(cls, v):
        """Convert strings to Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v

    def resolve_paths(self, base_dir: Path) -> "PathConfig":
        """
        Resolve all relative paths against a base directory.

        Args:
            base_dir: The base directory (typically the project root)

        Returns:
            New PathConfig with absolute paths
        """
        resolved = {}
        for field_name in self.__fields__:
            path = getattr(self, field_name)
            if isinstance(path, Path) and not path.is_absolute():
                resolved[field_name] = (base_dir / path).resolve()
            else:
                resolved[field_name] = path
        return PathConfig(**resolved)


class AuditConfig(BaseModel):
    """Audit trail configuration."""

    enabled: bool = True
    log_dir: Path = Field(default=Path("data/.audit"))
    track_conversions: bool = True
    track_transformations: bool = True
    track_analyses: bool = True


class MetadataConfig(BaseModel):
    """Metadata and data dictionary configuration."""

    data_dictionary_available: bool = False
    field_mappings_file: Path = Field(default=Path("config/field_mappings.yaml"))

    @validator('field_mappings_file', pre=True)
    def convert_to_path(cls, v):
        """Convert string to Path object."""
        if isinstance(v, str):
            return Path(v)
        return v


class MOVRConfig(BaseModel):
    """Main MOVR configuration."""

    data_sources: List[DataSourceConfig] = Field(default_factory=list)
    wrangling: WranglingConfig = Field(default_factory=WranglingConfig)
    paths: PathConfig = Field(default_factory=PathConfig)
    audit: AuditConfig = Field(default_factory=AuditConfig)
    metadata: MetadataConfig = Field(default_factory=MetadataConfig)

    # Optional database config (future use)
    database_url: Optional[str] = None

    class Config:
        """Pydantic config."""
        extra = "allow"  # Allow additional fields
