"""Custom exception classes for MOVR."""


class MOVRError(Exception):
    """Base exception for MOVR package."""
    pass


class DataValidationError(MOVRError):
    """Raised when data validation fails."""
    pass


class ConfigurationError(MOVRError):
    """Raised when configuration is invalid."""
    pass


class EnrollmentError(MOVRError):
    """Raised when enrollment validation fails."""
    pass


class CohortError(MOVRError):
    """Raised for cohort-related errors."""
    pass
