"""
Custom exception classes for airtools.
Defines base and specific exceptions for error handling.
"""

from typing import Any


class BaseException(Exception):
    """
    Base exception class for airtools errors.

    Use this as a common ancestor for project-specific exceptions.
    """

    def __init__(self, message: str = "", *args: Any) -> None:
        super().__init__(message, *args)


class DownloadError(BaseException):
    """Raised when a download operation fails (HTTP errors, timeouts, etc.)."""


class DataParsingError(BaseException):
    """Raised when data parsing fails (CSV parsing, invalid formats, etc.)."""
