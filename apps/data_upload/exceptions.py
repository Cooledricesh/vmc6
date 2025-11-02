"""
Custom exceptions for data upload functionality.

These exceptions are raised during file parsing and validation to provide
clear error messages to users through Django Admin.
"""


class ValidationError(Exception):
    """Base exception for data validation errors."""
    pass


class FileFormatError(ValidationError):
    """Raised when file format is invalid (wrong extension, corrupted file)."""
    pass


class FileSizeError(ValidationError):
    """Raised when file size exceeds maximum allowed size."""
    pass


class MissingColumnError(ValidationError):
    """Raised when required columns are missing from the file."""
    pass


class DataTypeError(ValidationError):
    """Raised when data type validation fails."""
    pass


class ValueRangeError(ValidationError):
    """Raised when value is out of acceptable range."""
    pass


class DuplicateDataError(ValidationError):
    """Raised when duplicate records are found."""
    pass
