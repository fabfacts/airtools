from pathlib import Path
import pytest


@pytest.fixture()
def test_files_path():
    """
    Test files root dir
    """
    return Path(__file__).parent / "test_files"
