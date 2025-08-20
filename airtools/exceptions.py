"""
Custom exception classes for airtools.
Defines base and specific exceptions for error handling.
"""

from typing import Any


class BaseException(Exception):
    """
    Base exception class for airtools errors.
    Accepts an optional message and additional arguments.
    """

    def __init__(self, message: str = "", *args: Any) -> None:
        super().__init__(message, *args)


class DownloadError(BaseException):
    """
    Raised when a download operation fails.
    """

    pass


class DataParsingError(BaseException):
    """
    Raised when data parsing fails.
    """
