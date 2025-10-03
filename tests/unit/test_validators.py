"""Unit tests for path validator."""
import pytest
from pathlib import Path
from agent_mcp.validators.path_validator import PathValidator, PathSecurityError


class TestPathValidator:
    """Unit tests for PathValidator class."""

    def test_validate_relative_path_within_root(self, tmp_path):
        """Test validating relative path within root."""
        validator = PathValidator(tmp_path)

        # Create subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        # Validate relative path
        result = validator.validate("subdir")
        assert result == subdir
        assert result.is_absolute()

    def test_validate_absolute_path_within_root(self, tmp_path):
        """Test validating absolute path within root."""
        validator = PathValidator(tmp_path)

        # Create subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        # Validate absolute path
        result = validator.validate(subdir)
        assert result == subdir

    def test_validate_current_directory(self, tmp_path):
        """Test validating current directory (.)."""
        validator = PathValidator(tmp_path)

        result = validator.validate(".")
        assert result == tmp_path

    def test_reject_path_outside_root(self, tmp_path):
        """Test rejecting path outside root."""
        validator = PathValidator(tmp_path)

        # Try to access parent directory
        with pytest.raises(PathSecurityError) as exc_info:
            validator.validate("..")

        error = exc_info.value
        assert error.root_path == tmp_path

    def test_reject_absolute_path_outside_root(self, tmp_path):
        """Test rejecting absolute path outside root."""
        validator = PathValidator(tmp_path)

        # Try to access /etc (definitely outside tmp_path)
        with pytest.raises(PathSecurityError):
            validator.validate("/etc/passwd")

    def test_reject_directory_traversal_attack(self, tmp_path):
        """Test rejecting directory traversal attacks."""
        validator = PathValidator(tmp_path)

        # Create nested directory
        nested = tmp_path / "a" / "b" / "c"
        nested.mkdir(parents=True)

        # Try to escape using ../../../
        with pytest.raises(PathSecurityError):
            validator.validate("a/b/c/../../../..")

    def test_resolve_symlinks(self, tmp_path):
        """Test that symlinks are resolved properly."""
        validator = PathValidator(tmp_path)

        # Create target inside root
        target = tmp_path / "target"
        target.mkdir()

        # Create symlink inside root pointing to target
        link = tmp_path / "link"
        try:
            link.symlink_to(target)
        except OSError:
            pytest.skip("Symlinks not supported on this system")

        # Should validate successfully
        result = validator.validate("link")
        assert result == target

    def test_validate_multiple_paths(self, tmp_path):
        """Test validating multiple paths at once."""
        validator = PathValidator(tmp_path)

        # Create multiple subdirectories
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        # Validate multiple
        results = validator.validate_multiple(["dir1", "dir2", "."])
        assert len(results) == 3
        assert results[0] == dir1
        assert results[1] == dir2
        assert results[2] == tmp_path

    def test_validate_multiple_with_invalid_path(self, tmp_path):
        """Test that validate_multiple fails if any path is invalid."""
        validator = PathValidator(tmp_path)

        # Mix valid and invalid paths
        with pytest.raises(PathSecurityError):
            validator.validate_multiple([".", "..", "subdir"])
