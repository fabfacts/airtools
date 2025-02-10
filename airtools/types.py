import pathlib
from typing import TypeVar

PathLike = TypeVar("PathLike", str, pathlib.Path, None)


class Url(str):
    """
    Type URL, checks http/https present at the beginning of a string
    """

    def __new__(cls, *value):
        if value:
            v0 = value[0]
            if not isinstance(v0, str):
                raise TypeError(f'Unexpected type for URL: "{type(v0)}"')
            if not (v0.startswith("http://") or v0.startswith("https://")):
                raise ValueError(
                    f'Passed string value "{v0}" is not an "http*://" URL'
                )
        # else allow None to be passed. This allows an "empty" URL instance, e.g. `URL()`
        # `URL()` evaluates False

        return str.__new__(cls, *value)
