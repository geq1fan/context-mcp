"""Binary file detection using NULL byte detection.

Reads first 1024 bytes of a file to check for NULL bytes (\x00),
which are common in binary files but rare in text files.
"""
from pathlib import Path


class BinaryFileError(Exception):
    """Raised when attempting to read a binary file as text."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(
            f"BINARY_FILE_ERROR: Cannot read binary file '{file_path}'"
        )


def is_binary_file(file_path: Path, chunk_size: int = 1024) -> bool:
    """Detect if a file is binary by checking for NULL bytes.

    Args:
        file_path: Path to file to check
        chunk_size: Number of bytes to read for detection (default: 1024)

    Returns:
        True if file appears to be binary, False otherwise

    Note:
        This is a heuristic check. It may not be 100% accurate for all files.
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            # Check for NULL byte
            return b'\x00' in chunk
    except (IOError, OSError):
        # If we can't read the file, assume it's not binary
        # The actual file operation will fail with a proper error
        return False


def assert_text_file(file_path: Path) -> None:
    """Assert that a file is a text file (not binary).

    Args:
        file_path: Path to file to check

    Raises:
        BinaryFileError: If file appears to be binary
    """
    if is_binary_file(file_path):
        raise BinaryFileError(str(file_path))
