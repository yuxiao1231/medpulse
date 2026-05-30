"""Core exceptions."""


class MedPulseError(Exception):
    """Base application exception."""


class ValidationError(MedPulseError):
    """Raised when input validation fails."""


class FeatureNotReadyError(MedPulseError):
    """Raised for intentionally deferred features."""

