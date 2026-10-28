"""Custom domain exceptions for echochamber."""


class EchoChamberError(Exception):
    """Base exception for all echochamber operations."""


class ConfigurationError(EchoChamberError):
    """Raised when configuration validation fails."""


class DataValidationError(EchoChamberError):
    """Raised when input data schema or content is invalid."""


class MissingDataError(EchoChamberError):
    """Raised when expected data files or directories do not exist."""


class PipelineExecutionError(EchoChamberError):
    """Raised when a pipeline stage fails execution."""


class DimensionMismatchError(EchoChamberError):
    """Raised when embedding dimensions do not match expected shapes."""


class UnscorableCommunityError(EchoChamberError):
    """Raised when a community cannot be scored due to missing core metrics."""
