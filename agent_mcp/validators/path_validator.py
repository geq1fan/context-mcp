"""Path security validator to prevent directory traversal attacks.

Uses Path.resolve() to normalize paths and verify they are within project root.
"""
from pathlib import Path
from typing import Union


class PathSecurityError(Exception):
    """Raised when a path is outside the allowed project root."""

    def __init__(self, requested_path: str, root_path: Path):
        self.requested_path = requested_path
        self.root_path = root_path
        super().__init__(
            f"PATH_SECURITY_ERROR: Path '{requested_path}' is outside project root '{root_path}'"
        )


class PathValidator:
    """Validates that paths are within the configured project root.

    Prevents directory traversal attacks using Path.resolve() to normalize paths.
    """

    def __init__(self, root_path: Path):
        """Initialize validator with project root.

        Args:
            root_path: Absolute path to project root directory
        """
        self.root = root_path.resolve()

    def validate(self, path: Union[str, Path]) -> Path:
        """Validate that path is within project root.

        Args:
            path: Relative or absolute path to validate

        Returns:
            Absolute resolved Path object

        Raises:
            PathSecurityError: If path is outside project root
        """
        # Convert to Path and resolve to absolute path
        if isinstance(path, str):
            path = Path(path)

        # Handle relative paths from root
        if not path.is_absolute():
            target = (self.root / path).resolve()
        else:
            target = path.resolve()

        # Check if target is within root
        # Use is_relative_to() for Python 3.9+
        try:
            target.relative_to(self.root)
        except ValueError:
            raise PathSecurityError(str(path), self.root)

        return target

    def validate_multiple(self, paths: list[Union[str, Path]]) -> list[Path]:
        """Validate multiple paths at once.

        Args:
            paths: List of paths to validate

        Returns:
            List of validated absolute Path objects

        Raises:
            PathSecurityError: If any path is outside project root
        """
        return [self.validate(p) for p in paths]
